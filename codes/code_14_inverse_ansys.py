"""
code_14_inverse_ansys.py — Phase C: Inverse Design via Virtual High-Throughput Screening.

Loads the trained 3-Way Ensemble and screens NUM_VIRTUAL_CANDIDATES random polymer
configurations to find those closest to TARGET_CAPACITANCE_PF_M.
All random generation is seeded for full reproducibility.
"""
from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import rdMolDescriptors

# ── Reproducibility (must be first) ──────────────────────────────────────────
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
    TEMP_LEVELS,
    TG_NOISE,
    THICKNESS_MAX_NM,
    THICKNESS_MIN_NM,
    VOLTAGE_MAX_V,
    VOLTAGE_MIN_V,
)

RDLogger.DisableLog("rdApp.*")

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# ── Paths ─────────────────────────────────────────────────────────────────────
_REPO_ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH: Path = _REPO_ROOT / "files" / "ansys_ensemble_pipeline.pkl"


def smiles_to_morgan(smi: str, n_bits: int = 512) -> np.ndarray:
    """Convert a SMILES string to a Morgan fingerprint bit-vector."""
    mol = Chem.MolFromSmiles(smi)
    if mol is None:
        return np.zeros(n_bits)
    fp = rdMolDescriptors.GetMorganFingerprintAsBitVect(mol, radius=2, nBits=n_bits)
    return np.array(fp)


def run_inverse_design(seed: int = 42) -> None:
    logger.info("============================================================")
    logger.info("  Phase C — Inverse Design (Target: %.1f pF/m)", TARGET_CAPACITANCE_PF_M)
    logger.info("============================================================")

    if not MODEL_PATH.exists():
        logger.error("Model %s not found. Run code_13 first.", MODEL_PATH)
        return

    logger.info("[1/4] Loading trained 3-Way Ensemble Model...")
    model = joblib.load(MODEL_PATH)

    logger.info("[2/4] Generating Virtual Library (%d random configurations)...", NUM_VIRTUAL_CANDIDATES)

    # Use a local seeded RNG — independent of global state
    rng = np.random.default_rng(seed)
    backbone_names = list(BACKBONES.keys())

    candidates: list[dict] = []
    fps: list[np.ndarray] = []

    for _ in range(NUM_VIRTUAL_CANDIDATES):
        name = backbone_names[int(rng.integers(len(backbone_names)))]
        meta = BACKBONES[name]
        lg = LEFT_GROUPS[int(rng.integers(len(LEFT_GROUPS)))]
        rg = RIGHT_GROUPS[int(rng.integers(len(RIGHT_GROUPS)))]

        smi = f"{lg}{meta['backbone']}{rg}"

        candidates.append(
            {
                "smiles": smi,
                "base_material": name,
                "dielectric_constant": meta["eps"] + rng.uniform(-EPS_NOISE, EPS_NOISE),
                "tg_celsius": meta["tg"] + rng.uniform(-TG_NOISE, TG_NOISE),
                "density_g_cm3": meta["density"] + rng.uniform(-DENSITY_NOISE, DENSITY_NOISE),
                "thickness_nm": rng.uniform(THICKNESS_MIN_NM, THICKNESS_MAX_NM),
                "applied_voltage": rng.uniform(VOLTAGE_MIN_V, VOLTAGE_MAX_V),
                "temp_c": int(rng.choice(TEMP_LEVELS)),
            }
        )
        fps.append(smiles_to_morgan(smi))

    df_cand = pd.DataFrame(candidates)

    logger.info("[3/4] Running ultra-fast Machine Learning predictions...")
    fp_cols = [f"Morgan_{i}" for i in range(512)]
    df_fps = pd.DataFrame(fps, columns=fp_cols)
    physical_cols = [
        "dielectric_constant", "tg_celsius", "density_g_cm3", "thickness_nm", "applied_voltage", "temp_c"
    ]
    X = pd.concat([df_fps, df_cand[physical_cols]], axis=1)

    predictions = model.predict(X)
    df_cand["predicted_capacitance_pF_m"] = predictions * 1e12

    logger.info("[4/4] Ranking candidates by proximity to target...")
    df_cand["delta"] = abs(df_cand["predicted_capacitance_pF_m"] - TARGET_CAPACITANCE_PF_M)
    df_top = df_cand.nsmallest(10, "delta")

    logger.info("\nTop 5 Candidates:")
    for i, row in df_top.head(5).iterrows():
        logger.info(
            "  Rank %d | %s | Predicted: %.2f pF/m | Delta: %.2f",
            int(i) + 1,
            row["smiles"][:30],
            row["predicted_capacitance_pF_m"],
            row["delta"],
        )

    # Save results
    out_path = _REPO_ROOT / "results" / "inverse_design_candidates.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df_top.to_csv(out_path, index=False)
    logger.info("Saved top candidates -> %s", out_path)


if __name__ == "__main__":
    run_inverse_design()
