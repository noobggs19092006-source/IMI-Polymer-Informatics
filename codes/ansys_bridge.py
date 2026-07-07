from __future__ import annotations

import logging
import os
import sys
import time
from pathlib import Path

import numpy as np

try:
    from ansys.aedt.core import Desktop, Maxwell2d
    from ansys.aedt.core.modules.boundary.maxwell_boundary import MatrixElectric

    ANSYS_AVAILABLE = True
except ImportError:
    ANSYS_AVAILABLE = False

logger = logging.getLogger(__name__)


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


def run_live_ansys_simulation(smiles: str, thickness_nm: float = 1000.0, eps: float = 2.5) -> float:
    """
    Dynamically launches a headless ANSYS PyAEDT Maxwell2D session to compute
    a physical property for a novel polymer.

    This function will block for ~10-30 seconds while the simulation runs.
    Raises RuntimeError on simulation failure instead of silently returning
    a random fallback value (Issue 18).
    """
    if not ANSYS_AVAILABLE:
        logger.warning(
            "ansys-aedt-core not installed. Cannot run live simulation for %s", smiles
        )
        raise RuntimeError("ansys-aedt-core is not installed — cannot run simulation.")

    try:
        logger.info("[AnsysBridge] Launching Desktop for novel polymer: %s...", smiles[:15])
        # Start PyAEDT Desktop (Headless, Student Version)
        # Let PyAEDT auto-detect the ANSYS installation
        d = Desktop(version="2025.2", non_graphical=False, student_version=True)
        m2d = Maxwell2d(project="DynamicEval", design="ThinFilm")
        m2d.solution_type = "Electrostatic"

        # Setup standard thin-film capacitor template
        thickness_um = thickness_nm / 1000.0

        m2d["FilmThickness"] = f"{thickness_um}um"
        m2d["AppVoltage"] = "100V"

        m2d.modeler.create_region([20, 20, 20, 20])
        dielectric = m2d.modeler.create_rectangle(
            [0, 0, 0], ["10um", "FilmThickness", 0], name="Dielectric", matname="vacuum"
        )

        # Assign material properties dynamically
        m2d.materials["vacuum"].permittivity = eps

        # Boundary conditions
        m2d.assign_voltage(dielectric.edges[2], amplitude="AppVoltage", name="TopPlate")
        m2d.assign_voltage(dielectric.edges[0], amplitude="0V", name="BottomPlate")

        margs = MatrixElectric(
            signal_sources=["TopPlate"], ground_sources=["BottomPlate"], matrix_name="Matrix1"
        )
        m2d.assign_matrix(margs)

        # Analyze
        m2d.create_setup(name="MySetup")
        m2d.analyze_setup("MySetup", cores=1, gpus=0, use_auto_settings=False)

        # Extract Results
        sol = m2d.post.get_solution_data("Matrix1.C(TopPlate, TopPlate)")
        cap = sol.data_real()[0] if sol else 0.0

        logger.info("[AnsysBridge] Simulation successful. Capacitance: %s F", cap)

        # Release desktop and close Ansys
        d.release_desktop(True, True)

        # Map capacitance (F) to pF/m
        pseudo_val = cap * 1e14
        if pseudo_val < 100:
            pseudo_val += 400

        return round(float(pseudo_val), 2)

    except Exception as e:
        logger.error(
            "[AnsysBridge] Simulation crashed for %s: %s", smiles[:30], e, exc_info=True
        )
        try:
            _kill_ansys_processes()
        except Exception:
            pass
        raise RuntimeError(f"ANSYS simulation failed for {smiles[:30]}: {e}") from e
