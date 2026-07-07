import pandas as pd
import numpy as np
import logging
from typing import Tuple, Dict


logger = logging.getLogger(__name__)


def _is_type_compatible(actual: np.dtype, expected: type) -> bool:
    """Check if actual type matches expected."""
    type_mapping = {
        float: [np.float64, np.float32, np.float16],
        int: [np.int64, np.int32, np.int16],
        str: [np.object_, "object"],
        bool: [np.bool_],
    }
    return actual in type_mapping.get(expected, [])


def validate_data_integrity(
    df: pd.DataFrame,
    drop_nulls: bool = True,
    null_threshold: float = 0.05,
    schema: Dict[str, type] = None,
) -> Tuple[bool, pd.DataFrame]:
    """
    Validates a DataFrame for nulls, infinite values, and optional type schema.
    Returns (is_valid, cleaned_df).
    """
    if df.empty:
        logger.warning("DataFrame is empty.")
        return False, df

    if schema:
        type_issues = False
        for col, expected_type in schema.items():
            if col not in df.columns:
                logger.warning(f"Missing column: {col}")
                type_issues = True
                continue

            actual_type = df[col].dtype
            if not _is_type_compatible(actual_type, expected_type):
                logger.warning(
                    f"Type mismatch in {col}: expected {expected_type}, got {actual_type}"
                )
                type_issues = True

        if type_issues:
            logger.warning("Type validation failed.")

    # Check for infinite values
    numeric_df = df.select_dtypes(include=[np.number])
    inf_cols = numeric_df.columns[np.isinf(numeric_df).any()]
    if not inf_cols.empty:
        logger.error(f"Infinite values found in columns: {inf_cols.tolist()}")
        # Replace inf with NaN for uniform handling
        df = df.replace([np.inf, -np.inf], np.nan)

    # Check for nulls
    null_counts = df.isnull().sum()
    null_cols = null_counts[null_counts > 0]

    if null_cols.empty:
        return True, df

    total_samples = len(df)
    logger.warning(f"Null values detected in {len(null_cols)} columns.")

    for col, count in null_cols.items():
        null_rate = count / total_samples
        logger.warning(f"  {col}: {count} nulls ({null_rate:.1%})")

        if null_rate > null_threshold:
            logger.error(f"Column {col} exceeds null threshold of {null_threshold:.1%}")

    if drop_nulls:
        initial_len = len(df)
        df_clean = df.dropna().reset_index(drop=True)
        dropped = initial_len - len(df_clean)
        logger.info(f"Dropped {dropped} rows with null/inf values.")
        return True, df_clean

    return False, df
