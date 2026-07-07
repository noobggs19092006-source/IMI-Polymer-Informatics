"""
code_18_gnn_training.py — Phase 5.2: GNN Message Passing Feature Extractor + Retraining.

Instead of binary Morgan fingerprints, this script uses a manual 2-hop Message
Passing Neural Network (MPNN) philosophy to extract rich, continuous atom-level
features from each polymer's molecular graph using RDKit. These richer features
are then used to retrain the 3-Way Ensemble for improved R².
"""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

# ── Reproducibility (must come before any sklearn/numpy calls) ────────────────
sys.path.insert(0, str(Path(__file__).resolve().parent))
from reproducibility import enforce_reproducibility

enforce_reproducibility(42)

from logger_setup import PipelineLogger  # noqa: E402

PipelineLogger.setup_logging()
logger = PipelineLogger.get_logger(__name__)

from rdkit import Chem, RDLogger  # noqa: E402
from rdkit.Chem import Descriptors, rdMolDescriptors  # noqa: E402

RDLogger.DisableLog("rdApp.*")

from sklearn.decomposition import PCA  # noqa: E402
from sklearn.ensemble import GradientBoostingRegressor, VotingRegressor  # noqa: E402
from sklearn.impute import SimpleImputer  # noqa: E402
from sklearn.model_selection import cross_val_score, train_test_split  # noqa: E402
from sklearn.neural_network import MLPRegressor  # noqa: E402
from sklearn.pipeline import Pipeline  # noqa: E402
from sklearn.preprocessing import StandardScaler  # noqa: E402
from xgboost import XGBRegressor  # noqa: E402

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

# Import hyperparameters from constants — no more magic numbers
from constants import RANDOM_SEED  # noqa: E402

# ── Paths ─────────────────────────────────────────────────────────────────────
_REPO_ROOT = Path(__file__).resolve().parent.parent
INPUT_CSV: Path = _REPO_ROOT / "results" / "ansys_simulation_results.csv"
OUTPUT_MODEL: Path = _REPO_ROOT / "files" / "ansys_gnn_pipeline.pkl"

# ── GNN Hyperparameters (named constants — no magic numbers) ──────────────────
GNN_MLP_HIDDEN: tuple[int, ...] = (128, 64, 32)
GNN_MLP_MAX_ITER: int = 2000
GNN_MLP_PATIENCE: int = 200
GNN_GBR_N_ESTIMATORS: int = 300
GNN_GBR_LR: float = 0.05
GNN_GBR_DEPTH: int = 4
GNN_GBR_SUBSAMPLE: float = 0.8
GNN_XGB_N_ESTIMATORS: int = 300
GNN_XGB_DEPTH: int = 4
GNN_XGB_LR: float = 0.05
GNN_ENSEMBLE_WEIGHTS: list[float] = [0.35, 0.35, 0.30]
GNN_TEST_SIZE: float = 0.2
GNN_CV_FOLDS: int = 5

# ── Atom features list ────────────────────────────────────────────────────────
ATOM_FEATURES = [
    "AtomicNum", "Degree", "NumHs", "Charge", "IsArom",
    "IsInRing", "Hybridization_SP", "Hybridization_SP2", "Hybridization_SP3",
]
N_ATOM_FEATS: int = len(ATOM_FEATURES)


# ── Feature extraction functions ──────────────────────────────────────────────

def atom_features(atom: Chem.rdchem.Atom) -> list[int]:
    """Return a fixed-length feature vector for a single RDKit atom."""
    hyb = atom.GetHybridization()
    return [
        atom.GetAtomicNum(),
        atom.GetDegree(),
        atom.GetTotalNumHs(),
        atom.GetFormalCharge(),
        int(atom.GetIsAromatic()),
        int(atom.IsInRing()),
        int(hyb == Chem.rdchem.HybridizationType.SP),
        int(hyb == Chem.rdchem.HybridizationType.SP2),
        int(hyb == Chem.rdchem.HybridizationType.SP3),
    ]


def mpnn_fingerprint(smi: str, max_atoms: int = 30) -> np.ndarray:
    """
    2-hop Message Passing: for each atom, aggregate its own features
    plus the mean features of its 1-hop and 2-hop neighbors.
    Output: a fixed-length vector representing the whole molecule.
    """
    mol = Chem.MolFromSmiles(smi)
    if mol is None:
        return np.zeros(N_ATOM_FEATS * 3)  # own + 1hop + 2hop aggregates

    n_atoms = mol.GetNumAtoms()
    atom_feat_matrix = np.array([atom_features(a) for a in mol.GetAtoms()], dtype=float)

    adj: dict[int, list[int]] = {i: [] for i in range(n_atoms)}
    for bond in mol.GetBonds():
        i, j = bond.GetBeginAtomIdx(), bond.GetEndAtomIdx()
        adj[i].append(j)
        adj[j].append(i)

    hop1 = np.zeros_like(atom_feat_matrix)
    for i in range(n_atoms):
        nbrs = adj[i]
        if nbrs:
            hop1[i] = atom_feat_matrix[nbrs].mean(axis=0)

    hop2 = np.zeros_like(atom_feat_matrix)
    for i in range(n_atoms):
        nbrs2: set[int] = set()
        for j in adj[i]:
            nbrs2.update(adj[j])
        nbrs2.discard(i)
        if nbrs2:
            hop2[i] = atom_feat_matrix[list(nbrs2)].mean(axis=0)

    own_global = atom_feat_matrix.mean(axis=0)
    hop1_global = hop1.mean(axis=0)
    hop2_global = hop2.mean(axis=0)

    return np.concatenate([own_global, hop1_global, hop2_global])


def rdkit_2d_descriptors(smi: str) -> np.ndarray:
    """Additional 2D molecular descriptors from RDKit for extra signal."""
    mol = Chem.MolFromSmiles(smi)
    if mol is None:
        return np.zeros(6)
    return np.array([
        Descriptors.MolWt(mol),
        Descriptors.MolLogP(mol),
        Descriptors.NumHDonors(mol),
        Descriptors.NumHAcceptors(mol),
        rdMolDescriptors.CalcNumRings(mol),
        rdMolDescriptors.CalcNumAromaticRings(mol),
    ])


def build_gnn_features(df: pd.DataFrame) -> np.ndarray:
    """Combine MPNN fingerprints, RDKit descriptors, and physical properties."""
    mpnn_feats = np.vstack([mpnn_fingerprint(s) for s in df["smiles"]])
    rdkit_feats = np.vstack([rdkit_2d_descriptors(s) for s in df["smiles"]])
    phys = df[["dielectric_constant", "tg_celsius", "density_g_cm3",
               "thickness_nm", "applied_voltage", "temp_c"]].values
    return np.hstack([mpnn_feats, rdkit_feats, phys])


def main() -> None:
    logger.info("=" * 60)
    logger.info("  Phase 5.2 -- GNN Message Passing Feature Retraining")
    logger.info("=" * 60)

    logger.info("[1/5] Loading ANSYS ground truth data from %s", INPUT_CSV)
    df = pd.read_csv(INPUT_CSV)
    df_ok = df[df["sim_status"] == "Success"].dropna(subset=["sim_capacitance_F"]).copy()
    logger.info("     -> %d verified ANSYS samples loaded.", len(df_ok))

    logger.info("[2/5] Building MPNN molecular graph features (2-hop message passing)...")
    X = build_gnn_features(df_ok)
    y = df_ok["sim_capacitance_F"].values
    logger.info("     -> Feature matrix shape: %s", X.shape)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=GNN_TEST_SIZE, random_state=RANDOM_SEED
    )

    logger.info("[3/5] Training 3-Way Ensemble on GNN features...")
    mlp = MLPRegressor(
        hidden_layer_sizes=GNN_MLP_HIDDEN,
        max_iter=GNN_MLP_MAX_ITER,
        early_stopping=True,
        n_iter_no_change=GNN_MLP_PATIENCE,
        random_state=RANDOM_SEED,
        alpha=0.01,
        learning_rate="adaptive",
    )
    gbr = GradientBoostingRegressor(
        n_estimators=GNN_GBR_N_ESTIMATORS,
        learning_rate=GNN_GBR_LR,
        max_depth=GNN_GBR_DEPTH,
        subsample=GNN_GBR_SUBSAMPLE,
        random_state=RANDOM_SEED,
    )
    xgb = XGBRegressor(
        n_estimators=GNN_XGB_N_ESTIMATORS,
        max_depth=GNN_XGB_DEPTH,
        learning_rate=GNN_XGB_LR,
        colsample_bytree=0.8,
        subsample=0.8,
        random_state=RANDOM_SEED,
        verbosity=0,
    )

    ensemble = VotingRegressor(
        [("mlp", mlp), ("gbr", gbr), ("xgb", xgb)],
        weights=GNN_ENSEMBLE_WEIGHTS,
    )

    pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("model", ensemble),
    ])
    pipe.fit(X_train, y_train)

    logger.info("[4/5] Evaluating GNN Ensemble...")
    r2_test = pipe.score(X_test, y_test)
    y_pred = pipe.predict(X_test)
    mae = float(np.mean(np.abs(y_pred - y_test)))
    rmse = float(np.sqrt(np.mean((y_pred - y_test) ** 2)))

    cv_scores = cross_val_score(pipe, X, y, cv=GNN_CV_FOLDS, scoring="r2")
    logger.info("  Test R2 : %.4f", r2_test)
    logger.info("  MAE     : %.2f pF/m", mae)
    logger.info("  RMSE    : %.2f pF/m", rmse)
    logger.info("  %d-Fold CV R2: %.4f +/- %.4f", GNN_CV_FOLDS, cv_scores.mean(), cv_scores.std())

    # Parity Plot
    graphs_dir = _REPO_ROOT / "graphs"
    graphs_dir.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(7, 6))
    plt.scatter(y_test, y_pred, alpha=0.6, color="steelblue", edgecolors="k", lw=0.3)
    lims = [min(y_test.min(), y_pred.min()), max(y_test.max(), y_pred.max())]
    plt.plot(lims, lims, "r--", label="Perfect Prediction")
    plt.xlabel("Actual Capacitance (pF/m)")
    plt.ylabel("GNN Ensemble Prediction (pF/m)")
    plt.title(f"GNN (MPNN) Surrogate Model Parity Plot\nR2 = {r2_test:.4f}")
    plt.legend()
    plt.tight_layout()
    plt.savefig(graphs_dir / "gnn_parity_plot.png", dpi=300)
    plt.close()
    logger.info("  -> Saved: gnn_parity_plot.png")

    logger.info("[5/5] Saving GNN ensemble model -> %s", OUTPUT_MODEL)
    OUTPUT_MODEL.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipe, OUTPUT_MODEL)

    logger.info("=" * 60)
    logger.info("  Phase 5.2 COMPLETE")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
