"""Normalization helpers scaffold."""

from __future__ import annotations


def normalize_numeric_value(value: object) -> float | None:
    """Convert Indonesian/standard numeric value to float, returning None if invalid."""
    if value is None:
        return None
    try:
        return float(str(value).replace(",", ".").strip())
    except ValueError:
        return None
