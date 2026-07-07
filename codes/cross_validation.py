import numpy as np
import pandas as pd
from typing import Dict, Any, List
from scipy import stats
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class MaterialClass(Enum):
    POLYMER_BLEND = "Polymer_Blend"
    ALLOY = "Alloy"
    NANOCOMPOSITE = "Nanocomposite"


class CrossValidationByMaterialClass:
    """Validate model performance across material classes with statistical testing."""

    def evaluate_per_material_class(self, df: pd.DataFrame, y_true, y_pred) -> Dict[str, Any]:
        """Calculate metrics with confidence intervals."""
        from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

        metrics_by_class = {}

        for mat_class in MaterialClass:
            mask = df["Material_Type"] == mat_class.value

            if mask.sum() < 10:  # Need minimum samples for statistics
                logger.warning(f"{mat_class.value}: Only {mask.sum()} samples, skipping")
                continue

            y_true_class = y_true[mask]
            y_pred_class = y_pred[mask]

            # Calculate metrics
            r2 = r2_score(y_true_class, y_pred_class)
            mae = mean_absolute_error(y_true_class, y_pred_class)
            rmse = np.sqrt(mean_squared_error(y_true_class, y_pred_class))

            # Calculate confidence intervals using bootstrap
            ci_r2 = self._bootstrap_ci(y_true_class, y_pred_class, r2_score, n_boot=1000)
            ci_mae = self._bootstrap_ci(
                y_true_class, y_pred_class, mean_absolute_error, n_boot=1000
            )

            metrics_by_class[mat_class.value] = {
                "sample_count": mask.sum(),
                "r2_score": r2,
                "r2_ci_lower": ci_r2[0],
                "r2_ci_upper": ci_r2[1],
                "mae": mae,
                "mae_ci_lower": ci_mae[0],
                "mae_ci_upper": ci_mae[1],
                "rmse": rmse,
                "mean_target": float(y_true_class.mean()),
                "std_target": float(y_true_class.std()),
            }

        return metrics_by_class

    @staticmethod
    def _bootstrap_ci(y_true, y_pred, metric_func, n_boot: int = 1000, ci: float = 0.95):
        """Calculate bootstrap confidence interval for metric."""
        bootstrap_scores = []
        n_samples = len(y_true)

        y_true_np = np.array(y_true)
        y_pred_np = np.array(y_pred)

        rng = np.random.RandomState(42)
        for _ in range(n_boot):
            indices = rng.choice(n_samples, n_samples, replace=True)
            score = metric_func(y_true_np[indices], y_pred_np[indices])
            bootstrap_scores.append(score)

        alpha = 1 - ci
        lower = np.percentile(bootstrap_scores, alpha / 2 * 100)
        upper = np.percentile(bootstrap_scores, (1 - alpha / 2) * 100)

        return lower, upper

    def test_performance_differences(self, metrics_dict: Dict) -> Dict:
        """Test if performance significantly differs across material classes."""
        # Extract R² scores for each class
        r2_scores = {mat_class: metrics["r2_score"] for mat_class, metrics in metrics_dict.items()}

        if len(r2_scores) < 2:
            logger.warning("Need >=2 material classes for significance testing")
            return {}

        # One-way ANOVA
        scores_list = list(r2_scores.values())
        f_stat, p_value = stats.f_oneway(*[[s] for s in scores_list])

        return {
            "f_statistic": f_stat,
            "p_value": p_value,
            "significant_difference": p_value < 0.05,
            "interpretation": (
                "Performance differs significantly across material classes"
                if p_value < 0.05
                else "No significant performance difference across material classes"
            ),
        }

    def analyze_prediction_errors(self, df: pd.DataFrame, y_true, y_pred) -> Dict[str, Any]:
        """Analyze prediction errors by material class and other features."""
        y_true_np = np.array(y_true)
        y_pred_np = np.array(y_pred)
        errors = np.abs(y_true_np - y_pred_np)

        error_analysis = {}

        for mat_class in MaterialClass:
            mask = df["Material_Type"] == mat_class.value
            class_errors = errors[mask]

            if len(class_errors) == 0:
                continue

            worst_indices = np.argsort(class_errors)[-5:]  # Top 5 worst

            worst_samples = []
            for idx in worst_indices:
                sample_idx = df[mask].index[idx]
                actual_val = y_true_np[mask][idx]
                predicted_val = y_pred_np[mask][idx]
                err_val = class_errors[idx]
                worst_samples.append(
                    {
                        "sample_id": df.loc[sample_idx, "sample_id"]
                        if "sample_id" in df.columns
                        else sample_idx,
                        "actual": actual_val,
                        "predicted": predicted_val,
                        "error": err_val,
                        "error_percent": (err_val / actual_val * 100)
                        if actual_val != 0
                        else np.inf,
                    }
                )

            error_analysis[mat_class.value] = {
                "mean_error": class_errors.mean(),
                "median_error": np.median(class_errors),
                "std_error": class_errors.std(),
                "max_error": class_errors.max(),
                "percentile_95": np.percentile(class_errors, 95),
                "worst_predictions": worst_samples,
            }

        return error_analysis
