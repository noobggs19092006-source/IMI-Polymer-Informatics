"""
transformers.py — Scikit-learn compatible custom transformers.

Extracted from config.py (P2 Code Hygiene) so sklearn transformers are in a
dedicated module and config.py can remain a pure configuration file.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class CollinearityDropper(BaseEstimator, TransformerMixin):
    """
    Safely calculates and drops extremely highly correlated features natively
    within an sklearn Pipeline, fitted strictly upon X_train space.

    Attributes:
        threshold: Pearson |r| above which the second feature in a correlated
            pair is dropped.
        drop_columns_: Column indices identified at fit-time (set during fit()).
    """

    def __init__(self, threshold: float = 0.95) -> None:
        self.threshold = threshold
        self.drop_columns_: list[int] = []

    def fit(self, X, y=None) -> "CollinearityDropper":
        df = pd.DataFrame(X)
        corr_matrix = df.corr().abs().fillna(0)
        upper = corr_matrix.where(
            np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)
        )
        self.drop_columns_ = [
            column for column in upper.columns if any(upper[column] > self.threshold)
        ]
        return self

    def transform(self, X, y=None) -> np.ndarray:
        df = pd.DataFrame(X)
        df_dropped = df.drop(columns=self.drop_columns_)
        return df_dropped.values
