"""Pipeline runner scaffold."""

from __future__ import annotations


def planned_modes() -> tuple[str, str]:
    """Return supported ETL modes planned for later phases."""
    return ("quick", "full")
