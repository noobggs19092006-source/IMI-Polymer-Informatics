from typing import Union, Optional, Any
from datetime import datetime
from decimal import Decimal
from pathlib import Path


class ExtendedTypeConverter:
    """Convert values to target types with comprehensive support."""

    CONVERTERS = {
        float: lambda x: float(x),
        int: lambda x: int(float(x)),  # Handles "3.0" -> 3
        str: lambda x: str(x),
        bool: lambda x: x.lower() in ["true", "1", "yes"] if isinstance(x, str) else bool(x),
        datetime: lambda x: datetime.fromisoformat(x) if isinstance(x, str) else x,
        Decimal: lambda x: Decimal(str(x)),  # Always convert via string for precision
        Path: lambda x: Path(x),
        list: lambda x: x if isinstance(x, list) else [x],
        dict: lambda x: x if isinstance(x, dict) else {},
    }

    @classmethod
    def convert(cls, value: Any, target_type: type) -> Any:
        """Convert value to target type."""
        if type(value) == target_type:
            return value

        if value is None:
            if target_type in [list, dict]:
                return target_type()
            return None

        if target_type not in cls.CONVERTERS:
            raise TypeError(f"No converter for type {target_type}")

        try:
            return cls.CONVERTERS[target_type](value)
        except (ValueError, TypeError) as e:
            raise ValueError(
                f"Cannot convert {value} ({type(value).__name__}) to {target_type.__name__}: {e}"
            )

    @classmethod
    def validate_type(cls, value: Any, expected_type: type, allow_none: bool = False) -> bool:
        """Check if value matches expected type."""
        if value is None:
            return allow_none
        return isinstance(value, expected_type)


def process_numeric_value(val: Union[int, float]) -> float:
    """Process numeric values (int or float)."""
    if not isinstance(val, (int, float)):
        raise TypeError(f"Expected int or float, got {type(val).__name__}")
    return float(val)


def process_optional_string(val: Optional[str]) -> str:
    """Process optional string value."""
    if val is None:
        return ""
    if not isinstance(val, str):
        raise TypeError(f"Expected str or None, got {type(val).__name__}")
    return val.strip()
