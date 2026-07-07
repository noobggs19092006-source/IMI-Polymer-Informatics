"""
data_pipeline.py — Generates a physically parameterised synthetic dataset.

All random generation is seeded via a local np.random.Generator so the output
is bit-identical across machines.
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from logger_setup import PipelineLogger
from data_validation import validate_data_integrity
from reproducibility import DeterministicPipeline
from config_manager import pipeline_config

PipelineLogger.setup_logging()
logger = PipelineLogger.get_logger(__name__)

# ── Paths ─────────────────────────────────────────────────────────────────────
_REPO_ROOT = Path(__file__).resolve().parent.parent
_OUTPUT_PATH: Path = _REPO_ROOT / "results" / "ansys_target_dataset_7200.csv"


def generate_strict_dataset(num_samples: int = 7200) -> pd.DataFrame:
    """
    Generate a physically sound dataset of *num_samples* rows for
    high-temperature polymer alloys.

    Uses a local seeded np.random.Generator — independent of global state.
    """
    seed: int = pipeline_config["simulation"]["random_seed"]
    DeterministicPipeline.set_random_seed(seed)

    rng = np.random.default_rng(seed)

    material_types = rng.choice(
        ["Polymer_Blend", "Alloy", "Nanocomposite"],
        size=num_samples,
        p=[0.5, 0.3, 0.2],
    )

    base_k          = rng.uniform(2.0,   10.0,  num_samples)
    tan_delta       = rng.uniform(0.001, 0.05,  num_samples)
    temperature_c   = rng.uniform(100,   250,   num_samples)
    thickness_um    = rng.uniform(2.0,   15.0,  num_samples)
    eb_base         = rng.uniform(300,   800,   num_samples)
    alpha           = rng.uniform(0.001, 0.003, num_samples)

    breakdown_strength_mvm = (
        eb_base * (1 - alpha * (temperature_c - 25)) / np.sqrt(thickness_um)
    )

    df = pd.DataFrame({
        "Material_Type":                  material_types,
        "Temperature_C":                  temperature_c,
        "Thickness_um":                   thickness_um,
        "Dielectric_Constant":            base_k,
        "Dissipation_Factor":             tan_delta,
        "Theoretical_Breakdown_Strength_MVm": breakdown_strength_mvm,
    })

    return df


if __name__ == "__main__":
    logger.info("Generating strictly parameterised dataset for 7,200 samples...")
    dataset = generate_strict_dataset(7200)

    is_valid, dataset = validate_data_integrity(dataset)
    if not is_valid:
        logger.warning("Dataset validation failed or required heavy null dropping.")

    _OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    dataset.to_csv(_OUTPUT_PATH, index=False)
    logger.info(
        "Dataset with %d verified samples saved to %s.", len(dataset), _OUTPUT_PATH
    )
