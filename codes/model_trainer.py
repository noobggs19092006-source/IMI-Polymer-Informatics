import pandas as pd
from typing import Dict
import logging
from tqdm import tqdm
import joblib
from pathlib import Path

logger = logging.getLogger(__name__)


class ProgressTrackingModelTrainer:
    """Train models with progress monitoring and checkpoint save."""

    def __init__(self, model, checkpoint_dir: str = "./checkpoints"):
        self.model = model
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.last_checkpoint = None

    def train_on_dataset(self, df: pd.DataFrame, target_col: str, config: Dict) -> Dict:
        """Train model in a single batch pass (not sample-by-sample)."""
        training_log = {
            "total_samples": len(df),
            "successful_training": 0,
            "failed_training": 0,
            "errors": [],
        }

        try:
            y = df[target_col].values
            X = df.drop(columns=[target_col]).values
            self.model.fit(X, y)
            training_log["successful_training"] = len(df)
            logger.info("Batch fit completed on %d samples.", len(df))
        except Exception as e:
            logger.error("Batch fit failed: %s", e, exc_info=True)
            training_log["failed_training"] = len(df)
            training_log["errors"].append(str(e))
            failure_rate = 1.0
            if failure_rate > config.get("max_failure_rate", 0.05):
                raise RuntimeError(f"Training failed: {e}") from e

        return training_log

    def train_with_checkpoints(
        self, df: pd.DataFrame, target_col: str, checkpoint_interval: int = 100
    ) -> Dict:
        """Train in batch, saving a model checkpoint every *checkpoint_interval* samples.

        Each checkpoint is a full fit on all rows seen so far — not a
        one-sample-at-a-time online update, which was the previous bug.
        """
        training_log = {
            "total_samples": len(df),
            "checkpoints_saved": 0,
            "last_checkpoint": None,
        }

        y = df[target_col].values
        X = df.drop(columns=[target_col]).values

        for batch_end in range(checkpoint_interval, len(df) + 1, checkpoint_interval):
            X_batch = X[:batch_end]
            y_batch = y[:batch_end]
            try:
                self.model.fit(X_batch, y_batch)
            except Exception as e:
                logger.error("Batch fit failed at row %d: %s", batch_end, e)
                raise

            checkpoint_path = self._save_checkpoint(batch_end)
            training_log["checkpoints_saved"] += 1
            training_log["last_checkpoint"] = str(checkpoint_path)

        # Final fit on the full dataset if total rows not a clean multiple
        remainder = len(df) % checkpoint_interval
        if remainder:
            try:
                self.model.fit(X, y)
            except Exception as e:
                logger.error("Final batch fit failed: %s", e)
                raise
            checkpoint_path = self._save_checkpoint(len(df))
            training_log["checkpoints_saved"] += 1
            training_log["last_checkpoint"] = str(checkpoint_path)

        return training_log


    def _save_checkpoint(self, step: int) -> Path:
        """Save model checkpoint."""
        checkpoint_path = self.checkpoint_dir / f"model_step_{step}.pkl"
        joblib.dump(self.model, checkpoint_path)
        logger.info(f"Saved checkpoint: {checkpoint_path}")
        return checkpoint_path

    def load_checkpoint(self, checkpoint_path: str):
        """Load model from checkpoint."""
        self.model = joblib.load(checkpoint_path)
        logger.info(f"Loaded checkpoint: {checkpoint_path}")
