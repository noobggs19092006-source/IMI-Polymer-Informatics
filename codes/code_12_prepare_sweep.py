"""
code_12_prepare_sweep.py — Combinatorial SMILES Sweep Target Generator.

Generates all 1440 polymer configurations that will be submitted to ANSYS Maxwell 2D.
All random number generation is seeded via enforce_reproducibility() so the output
CSV is bit-identical across machines.
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# ── Reproducibility (must come before any random calls) ──────────────────────
sys.path.insert(0, str(Path(__file__).resolve().parent))
from reproducibility import enforce_reproducibility

enforce_reproducibility(42)

from constants import (  # noqa: E402
    BACKBONES,
    DENSITY_NOISE,
    EPS_NOISE,
    LEFT_GROUPS,
    RIGHT_GROUPS,
    SWEEP_REPEAT,
    TEMP_LEVELS,
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

# ── Paths (relative to this file, not CWD) ──────────────────────────────────
_REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_FILE: Path = _REPO_ROOT / "results" / "ansys_sweep_targets.csv"


def generate_targets(seed: int = 42) -> pd.DataFrame:
    """
    Build the combinatorial polymer dataset.

    Uses a local numpy Generator seeded from *seed* so results are independent
    of any global random-state mutations by other modules.
    """
    rng = np.random.default_rng(seed)

    data: list[dict] = []

    for _ in range(SWEEP_REPEAT):
        for name, meta in BACKBONES.items():
            for lg in LEFT_GROUPS:
                for rg in RIGHT_GROUPS:
                    mutated_smiles = f"{lg}{meta['backbone']}{rg}"

                    data.append(
                        {
                            "smiles": mutated_smiles,
                            "base_material": name,
                            "dielectric_constant": meta["eps"] + rng.uniform(-EPS_NOISE, EPS_NOISE),
                            "tg_celsius": meta["tg"] + rng.uniform(-TG_NOISE, TG_NOISE),
                            "density_g_cm3": meta["density"] + rng.uniform(-DENSITY_NOISE, DENSITY_NOISE),
                            "thickness_nm": rng.uniform(THICKNESS_MIN_NM, THICKNESS_MAX_NM),
                            "applied_voltage": rng.uniform(VOLTAGE_MIN_V, VOLTAGE_MAX_V),
                            "temp_c": int(rng.choice(TEMP_LEVELS)),
                        }
                    )

    # Deterministic shuffle using the same rng
    rng.shuffle(data)  # type: ignore[arg-type]

    df = pd.DataFrame(data)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)

    logger.info("Created %s with %d unique polymer structures (%d total sweep samples)!", OUTPUT_FILE, len(df) // SWEEP_REPEAT, len(df))
    return df


if __name__ == "__main__":
    logger.info("--- Preparing Combinatorial SMILES Sweep Targets ---")
    generate_targets()
