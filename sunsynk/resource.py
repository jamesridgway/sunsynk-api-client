import datetime
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


def to_bool(value: Any) -> bool | None:
    """Convert an API value to a bool.

    The settings endpoint returns booleans as ``true``/``false``, ``"true"``/``"false"``
    or ``"1"``/``"0"``. Values that are missing return None.
    """
    if value is None or value == '':
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    text = str(value).strip().lower()
    if text in ('true', '1', 'on', 'yes'):
        return True
    if text in ('false', '0', 'off', 'no'):
        return False
    return None


def to_datetime(value: Any) -> datetime.datetime | None:
    """Convert an API timestamp to a timezone-aware datetime.

    Handles the ``2023-01-07T16:50:17Z`` and ``2023-01-07 16:50:17`` forms
    used by the API, with or without fractional seconds or a UTC offset.
    Timestamps without an offset are treated as UTC. Values that are missing or
    cannot be parsed return None.
    """
    if value is None or value == '':
        return None
    if isinstance(value, datetime.datetime):
        return value if value.tzinfo else value.replace(tzinfo=datetime.timezone.utc)
    try:
        parsed = datetime.datetime.fromisoformat(str(value))
    except (TypeError, ValueError):
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=datetime.timezone.utc)
    return parsed


class Resource:
    def __repr__(self):
        attrs = " ".join(f"{k}={v}" for k, v in self.__dict__.items())
        return f"<{self.__class__.__name__} @{id(self) & 0xFFFFFF} {attrs}>"
