"""
Code 13: Phase B — ANSYS-Integrated ML Training Pipeline.

Ingests the 272 physically verified ANSYS Maxwell 2D simulation results and
trains a 3-way ensemble (MLP + GBR + XGBoost) to predict thin-film capacitance.

Key# Standard processing applied for code_13_train_ansys.py:
  - Source:   ansys_simulation_results.csv (ANSYS-derived ground truth)
  - Target:   sim_capacitance_F (FEA-derived capacitance, pF/m)
  - Features: Morgan Fingerprints (from SMILES) + Physical Properties
  - Model:    3-way Ensemble: MLP + GBR + XGBoost
  - Output:   ansys_ensemble_pipeline.pkl
"""
import pandas as pd
import numpy as np
import joblib
import os
from pathlib import Path
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.neural_network import MLPRegressor
from sklearn.ensemble import GradientBoostingRegressor, VotingRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    r2_score,
    mean_absolute_error,
    mean_squared_error,
    confusion_matrix,
    ConfusionMatrixDisplay,
)

from rdkit import Chem
from rdkit.Chem import rdMolDescriptors
from rdkit import RDLogger

RDLogger.DisableLog("rdApp.*")

try:
    from xgboost import XGBRegressor

    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    # logger not yet available at import time; use warnings module
    import warnings
    warnings.warn("XGBoost not found. Running 2-way ensemble (MLP + GBR).", ImportWarning)

import config
from codes.dataset_composition_manager import DatasetCompositionManager
from codes.cross_validation import CrossValidationByMaterialClass, MaterialClass
from reproducibility import enforce_reproducibility, DeterministicPipeline

# ── Enforce reproducibility immediately ───────────────────────────────────────
enforce_reproducibility(42)

from logger_setup import PipelineLogger  # noqa: E402

PipelineLogger.setup_logging()
logger = PipelineLogger.get_logger(__name__)

ANSYS_DATA_PATH = str(Path(__file__).parent.parent / "results/ansys_simulation_results.csv")
ANSYS_MODEL_PATH = str(Path(__file__).parent.parent / "files/ansys_ensemble_pipeline.pkl")
MORGAN_BITS = 512  # Smaller than the main pipeline (fewer training samples)


# ─── 1. SMILES → Morgan Fingerprint ──────────────────────────────────────────
def smiles_to_morgan(smi: str, n_bits: int = MORGAN_BITS) -> np.ndarray:
    """Converts a SMILES string to a Morgan fingerprint bit-vector."""
    mol = Chem.MolFromSmiles(smi)
    if mol is None:
        return np.zeros(n_bits)
    fp = rdMolDescriptors.GetMorganFingerprintAsBitVect(mol, radius=2, nBits=n_bits)
    return np.array(fp)


# ─── 2. Feature Engineering ───────────────────────────────────────────────────
def build_feature_matrix(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """
    Builds the full feature matrix from the ANSYS results DataFrame.

    Feature groups:
      - Morgan fingerprints (512 bits) from SMILES column
      - Physical properties: dielectric_constant, tg_celsius, density_g_cm3
      - Simulation conditions: thickness_nm, applied_voltage, temp_c
    """
    logger.info("      Engineering Morgan Fingerprints from SMILES (%d bits)...", MORGAN_BITS)
    fps = np.vstack([smiles_to_morgan(s) for s in df["smiles"]])
    fp_cols = [f"Morgan_{i}" for i in range(MORGAN_BITS)]
    df_fps = pd.DataFrame(fps, columns=fp_cols, index=df.index)

    physical_cols = [
        "dielectric_constant",
        "tg_celsius",
        "density_g_cm3",
        "thickness_nm",
        "applied_voltage",
        "temp_c",
    ]
    df_physical = df[physical_cols].copy()

    X = pd.concat([df_fps, df_physical], axis=1)
    feature_names = fp_cols + physical_cols
    return X, feature_names


# ─── 3. Pipeline Builders ─────────────────────────────────────────────────────
def build_preprocessor(morgan_cols: list, physical_cols: list):
    """PCA on Morgan bits only; physical cols pass through with scaling."""
    n_components = min(64, len(morgan_cols) - 1)
    return ColumnTransformer(
        transformers=[
            (
                "pca_morgan",
                PCA(n_components=n_components, random_state=config.RANDOM_SEED),
                morgan_cols,
            ),
        ],
        remainder="passthrough",  # Physical features passed through directly
    )


def build_mlp(preprocessor):
    return Pipeline(
        [
            ("preprocessor", preprocessor),
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            (
                "mlp",
                MLPRegressor(
                    hidden_layer_sizes=(128, 64, 32),
                    activation="relu",
                    solver="adam",
                    learning_rate="adaptive",
                    learning_rate_init=0.001,
                    max_iter=2000,
                    early_stopping=True,
                    validation_fraction=0.15,
                    n_iter_no_change=200,
                    alpha=0.01,
                    random_state=config.RANDOM_SEED,
                ),
            ),
        ]
    )


def build_gbr(preprocessor):
    return Pipeline(
        [
            ("preprocessor", preprocessor),
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            (
                "gbr",
                GradientBoostingRegressor(
                    n_estimators=300,
                    learning_rate=0.05,
                    max_depth=4,
                    subsample=0.8,
                    min_samples_leaf=3,
                    random_state=config.RANDOM_SEED,
                ),
            ),
        ]
    )


def build_xgb(preprocessor):
    return Pipeline(
        [
            ("preprocessor", preprocessor),
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            (
                "xgb",
                XGBRegressor(
                    n_estimators=300,
                    learning_rate=0.05,
                    max_depth=4,
                    subsample=0.8,
                    colsample_bytree=0.8,
                    reg_alpha=0.1,
                    random_state=config.RANDOM_SEED,
                    verbosity=0,
                    tree_method="hist",
                    device="cuda",
                ),
            ),
        ]
    )


# ─── 4. Metrics ───────────────────────────────────────────────────────────────
def log_metrics(label: str, y_true, y_pred) -> tuple:
    r2 = r2_score(y_true, y_pred)
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    logger.info("--- %s ---", label)
    logger.info("  R²:   %.4f", r2)
    logger.info("  MAE:  %.4f pF/m", mae)
    logger.info("  RMSE: %.4f pF/m", rmse)
    return r2, mae, rmse


# ─── 5. Plots ─────────────────────────────────────────────────────────────────
def generate_plots(y_test, y_pred_ens, y_pred_mlp, mlp_pipeline):
    """Generates parity plot, loss curve, and error distribution."""

    # Parity plot
    plt.figure(figsize=(8, 6))
    plt.scatter(
        y_test,
        y_pred_ens,
        alpha=0.75,
        color="royalblue",
        edgecolors="black",
        s=60,
        label="3-Way Ensemble",
        zorder=3,
    )
    plt.scatter(
        y_test,
        y_pred_mlp,
        alpha=0.35,
        color="darkorange",
        edgecolors="none",
        s=40,
        label="MLP only",
        zorder=2,
    )
    lims = [min(y_test.min(), y_pred_ens.min()) - 5, max(y_test.max(), y_pred_ens.max()) + 5]
    plt.plot(lims, lims, "r--", lw=2.5, label="Perfect Fit", zorder=4)
    plt.xlim(lims)
    plt.ylim(lims)
    plt.title("Phase B: ANSYS Capacitance — Ensemble vs Actual", fontsize=14, pad=15)
    plt.xlabel("Simulated Capacitance (pF/m)", fontsize=12)
    plt.ylabel("Predicted Capacitance (pF/m)", fontsize=12)
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()
    plt.savefig(str(Path(__file__).parent.parent / "graphs/ansys_predictions.png"), dpi=300)
    plt.close()

    # Loss curve
    mlp_model = mlp_pipeline.named_steps["mlp"]
    plt.figure(figsize=(8, 6))
    plt.plot(mlp_model.loss_curve_, color="crimson", lw=2, label="Training Loss")
    if hasattr(mlp_model, "validation_scores_") and mlp_model.validation_scores_:
        val_loss = [-s for s in mlp_model.validation_scores_]
        plt.plot(
            val_loss, color="steelblue", lw=1.5, linestyle="--", label="Validation Score (neg)"
        )
    plt.title("Phase B: ANSYS MLP Training Loss Curve", fontsize=14, pad=15)
    plt.xlabel("Iterations", fontsize=12)
    plt.ylabel("Loss", fontsize=12)
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()
    plt.savefig(str(Path(__file__).parent.parent / "graphs/ansys_mlp_loss.png"), dpi=300)
    plt.close()

    # Error distribution
    abs_errors = np.abs(y_test.values - y_pred_ens)
    plt.figure(figsize=(8, 6))
    plt.hist(abs_errors, bins=20, color="teal", edgecolor="black", alpha=0.75)
    plt.title("Phase B: Ensemble Absolute Error Distribution", fontsize=14, pad=15)
    plt.xlabel("Absolute Error (pF/m)", fontsize=12)
    plt.ylabel("Frequency", fontsize=12)
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()
    plt.savefig(str(Path(__file__).parent.parent / "graphs/ansys_error_dist.png"), dpi=300)
    plt.close()
    logger.info("      Plots saved: ansys_predictions.png, ansys_mlp_loss.png, ansys_error_dist.png")


def generate_confusion_matrix(y_test, y_pred_ens):
    """
    Produces a Binned Confusion Matrix for the regression output.
    Capacitance is discretised into 4 physically meaningful bands:
      Low     : < 75  pF/m
      Medium  : 75-150 pF/m
      High    : 150-300 pF/m
      Very High: >= 300 pF/m
    """
    bins = [0, 75, 150, 300, float("inf")]
    labels = ["Low\n(<75)", "Medium\n(75-150)", "High\n(150-300)", "Very High\n(>300)"]

    y_true_binned = pd.cut(y_test.values, bins=bins, labels=labels).astype(str)
    y_pred_binned = pd.cut(y_pred_ens, bins=bins, labels=labels).astype(str)

    cm = confusion_matrix(y_true_binned, y_pred_binned, labels=labels)

    fig, ax = plt.subplots(figsize=(8, 6))
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=labels)
    disp.plot(ax=ax, cmap="Blues", colorbar=True, values_format="d")
    ax.set_title(
        "Phase B: Ensemble Binned Confusion Matrix\n(Capacitance Range Bands)", fontsize=13, pad=15
    )
    ax.set_xlabel("Predicted Capacitance Band", fontsize=11)
    ax.set_ylabel("Actual Capacitance Band", fontsize=11)
    plt.tight_layout()
    plt.savefig(str(Path(__file__).parent.parent / "graphs/ansys_confusion_matrix.png"), dpi=300)
    plt.close()
    logger.info("      Confusion matrix saved: ansys_confusion_matrix.png")


# ─── 6. Main ──────────────────────────────────────────────────────────────────
def main():
    logger.info("=" * 60)
    logger.info("  Phase B — ANSYS-Integrated ML Training (code_13)")
    logger.info("=" * 60)

    logger.info("[1/7] Loading ANSYS simulation results...")
    df_raw = pd.read_csv(ANSYS_DATA_PATH)
    df = df_raw[df_raw["sim_status"] == "Success"].copy().reset_index(drop=True)
    logger.info("      Total records: %d | High-Fidelity Success: %d", len(df_raw), len(df))

    q99 = df["sim_capacitance_F"].quantile(0.99)
    df = df[df["sim_capacitance_F"] <= q99].reset_index(drop=True)
    logger.info("      After outlier trim (99th pct = %.2f): %d samples", q99, len(df))

    y = df["sim_capacitance_F"]

    logger.info("[2/7] Building feature matrix...")
    X, feature_names = build_feature_matrix(df)
    morgan_cols = [c for c in feature_names if c.startswith("Morgan_")]
    physical_cols = [c for c in feature_names if not c.startswith("Morgan_")]
    logger.info("      Feature matrix: %d samples x %d features", X.shape[0], X.shape[1])
    logger.info("      Morgan bits: %d | Physical features: %d", len(morgan_cols), len(physical_cols))

    logger.info("[3/7] Splitting Train/Test (80/20) with Stratification...")
    manager = DatasetCompositionManager()
    manager.generate_composition_report(
        df, str(Path(__file__).parent.parent / "results/dataset_composition.txt")
    )
    train_df, test_df = manager.split_by_material_class(df, test_size=0.20)
    X_train = X.loc[train_df.index]
    X_test  = X.loc[test_df.index]
    y_train = y.loc[train_df.index]
    y_test  = y.loc[test_df.index]
    logger.info("      Train: %d | Test: %d", len(X_train), len(X_test))

    logger.info("[4/7] Building MLP pipeline...")
    mlp_pipeline = build_mlp(build_preprocessor(morgan_cols, physical_cols))

    logger.info("[4/7] Building GBR pipeline...")
    gbr_pipeline = build_gbr(build_preprocessor(morgan_cols, physical_cols))

    logger.info("[5/7] Fitting MLP pipeline...")
    mlp_pipeline.fit(X_train, y_train)
    y_pred_mlp = mlp_pipeline.predict(X_test)
    mlp_metrics = log_metrics("MLP Stand-alone", y_test, y_pred_mlp)

    logger.info(
        "[6/7] Fitting 3-Way Ensemble (MLP + GBR%s...",
        " + XGBoost)" if XGBOOST_AVAILABLE else ")",
    )
    mlp2 = build_mlp(build_preprocessor(morgan_cols, physical_cols))
    gbr2 = build_gbr(build_preprocessor(morgan_cols, physical_cols))

    estimators = [("mlp", mlp2), ("gbr", gbr2)]
    weights = [0.35, 0.35]

    if XGBOOST_AVAILABLE:
        xgb2 = build_xgb(build_preprocessor(morgan_cols, physical_cols))
        estimators.append(("xgb", xgb2))
        weights.append(0.30)

    ensemble = VotingRegressor(estimators=estimators, weights=weights, n_jobs=1)
    ensemble.fit(X_train, y_train)

    logger.info("      Saving individual model checkpoints...")
    checkpoint_dir = Path(__file__).parent.parent / "results/checkpoints"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    for name, fitted_estimator in ensemble.named_estimators_.items():
        ckpt_path = checkpoint_dir / f"ansys_{name}_checkpoint.pkl"
        joblib.dump(fitted_estimator, ckpt_path)
        logger.info("        Saved %s checkpoint -> %s", name.upper(), ckpt_path)

    y_pred_ens = ensemble.predict(X_test)
    ens_metrics = log_metrics(
        "3-Way Ensemble (MLP + GBR" + (" + XGBoost)" if XGBOOST_AVAILABLE else " + GBR)"),
        y_test,
        y_pred_ens,
    )

    cv_r2 = cross_val_score(ensemble, X_train, y_train, cv=10, scoring="r2")
    logger.info("  10-Fold CV R²: %.4f ± %.4f", cv_r2.mean(), cv_r2.std())

    joblib.dump(ensemble, ANSYS_MODEL_PATH)
    logger.info("      Model saved -> %s", ANSYS_MODEL_PATH)

    logger.info("[7/7] Generating evaluation plots and cross-class validation...")
    generate_plots(y_test, y_pred_ens, y_pred_mlp, mlp_pipeline)
    generate_confusion_matrix(y_test, y_pred_ens)

    cv_metrics = CrossValidationByMaterialClass.evaluate_per_material_class(
        test_df, y_test, y_pred_ens
    )
    with open(str(Path(__file__).parent.parent / "results/cross_class_validation.txt"), "w") as f:
        f.write("CROSS-MATERIAL-CLASS VALIDATION REPORT\n")
        f.write("=" * 80 + "\n\n")
        for mat_class, metrics in cv_metrics.items():
            f.write(
                f"{mat_class:<25} {metrics['sample_count']:>10} "
                f"{metrics['r2_score']:>12.3f} {metrics['mae']:>12.3f} "
                f"{metrics['rmse']:>12.3f}\n"
            )
    logger.info("      Cross-class validation saved: cross_class_validation.txt")

    logger.info("=" * 60)
    logger.info("  Phase B COMPLETE")
    logger.info("  Training Samples:  %d", len(X_train))
    logger.info("  Test Samples:      %d", len(X_test))
    logger.info("  MLP  R²:   %.4f  |  MAE: %.2f pF/m", mlp_metrics[0], mlp_metrics[1])
    logger.info("  Ens  R²:   %.4f  |  MAE: %.2f pF/m", ens_metrics[0], ens_metrics[1])
    logger.info("  CV   R²:   %.4f ± %.4f  (10-Fold)", cv_r2.mean(), cv_r2.std())
    logger.info("  Model:     %s", ANSYS_MODEL_PATH)
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
