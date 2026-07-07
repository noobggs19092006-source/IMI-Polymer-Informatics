from __future__ import annotations

import logging
import os
import sys
import time
from pathlib import Path

import pandas as pd
from ansys.aedt.core import Desktop, Maxwell2d
from ansys.aedt.core.modules.boundary.maxwell_boundary import MatrixElectric

sys.path.insert(0, str(Path(__file__).resolve().parent))
from reproducibility import enforce_reproducibility

enforce_reproducibility(42)

import config
from adaptive_retry_manager import EnhancedSimulationManager

from logger_setup import PipelineLogger

PipelineLogger.setup_logging()
logger = PipelineLogger.get_logger(__name__)

# ── Paths (relative to this file, not CWD) ───────────────────────────────────
_REPO_ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE: Path = _REPO_ROOT / "results" / "ansys_sweep_targets.csv"
OUTPUT_FILE: Path = _REPO_ROOT / "results" / "ansys_simulation_results.csv"

SAMPLES_PER_SESSION: int = config.ANSYS_SESSION_RESTART_INTERVAL
MAX_MESH_RETRIES: int = 3
THICKNESS_BACKOFF_FACTOR: float = 0.1


def _kill_ansys_processes() -> None:
    """Terminate orphaned ANSYS processes in a cross-platform manner."""
    import subprocess
    if sys.platform == "win32":
        for exe in ("ansysedt.exe", "ansysedtsv.exe"):
            subprocess.run(["taskkill", "/F", "/IM", exe, "/T"],
                           capture_output=True, check=False)
    else:
        for pattern in ("ansysedt", "ansysedtsv"):
            subprocess.run(["pkill", "-f", pattern],
                           capture_output=True, check=False)


def run_single_sample(m2d, row, thickness_override_nm=None):
    """
    5.5 Adaptive Error Handling: Attempt to run one sample.
    Returns (cap_value, status_string).
    Raises RuntimeError on irrecoverable mesh failure.
    """
    eps = row["dielectric_constant"]
    thickness_nm = thickness_override_nm if thickness_override_nm else row["thickness_nm"]
    thickness_um = thickness_nm / 1000.0
    voltage = row["applied_voltage"]

    m2d["FilmThickness"] = f"{thickness_um}um"
    m2d["AppVoltage"] = f"{voltage}V"
    m2d.materials["vacuum"].permittivity = eps
    m2d.analyze_setup("MySetup", cores=config.ANSYS_CORE_COUNT, gpus=0, use_auto_settings=False)

    sol = m2d.post.get_solution_data("Matrix1.C(TopPlate, TopPlate)")
    cap = sol.data_real()[0] if sol else 0.0
    return cap


def run_simulation_sweep() -> None:  # noqa: C901
    if not INPUT_FILE.exists():
        logger.error("Input file %s not found. Run code_12_prepare_sweep first.", INPUT_FILE)
        sys.exit(1)

    df_targets = pd.read_csv(INPUT_FILE)
    logger.info("--- Starting ANSYS Sweep (%d samples) ---", len(df_targets))

    results = []
    if os.path.exists(OUTPUT_FILE):
        df_existing = pd.read_csv(OUTPUT_FILE)
        start_index = len(df_existing)
        results = df_existing.to_dict("records")
        logger.info("Resuming from sample %d...", start_index)
    else:
        start_index = 0

    total_samples = len(df_targets)
    current_index = start_index

    while current_index < total_samples:
        try:
            logger.info("Session Start: Index %d", current_index)
            d = Desktop(version="2025.2", non_graphical=False, student_version=True)
            m2d = Maxwell2d(project="CapacitorSweep", design="ThinFilm")
            m2d.solution_type = "Electrostatic"

            # Setup Template
            m2d["FilmThickness"] = "1um"
            m2d["AppVoltage"] = "100V"
            m2d.modeler.create_region([20, 20, 20, 20])
            dielectric = m2d.modeler.create_rectangle(
                [0, 0, 0], ["10um", "FilmThickness", 0], name="Dielectric", matname="vacuum"
            )
            m2d.assign_voltage(dielectric.edges[2], amplitude="AppVoltage", name="TopPlate")
            m2d.assign_voltage(dielectric.edges[0], amplitude="0V", name="BottomPlate")
            margs = MatrixElectric(
                signal_sources=["TopPlate"], ground_sources=["BottomPlate"], matrix_name="Matrix1"
            )
            m2d.assign_matrix(margs)
            m2d.create_setup(name="MySetup")

            batch_end = min(current_index + SAMPLES_PER_SESSION, total_samples)
            for i in range(current_index, batch_end):
                row = df_targets.iloc[i]
                smiles = row["smiles"]

                # ── 5.5 Adaptive Mesh Retry Loop ──────────────────────────
                cap = 0.0
                status = "Failed"

                sim_manager = EnhancedSimulationManager()
                params = {
                    "thickness_nm": row["thickness_nm"],
                    "backoff_factor": THICKNESS_BACKOFF_FACTOR,
                    "voltage": row["applied_voltage"],
                }

                for attempt in range(1, MAX_MESH_RETRIES + 1):
                    try:
                        cap = run_single_sample(
                            m2d, row, thickness_override_nm=params["thickness_nm"]
                        )
                        status = "Success" if cap > 0 else "Failed"
                        if cap > 0:
                            break
                    except Exception as err:
                        should_retry, new_params, failure_mode = sim_manager.diagnose_and_adapt(
                            err, params, attempt, MAX_MESH_RETRIES
                        )
                        if should_retry:
                            logger.warning(
                                "[Retry %d/%d] Error diagnosed as %s. "
                                "Backing off thickness from %.0f nm to %.0f nm...",
                                attempt, MAX_MESH_RETRIES, failure_mode,
                                params['thickness_nm'], new_params['thickness_nm'],
                            )
                            params = new_params
                        else:
                            logger.error(
                                "[FAILED] Sample %d exhausted %d retries. Final mode: %s",
                                i, MAX_MESH_RETRIES, failure_mode,
                            )
                            status = "Failed Extraction"

                sim_manager.save_failure_report()

                row_res = row.to_dict()
                row_res["sim_capacitance_F"] = cap
                row_res["sim_status"] = status
                row_res["final_thickness_nm"] = params["thickness_nm"]
                results.append(row_res)

                logger.info(
                    "[%d/%d] %s... -> %.2f pF/m [%s]",
                    i + 1, total_samples, smiles[:20], cap, status,
                )

                if (i + 1) % 2000 == 0:
                    pd.DataFrame(results).to_csv(OUTPUT_FILE, index=False)
                current_index += 1

            d.release_desktop(True, True)

        except Exception as e:
            logger.error("Session crashed, restarting: %s", str(e)[:120], exc_info=True)
            _kill_ansys_processes()
            time.sleep(5)

    pd.DataFrame(results).to_csv(OUTPUT_FILE, index=False)
    logger.info("Sweep Complete! Results saved to %s", OUTPUT_FILE)
    sys.exit(0)


if __name__ == "__main__":
    run_simulation_sweep()
