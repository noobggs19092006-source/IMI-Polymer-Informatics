import pandas as pd
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class SmartEncodingHandler:
    """Detect and handle file encodings intelligently."""

    STANDARD_ENCODINGS = [
        "utf-8",
        "utf-16",
        "utf-32",
        "latin-1",
        "iso-8859-1",
        "iso-8859-15",
        "cp1252",  # Windows
        "gb2312",
        "gbk",  # Chinese
        "shift_jis",  # Japanese
    ]

    @staticmethod
    def detect_encoding(file_path: str, sample_size: int = 10000) -> Optional[str]:
        """Detect file encoding using chardet."""
        try:
            import chardet
        except ImportError:
            logger.warning("chardet not installed. Encoding detection disabled.")
            return None

        try:
            with open(file_path, "rb") as f:
                raw_data = f.read(sample_size)

            detection = chardet.detect(raw_data)

            if detection["encoding"] and detection["confidence"] > 0.7:
                logger.info(
                    f"Detected encoding: {detection['encoding']} "
                    f"(confidence: {detection['confidence']:.1%})"
                )
                return detection["encoding"]
        except Exception as e:
            logger.debug(f"Encoding detection failed: {e}")

        return None

    @classmethod
    def load_csv_with_detection(cls, filepath: str) -> pd.DataFrame:
        """Load CSV with automatic encoding detection."""
        detected = cls.detect_encoding(filepath)

        encodings_to_try = []
        if detected:
            encodings_to_try.append(detected)

        encodings_to_try.extend(cls.STANDARD_ENCODINGS)

        last_error = None
        for enc in encodings_to_try:
            try:
                df = pd.read_csv(filepath, encoding=enc)
                logger.info(f"Successfully loaded {filepath} with encoding: {enc}")
                return df
            except UnicodeDecodeError as e:
                last_error = e
                continue

        raise ValueError(
            f"Could not load {filepath} with any encoding. "
            f"Last error: {last_error}. "
            f"Tried: {encodings_to_try}"
        )


class SafeFileWriter:
    """Write files with explicit encoding handling."""

    DEFAULT_ENCODING = "utf-8"

    @classmethod
    def write_csv(cls, df: pd.DataFrame, output_path: str, encoding: str = DEFAULT_ENCODING):
        """Write DataFrame to CSV with explicit encoding."""
        try:
            df.to_csv(output_path, encoding=encoding, index=False)
            logger.info(f"Wrote CSV to {output_path} (encoding: {encoding})")
        except UnicodeEncodeError as e:
            logger.error(f"Encoding error writing {output_path}: {e}")
            logger.warning("Falling back to latin-1 encoding")
            df.to_csv(output_path, encoding="latin-1", index=False)

    @classmethod
    def write_json(cls, data: dict, output_path: str, encoding: str = DEFAULT_ENCODING):
        """Write dict to JSON with explicit encoding."""
        with open(output_path, "w", encoding=encoding) as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Wrote JSON to {output_path} (encoding: {encoding})")
