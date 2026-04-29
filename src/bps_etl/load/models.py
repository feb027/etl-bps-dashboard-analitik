"""Database schema metadata for ETL BPS project."""

from __future__ import annotations

from pathlib import Path

TARGET_TABLES = (
    "dim_indikator",
    "dim_wilayah",
    "dim_waktu",
    "dim_turvar",
    "dim_turtahun",
    "fact_statistik",
    "raw_api_snapshot",
    "etl_run_log",
)

DIMENSION_TABLES = (
    "dim_indikator",
    "dim_wilayah",
    "dim_waktu",
    "dim_turvar",
    "dim_turtahun",
)

FACT_TABLES = ("fact_statistik",)
AUDIT_TABLES = ("raw_api_snapshot", "etl_run_log")

FACT_UNIQUE_GRAIN = (
    "var_id",
    "kode_wilayah",
    "th_id",
    "turvar_id",
    "turth_id",
    "source_domain",
)


def schema_path() -> Path:
    """Return the SQLite DDL path."""
    return Path(__file__).with_name("schema.sql")


def load_schema_sql() -> str:
    """Read SQLite schema SQL."""
    return schema_path().read_text(encoding="utf-8")
