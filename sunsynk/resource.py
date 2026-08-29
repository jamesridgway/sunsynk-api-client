from typing import Any


def to_float(value: Any) -> float | None:
    """Convert an API value to a float.

    The Sunsynk API returns many numbers as strings. Values that are missing
    or cannot be converted return None.
    """
    if value is None or value == '':
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def to_int(value: Any) -> int | None:
    """Convert an API value to an int. Values that are missing return None."""
    if value is None or value == '':
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


class Resource:
    def __repr__(self):
        attrs = " ".join(f"{k}={v}" for k, v in self.__dict__.items())
        return f"<{self.__class__.__name__} @{id(self) & 0xFFFFFF} {attrs}>"
