import pandas as pd
import logging
from typing import Generator, Tuple, Any

logger = logging.getLogger(__name__)


def safe_iterate_dataframe(df: pd.DataFrame) -> Generator[Tuple[int, pd.Series], None, None]:
    """
    Safely iterate over a pandas DataFrame without bounds errors or skipped samples.
    """
    expected_length = len(df)
    if expected_length == 0:
        logger.warning("Attempted to iterate over an empty DataFrame.")
        return

    logger.info(f"Starting safe iteration over {expected_length} samples.")

    count = 0
    for idx, row in df.iterrows():
        yield idx, row
        count += 1

    if count != expected_length:
        logger.error(
            f"Iteration completeness assertion failed! Expected {expected_length}, got {count}"
        )
        raise RuntimeError(f"Dataframe iteration incomplete. {expected_length} vs {count}")

    logger.info("Iteration completed successfully without skipped elements.")
