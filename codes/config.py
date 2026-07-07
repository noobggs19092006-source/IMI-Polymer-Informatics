"""
Configuration Module for IMI Polymer Informatics Architecture.
Phase 2 Extended — includes model tuning, ensemble, and class inference config.
"""
import pandas as pd
import numpy as np
from config_manager import pipeline_config

# CollinearityDropper has been moved to transformers.py (P2 Code Hygiene).
# Import it here so existing code that does `from config import CollinearityDropper`
# continues to work without change.
from transformers import CollinearityDropper  # noqa: F401  (re-export)

# Dynamic Architecture Constraints
NUM_SAMPLES = 1440
NUM_STRUCTURAL = 40
NUM_PHYSICAL = 40
NUM_POLYBERT_PCA = 128
NUM_MORGAN_PCA = 256

# Optimization Bounds
TEMP_BOUNDS = (100, 300)
CRYST_BOUNDS = (0.10, 0.90)

TARGET_TG_NOISE = 12.0
RANDOM_SEED = pipeline_config["simulation"]["random_seed"]

# ─── Phase A: MLP Hyperparameter Tuning ─────────────────────────────────────
# Deeper architecture + adaptive LR to fix the convergence warning (max_iter=200)
MLP_HIDDEN_LAYER_SIZES = (128, 64)  # Reduced to prevent severe overfitting
MLP_ALPHA = 0.01  # L2 regularization
MLP_ACTIVATION = "relu"
MLP_SOLVER = "adam"
MLP_LEARNING_RATE = "adaptive"  # drops LR when loss plateaus
MLP_LEARNING_RATE_INIT = 0.001
MLP_MAX_ITER = 2000  # was 200 — guaranteed convergence
MLP_EARLY_STOPPING = True
MLP_VALIDATION_FRACTION = 0.10
MLP_N_ITER_NO_CHANGE = 20  # patience

# ─── Phase A: Gradient Boosting Ensemble (GBR) ───────────────────────────────
GBR_N_ESTIMATORS = 300
GBR_LEARNING_RATE = 0.05
GBR_MAX_DEPTH = 5
GBR_SUBSAMPLE = 0.8
GBR_MIN_SAMPLES_LEAF = 4
GBR_RANDOM_STATE = RANDOM_SEED

# ─── Phase A: Ensemble Blend Weights ─────────────────────────────────────────
# VotingRegressor weights: [MLP, GBR]
ENSEMBLE_WEIGHTS = (0.55, 0.45)

# ─── Phase B: Polymer Class Inference (SMILES Pattern Matching) ──────────────
# Used by code_10_conditional_search and the API routers
CLASS_PATTERNS = {
    "PVDF": ["C(F)", "C(F)(F)", "CF"],  # fluorinated backbone
    "PET": ["C(=O)c1", "OCC", "c1ccc"],  # aromatic ester linkages
    "PP": ["CC(", "[*]C("],  # aliphatic olefin backbone
}
CLASS_PRIORITY = ["PVDF", "PET", "PP"]  # checked in this order

# ─── Phase C: API Config ──────────────────────────────────────────────────────
MODEL_PATH = "mlp_pipeline.pkl"  # backward-compat model
ENSEMBLE_PATH = "ensemble_pipeline.pkl"  # new ensemble model
DATASET_PATH = "ready_polymer_dataset.csv"
GOOD_FIT_THRESHOLD = 450.0  # MV/m cutoff from code_9

# ─── ANSYS FEA Parameters ─────────────────────────────────────────────────────
ANSYS_CORE_COUNT = pipeline_config["ansys"]["core_count"]
ANSYS_MESH_RESOLUTION = pipeline_config["ansys"]["mesh_resolution"]
ANSYS_SESSION_RESTART_INTERVAL = 50

# ─── Phase B: ANSYS Ensemble Hyperparameters ──────────────────────────────────
# MLP
ANSYS_MLP_HIDDEN = (128, 64, 32)
ANSYS_MLP_PATIENCE = 200
# GBR
ANSYS_GBR_ESTIMATORS = 300
ANSYS_GBR_DEPTH = 4
# XGBoost
ANSYS_XGB_ESTIMATORS = 300
ANSYS_XGB_DEPTH = 4

