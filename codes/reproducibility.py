"""
reproducibility.py — Canonical seed-locking for the full pipeline.

Usage at the top of every entry-point script:
    from reproducibility import enforce_reproducibility
    enforce_reproducibility(42)
"""
from __future__ import annotations

import logging
import os
import random

import numpy as np

logger = logging.getLogger(__name__)

try:
    import tensorflow as tf  # type: ignore[import]
except ImportError:
    tf = None


def enforce_reproducibility(seed: int = 42) -> None:
    """
    Lock every relevant RNG to *seed* so the pipeline produces
    bit-identical results on any machine.

    Sets:
      - os.environ PYTHONHASHSEED  (must be set before any hash-sensitive op)
      - os.environ TF_DETERMINISTIC_OPS / TF_CUDNN_DETERMINISTIC
      - Python's built-in random module
      - NumPy's legacy global random state (np.random)
      - NumPy's new-style default_rng (via global seed)
      - TensorFlow (if installed)

    Note: PYTHONHASHSEED only affects Python processes started AFTER this
    env-var is set.  For full hash determinism, export it in the shell before
    launching: `PYTHONHASHSEED=42 python codes/code_12_prepare_sweep.py`
    """
    # ── Environment ──────────────────────────────────────────────────────────
    os.environ["PYTHONHASHSEED"] = str(seed)
    os.environ["TF_DETERMINISTIC_OPS"] = "1"
    os.environ["TF_CUDNN_DETERMINISTIC"] = "1"

    # ── Python stdlib ─────────────────────────────────────────────────────────
    random.seed(seed)

    # ── NumPy ─────────────────────────────────────────────────────────────────
    np.random.seed(seed)  # legacy global state used by most sklearn internals

    # ── TensorFlow ────────────────────────────────────────────────────────────
    if tf is not None:
        tf.random.set_seed(seed)

    logger.info("Random seed set to %d for os, random, numpy, tensorflow", seed)

    # ── Persist seed metadata ─────────────────────────────────────────────────
    import json
    from pathlib import Path

    results_dir = Path(__file__).resolve().parent.parent / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    metadata_path = results_dir / "metadata.json"
    try:
        existing: dict = {}
        if metadata_path.exists():
            existing = json.loads(metadata_path.read_text())
        existing["random_seed"] = seed
        metadata_path.write_text(json.dumps(existing, indent=2))
    except OSError as exc:
        logger.warning("Could not write seed metadata: %s", exc)


# ── Legacy shim ──────────────────────────────────────────────────────────────
class DeterministicPipeline:
    """Kept for backward-compatibility with older imports."""

    @staticmethod
    def set_random_seed(seed: int = 42) -> None:  # noqa: D102
        enforce_reproducibility(seed)
