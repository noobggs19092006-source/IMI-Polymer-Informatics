"""
rank_successful_polymers.py — Post-simulation ranking utility.

Reads ansys_simulation_results.csv, filters successful simulations,
ranks by capacitance, and writes a sorted output CSV.
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from logger_setup import PipelineLogger

PipelineLogger.setup_logging()
logger = PipelineLogger.get_logger(__name__)

# ── Paths ─────────────────────────────────────────────────────────────────────
_REPO_ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE: Path = _REPO_ROOT / "results" / "ansys_simulation_results.csv"
OUTPUT_FILE: Path = _REPO_ROOT / "results" / "ranked_successful_polymers.csv"


def rank_polymers() -> None:
    if not INPUT_FILE.exists():
        logger.error("Input file not found: %s", INPUT_FILE)
        return

    logger.info("--- Analyzing %s ---", INPUT_FILE)
    df = pd.read_csv(INPUT_FILE)

    success_df = df[df["sim_status"] == "Success"].copy()
    logger.info(
        "Found %d successful simulations out of %d total.", len(success_df), len(df)
    )

    ranked_df = success_df.sort_values(
        by="sim_capacitance_F", ascending=False
    ).reset_index(drop=True)

    logger.info("--- TOP 10 HIGHEST CAPACITANCE POLYMERS ---")
    for i, row in ranked_df.head(10).iterrows():
        smiles_trunc = row["smiles"][:20] + "..." if len(row["smiles"]) > 20 else row["smiles"]
        logger.info(
            "#%-4d | %-15s | %10.2f pF/m | %8.1f nm | eps=%.2f | %s",
            i + 1,
            row["base_material"],
            row["sim_capacitance_F"],
            row["thickness_nm"],
            row["dielectric_constant"],
            smiles_trunc,
        )

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    ranked_df.to_csv(OUTPUT_FILE, index=False)
    logger.info(
        "Full ranked list containing %d success cases saved to: %s",
        len(ranked_df),
        OUTPUT_FILE,
    )


if __name__ == "__main__":
    rank_polymers()
