"""
constants.py — Single Source of Truth for All Magic Numbers and Shared Data.

All BACKBONES, LEFT_GROUPS, RIGHT_GROUPS, and numeric constants live here.
Import from this module in ALL entry-point scripts instead of repeating.
"""
from __future__ import annotations

# ──────────────────────────────────────────────────────────────────────────────
# Random / Reproducibility
# ──────────────────────────────────────────────────────────────────────────────
RANDOM_SEED: int = 42

# ──────────────────────────────────────────────────────────────────────────────
# Data Generation (code_12_prepare_sweep)
# ──────────────────────────────────────────────────────────────────────────────
SWEEP_REPEAT: int = 2           # how many times the combinatorial grid is repeated
EPS_NOISE: float = 0.1          # ±noise on dielectric constant
TG_NOISE: float = 5.0           # ±noise on glass-transition temperature (°C)
DENSITY_NOISE: float = 0.05     # ±noise on density (g/cm³)
THICKNESS_MIN_NM: float = 500.0
THICKNESS_MAX_NM: float = 5000.0
VOLTAGE_MIN_V: float = 10.0
VOLTAGE_MAX_V: float = 500.0
TEMP_LEVELS: list[int] = [25, 100, 200, 300]   # standard test temperatures (°C)

# ──────────────────────────────────────────────────────────────────────────────
# Inverse Design (code_14_inverse_ansys, code_17_pareto_optimization)
# ──────────────────────────────────────────────────────────────────────────────
NUM_VIRTUAL_CANDIDATES: int = 25_000
TARGET_CAPACITANCE_PF_M: float = 200.0   # industrial EV target (pF/m)

# ──────────────────────────────────────────────────────────────────────────────
# Shared Polymer Library — canonical single definition
# ──────────────────────────────────────────────────────────────────────────────
BACKBONES: dict[str, dict] = {
    "PE":           {"backbone": "CCCCC",                           "eps": 2.2,  "tg": -120, "density": 0.92},
    "PP":           {"backbone": "CC(C)CC(C)",                      "eps": 2.2,  "tg": -10,  "density": 0.90},
    "PVC":          {"backbone": "CC(Cl)CC(Cl)",                    "eps": 3.5,  "tg": 80,   "density": 1.40},
    "PTFE":         {"backbone": "C(F)(F)C(F)(F)",                  "eps": 2.1,  "tg": 115,  "density": 2.20},
    "PVDF":         {"backbone": "CC(F)(F)CC(F)(F)",                "eps": 12.0, "tg": -35,  "density": 1.78},
    "Polystyrene":  {"backbone": "CC(c1ccccc1)CC(c1ccccc1)",        "eps": 2.5,  "tg": 100,  "density": 1.05},
    "PMMA":         {"backbone": "CC(C)(C(=O)OC)CC(C)(C(=O)OC)",   "eps": 3.0,  "tg": 105,  "density": 1.18},
    "Polycarbonate":{"backbone": "Oc1ccc(cc1)C(C)(C)c2ccc(cc2)O",  "eps": 2.9,  "tg": 145,  "density": 1.20},
    "PET":          {"backbone": "C(=O)c1ccc(cc1)C(=O)OCCO",       "eps": 3.3,  "tg": 75,   "density": 1.38},
    "Nylon-6":      {"backbone": "CCCCCC(=O)N",                     "eps": 3.5,  "tg": 47,   "density": 1.14},
}

LEFT_GROUPS: list[str]  = ["C", "CC", "CCC", "FC(F)(F)", "Cl", "CO", "CC(=O)", "c1ccccc1", "N", "O", "S", "Br"]
RIGHT_GROUPS: list[str] = ["C", "CC", "CCC", "C(F)(F)F", "Cl", "OC", "C(=O)O", "C#N", "O", "S", "Br", "N"]
