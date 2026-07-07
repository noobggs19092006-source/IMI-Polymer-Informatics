from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors

sys.path.insert(0, str(Path(__file__).resolve().parent))
from reproducibility import enforce_reproducibility

enforce_reproducibility(42)

from constants import (  # noqa: E402
    BACKBONES,
    DENSITY_NOISE,
    EPS_NOISE,
    LEFT_GROUPS,
    NUM_VIRTUAL_CANDIDATES,
    RIGHT_GROUPS,
    TARGET_CAPACITANCE_PF_M,
    TG_NOISE,
    THICKNESS_MAX_NM,
    THICKNESS_MIN_NM,
    VOLTAGE_MAX_V,
    VOLTAGE_MIN_V,
)

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# ── Paths ────────────────────────────────────────────────────────
_REPO_ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH: Path = _REPO_ROOT / "files" / "ansys_ensemble_pipeline.pkl"
NUM_CANDIDATES = NUM_VIRTUAL_CANDIDATES  # alias for clarity



def smiles_to_morgan(smi, n_bits=512):
    mol = Chem.MolFromSmiles(smi)
    if mol is None:
        return np.zeros(n_bits)
    fp = rdMolDescriptors.GetMorganFingerprintAsBitVect(mol, radius=2, nBits=n_bits)
    return np.array(fp)


# --- PARETO FRONT ALGORITHM ---
def identify_pareto(scores):
    """
    Find the pareto-efficient points
    scores is a numpy array of shape (N, 2).
    We want to MINIMIZE column 0 (Capacitance Error) and MAXIMIZE column 1 (Tg).
    Since standard pareto algorithms minimize both, we will invert column 1 for the math.
    """
    # Create a copy where objective 2 is inverted
    scores_inv = scores.copy()
    scores_inv[:, 1] = -scores_inv[:, 1]

    population_size = scores_inv.shape[0]
    pareto_front = np.ones(population_size, dtype=bool)
    for i in range(population_size):
        for j in range(population_size):
            if all(scores_inv[j] <= scores_inv[i]) and any(scores_inv[j] < scores_inv[i]):
                pareto_front[i] = 0
                break
    return pareto_front


def main() -> None:
    logger.info("============================================================")
    logger.info("  Phase 5.1 — Multi-Objective Pareto Optimization")
    logger.info("  Objective 1: Minimize Error from %.1f pF/m", TARGET_CAPACITANCE_PF_M)
    logger.info("  Objective 2: Maximize Thermal Stability (Tg Celsius)")
    logger.info("============================================================")

    if not MODEL_PATH.exists():
        logger.error("Model %s not found. Run code_13 first.", MODEL_PATH)
        return

    logger.info("[1/4] Loading trained Ensemble Model...")
    model = joblib.load(MODEL_PATH)

    logger.info("[2/4] Generating Virtual Library (%d random configurations)...", NUM_CANDIDATES)
    rng = np.random.default_rng(42)
    backbone_names = list(BACKBONES.keys())
    candidates: list[dict] = []
    fps: list[np.ndarray] = []

    for _ in range(NUM_CANDIDATES):
        name = backbone_names[int(rng.integers(len(backbone_names)))]
        meta = BACKBONES[name]
        smi = (
            f"{LEFT_GROUPS[int(rng.integers(len(LEFT_GROUPS)))]}"
            f"{meta['backbone']}"
            f"{RIGHT_GROUPS[int(rng.integers(len(RIGHT_GROUPS)))]}"
        )
        tg = meta["tg"] + rng.uniform(-TG_NOISE, TG_NOISE)
        candidates.append(
            {
                "smiles": smi,
                "base_material": name,
                "dielectric_constant": meta["eps"] + rng.uniform(-EPS_NOISE, EPS_NOISE),
                "tg_celsius": tg,
                "density_g_cm3": meta["density"] + rng.uniform(-DENSITY_NOISE, DENSITY_NOISE),
                "thickness_nm": rng.uniform(THICKNESS_MIN_NM, THICKNESS_MAX_NM),
                "applied_voltage": rng.uniform(VOLTAGE_MIN_V, VOLTAGE_MAX_V),
                "temp_c": 25,
            }
        )
        fps.append(smiles_to_morgan(smi))

    df_cand = pd.DataFrame(candidates)

    logger.info("[3/4] Running ultra-fast Machine Learning predictions...")
    fp_cols = [f"Morgan_{i}" for i in range(512)]
    df_fps = pd.DataFrame(np.vstack(fps), columns=fp_cols)
    physical_cols = [
        "dielectric_constant", "tg_celsius", "density_g_cm3",
        "thickness_nm", "applied_voltage", "temp_c",
    ]
    X = pd.concat([df_fps, df_cand[physical_cols]], axis=1)
    preds = model.predict(X)
    df_cand["predicted_capacitance"] = preds
    df_cand["cap_error"] = abs(df_cand["predicted_capacitance"] - TARGET_CAPACITANCE_PF_M)

    logger.info("[4/4] Calculating Pareto-Optimal Front...")
    scores = df_cand[["cap_error", "tg_celsius"]].values
    pareto_mask = identify_pareto(scores)
    pareto_df = df_cand[pareto_mask].sort_values(by="tg_celsius", ascending=False)

    out_path = _REPO_ROOT / "results" / "pareto_optimal_polymers.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    pareto_df.to_csv(out_path, index=False)
    logger.info("Identified %d Pareto-Optimal polymers out of %d.", len(pareto_df), NUM_CANDIDATES)
    logger.info("Saved to %s", out_path)

    # --- PLOTTING ---
    plt.figure(figsize=(10, 7))
    # Plot all candidates in grey
    plt.scatter(
        df_cand["tg_celsius"],
        df_cand["cap_error"],
        c="lightgrey",
        alpha=0.5,
        label="Sub-optimal Candidates",
        s=10,
    )
    # Plot Pareto Front in red
    plt.scatter(
        pareto_df["tg_celsius"],
        pareto_df["cap_error"],
        c="red",
        label="Pareto Front",
        s=30,
        edgecolor="black",
    )

    plt.title(
        f"Multi-Objective Pareto Optimization\nTarget: {TARGET_CAPACITANCE_PF_M} pF/m vs Thermal Stability (Tg)"
    )
    plt.xlabel("Thermal Stability (Tg Celsius) $\\rightarrow$ Maximize")
    plt.ylabel(f"Absolute Capacitance Error from {TARGET_CAPACITANCE_PF_M} pF/m $\\rightarrow$ Minimize")
    plt.axhline(0, color="black", linestyle="--")
    plt.ylim(-10, 150)  # Zoom in on the relevant error region
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    graphs_dir = _REPO_ROOT / "graphs"
    graphs_dir.mkdir(parents=True, exist_ok=True)
    plt.savefig(graphs_dir / "pareto_front.png", dpi=300)
    logger.info("Generated plot: pareto_front.png")


if __name__ == "__main__":
    main()
