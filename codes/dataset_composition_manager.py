import pandas as pd
import numpy as np
from enum import Enum
from typing import Dict
import os
import json


class MaterialClass(Enum):
    """Explicitly define material classes."""

    PURE_POLYMER = "pure_polymer"
    POLYMER_ALLOY = "polymer_alloy"
    NANOCOMPOSITE = "nanocomposite"
    FILLED_POLYMER = "filled_polymer"


class DatasetCompositionManager:
    """Enforce strict dataset composition controls."""

    def __init__(self, min_samples_per_class: int = 100):
        self.min_samples_per_class = min_samples_per_class

    def infer_material_class(self, row: pd.Series) -> str:
        """Infer material class from SMILES or other features if not present."""
        smiles = row.get("smiles", "")
        if not isinstance(smiles, str):
            return MaterialClass.PURE_POLYMER.value

        # Basic heuristic: if it contains metals or typical nanoparticle elements, or specific alloy patterns
        # For this pipeline, assuming we can infer or default to pure polymer
        # This should be replaced with actual domain logic.
        if "Si" in smiles or "Ti" in smiles or "Al" in smiles:
            return MaterialClass.NANOCOMPOSITE.value
        elif "." in smiles:
            return MaterialClass.POLYMER_ALLOY.value
        return MaterialClass.PURE_POLYMER.value

    def verify_material_stratification(self, df: pd.DataFrame) -> Dict:
        """Analyze stratification of material classes."""
        if "material_class" not in df.columns:
            df["material_class"] = df.apply(self.infer_material_class, axis=1)

        composition = df["material_class"].value_counts()

        analysis = {
            "total_samples": len(df),
            "material_classes": composition.to_dict(),
            "proportions": (composition / len(df)).to_dict(),
            "representation": {},
        }

        for mat_class, count in composition.items():
            if count < self.min_samples_per_class:
                analysis["representation"][
                    mat_class
                ] = f"UNDERREPRESENTED ({count} < {self.min_samples_per_class})"
            else:
                analysis["representation"][mat_class] = "OK"

        return analysis

    def split_by_material_class(self, df: pd.DataFrame, test_size: float = 0.2):
        """Stratified split maintaining material class distribution."""
        from sklearn.model_selection import StratifiedShuffleSplit

        if "material_class" not in df.columns:
            df["material_class"] = df.apply(self.infer_material_class, axis=1)

        # Filter out classes with too few samples to split
        class_counts = df["material_class"].value_counts()
        valid_classes = class_counts[class_counts > 10].index
        df_valid = df[df["material_class"].isin(valid_classes)]

        sss = StratifiedShuffleSplit(n_splits=1, test_size=test_size, random_state=42)
        X = df_valid.drop("material_class", axis=1)
        y = df_valid["material_class"]

        for train_idx, test_idx in sss.split(X, y):
            train_df = df_valid.iloc[train_idx].copy()
            test_df = df_valid.iloc[test_idx].copy()
            return train_df, test_df

        # Fallback if split fails — seeded for reproducibility
        return df_valid.sample(frac=1 - test_size, random_state=42), df_valid.sample(frac=test_size, random_state=42)

    def generate_composition_report(self, df: pd.DataFrame, output_file: str):
        analysis = self.verify_material_stratification(df)
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        with open(output_file, "w") as f:
            f.write("DATASET COMPOSITION REPORT\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"Total Samples: {analysis['total_samples']}\n")
            f.write(f"Material Classes: {len(analysis['material_classes'])}\n\n")

            f.write("Breakdown:\n")
            f.write("-" * 70 + "\n")
            for mat_class, count in analysis["material_classes"].items():
                pct = analysis["proportions"][mat_class] * 100
                f.write(f"{mat_class:.<40} {count:>6} ({pct:>5.1f}%)\n")

            f.write("\n" + "-" * 70 + "\n")
            f.write("VALIDATION REQUIREMENTS:\n")

            for mat_class, status in analysis["representation"].items():
                f.write(f"  {mat_class:.<40} {status}\n")


class CrossValidationByMaterialClass:
    """Validate model performance across material classes."""

    @staticmethod
    def evaluate_per_material_class(df: pd.DataFrame, y_true, y_pred) -> Dict:
        from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

        metrics_by_class = {}

        classes = df["material_class"].unique()
        for mat_class in classes:
            mask = (df["material_class"] == mat_class).values
            if mask.sum() < 2:
                continue

            y_true_class = y_true[mask]
            y_pred_class = y_pred[mask]

            metrics_by_class[mat_class] = {
                "sample_count": int(mask.sum()),
                "r2_score": float(r2_score(y_true_class, y_pred_class)),
                "mae": float(mean_absolute_error(y_true_class, y_pred_class)),
                "rmse": float(np.sqrt(mean_squared_error(y_true_class, y_pred_class))),
            }

        return metrics_by_class
