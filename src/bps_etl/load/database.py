"""Database helper scaffold."""

from __future__ import annotations

from pathlib import Path


def default_database_path(root: Path) -> Path:
    """Return default SQLite database path under ignored data/database."""
    return root / "data" / "database" / "bps_etl.sqlite"
