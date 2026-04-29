"""Validation helpers scaffold."""

from __future__ import annotations


def is_valid_year(year: int | str) -> bool:
    """Validate a practical socioeconomic data year range."""
    try:
        y = int(year)
    except (TypeError, ValueError):
        return False
    return 1990 <= y <= 2035
