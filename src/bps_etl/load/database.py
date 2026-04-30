"""SQLite database initialization and Fase 5 load pipeline."""

from __future__ import annotations

import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
import subprocess
import uuid
from typing import Any, Iterable

from bps_etl.config import RESULTS_DIR
from bps_etl.load.models import TARGET_TABLES, load_schema_sql

DEFAULT_DATABASE_PATH = Path("data") / "database" / "bps_etl.sqlite"
DEFAULT_TRANSFORM_DIR = RESULTS_DIR / "tables" / "transform"
DEFAULT_EXTRACT_MANIFEST_PATH = RESULTS_DIR / "api" / "extract" / "extract_manifest.json"
DEFAULT_LOAD_METRICS_PATH = RESULTS_DIR / "database" / "load_metrics.json"

DIMENSION_INSERTS: dict[str, tuple[str, str]] = {
    "dim_indikator": (
        "var_id, indicator_key, nama_indikator, unit, subject, theme, definisi, catatan, decimal_places, source_model",
        "excluded.indicator_key, excluded.nama_indikator, excluded.unit, excluded.subject, excluded.theme, excluded.definisi, excluded.catatan, excluded.decimal_places, excluded.source_model, CURRENT_TIMESTAMP",
    ),
    "dim_wilayah": (
        "kode_wilayah, nama_wilayah, level_wilayah, group_ver_id, group_ver_name, source_model",
        "excluded.nama_wilayah, excluded.level_wilayah, excluded.group_ver_id, excluded.group_ver_name, excluded.source_model, CURRENT_TIMESTAMP",
    ),
    "dim_waktu": (
        "th_id, tahun, periode_label, source_model",
        "excluded.tahun, excluded.periode_label, excluded.source_model, CURRENT_TIMESTAMP",
    ),
    "dim_turvar": (
        "turvar_id, turvar_label, group_turvar_id, group_turvar_name, source_model",
        "excluded.turvar_label, excluded.group_turvar_id, excluded.group_turvar_name, excluded.source_model, CURRENT_TIMESTAMP",
    ),
    "dim_turtahun": (
        "turth_id, turth_label, group_turth_id, group_turth_name, source_model",
        "excluded.turth_label, excluded.group_turth_id, excluded.group_turth_name, excluded.source_model, CURRENT_TIMESTAMP",
    ),
}

DIMENSION_UPDATE_COLUMNS: dict[str, tuple[str, ...]] = {
    "dim_indikator": ("indicator_key", "nama_indikator", "unit", "subject", "theme", "definisi", "catatan", "decimal_places", "source_model"),
    "dim_wilayah": ("nama_wilayah", "level_wilayah", "group_ver_id", "group_ver_name", "source_model"),
    "dim_waktu": ("tahun", "periode_label", "source_model"),
    "dim_turvar": ("turvar_label", "group_turvar_id", "group_turvar_name", "source_model"),
    "dim_turtahun": ("turth_label", "group_turth_id", "group_turth_name", "source_model"),
}

DIMENSION_PK: dict[str, str] = {
    "dim_indikator": "var_id",
    "dim_wilayah": "kode_wilayah",
    "dim_waktu": "th_id",
    "dim_turvar": "turvar_id",
    "dim_turtahun": "turth_id",
}

FACT_COLUMNS = (
    "indicator_key",
    "var_id",
    "kode_wilayah",
    "th_id",
    "turvar_id",
    "turth_id",
    "data_key",
    "source_domain",
    "nilai",
    "last_update",
    "run_id",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def default_database_path(root: Path) -> Path:
    """Return default SQLite database path under ignored data/database."""
    return root / DEFAULT_DATABASE_PATH


def initialize_database(database_path: Path) -> None:
    """Create the SQLite database and all Fase 2 schema tables."""
    database_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(database_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.executescript(load_schema_sql())
        conn.commit()
    finally:
        conn.close()


def connect_database(database_path: Path) -> sqlite3.Connection:
    initialize_database(database_path)
    conn = sqlite3.connect(database_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_fact_rows(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _none_if_empty(value: Any) -> Any:
    if value == "":
        return None
    return value


def _int_or_none(value: Any) -> int | None:
    value = _none_if_empty(value)
    if value is None:
        return None
    return int(value)


def _float_or_none(value: Any) -> float | None:
    value = _none_if_empty(value)
    if value is None:
        return None
    return float(value)


def _insert_dimensions(conn: sqlite3.Connection, dimensions: dict[str, list[dict[str, Any]]]) -> None:
    for table, rows in dimensions.items():
        if table not in DIMENSION_INSERTS:
            continue
        column_text, _unused = DIMENSION_INSERTS[table]
        columns = tuple(part.strip() for part in column_text.split(","))
        placeholders = ", ".join("?" for _ in columns)
        update_columns = DIMENSION_UPDATE_COLUMNS[table]
        updates = ", ".join(f"{column}=excluded.{column}" for column in update_columns) + ", updated_at=CURRENT_TIMESTAMP"
        pk = DIMENSION_PK[table]
        sql = f"""
            INSERT INTO {table} ({', '.join(columns)})
            VALUES ({placeholders})
            ON CONFLICT({pk}) DO UPDATE SET {updates}
        """
        for row in rows:
            values: list[Any] = []
            for column in columns:
                value = row.get(column)
                if column in {"var_id", "th_id", "tahun", "decimal_places"}:
                    value = _int_or_none(value)
                else:
                    value = _none_if_empty(value)
                values.append(value)
            conn.execute(sql, values)


def _insert_fact_rows(conn: sqlite3.Connection, rows: list[dict[str, Any]], run_id: str) -> None:
    placeholders = ", ".join("?" for _ in FACT_COLUMNS)
    updates = ", ".join(
        f"{column}=excluded.{column}"
        for column in ("indicator_key", "data_key", "nilai", "last_update", "run_id")
    ) + ", loaded_at=CURRENT_TIMESTAMP"
    sql = f"""
        INSERT INTO fact_statistik ({', '.join(FACT_COLUMNS)})
        VALUES ({placeholders})
        ON CONFLICT(var_id, kode_wilayah, th_id, turvar_id, turth_id, source_domain)
        DO UPDATE SET {updates}
    """
    for row in rows:
        conn.execute(
            sql,
            (
                row["indicator_key"],
                int(row["var_id"]),
                row["kode_wilayah"],
                int(row["th_id"]),
                row["turvar_id"],
                row["turth_id"],
                row["data_key"],
                row.get("source_domain") or "0000",
                float(row["nilai"]),
                _none_if_empty(row.get("last_update")),
                run_id,
            ),
        )


def _extract_var_th(snapshot: dict[str, Any]) -> tuple[int | None, int | None]:
    params = snapshot.get("params") or {}
    var_id = _int_or_none(params.get("var")) if "var" in params else None
    th_id = _int_or_none(params.get("th")) if "th" in params else None
    return var_id, th_id


def _snapshot_display_path(snapshot: dict[str, Any]) -> str:
    group = snapshot.get("artifact_group")
    artifact_path = str(snapshot.get("artifact_path") or "")
    if group and not artifact_path.startswith(str(group) + "/"):
        return f"results/api/extract/{group}/{artifact_path}"
    return artifact_path


def _insert_raw_snapshots(conn: sqlite3.Connection, snapshots: Iterable[dict[str, Any]], run_id: str) -> int:
    sql = """
        INSERT INTO raw_api_snapshot
            (snapshot_id, model, var_id, th_id, source_domain, artifact_path, artifact_sha256, row_count, captured_at, run_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(snapshot_id) DO UPDATE SET
            model=excluded.model,
            var_id=excluded.var_id,
            th_id=excluded.th_id,
            source_domain=excluded.source_domain,
            artifact_path=excluded.artifact_path,
            artifact_sha256=excluded.artifact_sha256,
            row_count=excluded.row_count,
            captured_at=excluded.captured_at,
            run_id=excluded.run_id
    """
    count = 0
    for snapshot in snapshots:
        var_id, th_id = _extract_var_th(snapshot)
        conn.execute(
            sql,
            (
                snapshot["snapshot_id"],
                snapshot["model"],
                var_id,
                th_id,
                snapshot.get("domain") or "0000",
                _snapshot_display_path(snapshot),
                snapshot.get("artifact_sha256"),
                int(snapshot.get("row_count") or 0),
                snapshot.get("captured_at") or utc_now(),
                run_id,
            ),
        )
        count += 1
    return count


def _table_counts(conn: sqlite3.Connection) -> dict[str, int]:
    return {table: int(conn.execute("SELECT COUNT(*) FROM " + table).fetchone()[0]) for table in TARGET_TABLES}


def _git_commit() -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
    except Exception:
        return None


def _display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(Path.cwd().resolve()))
    except ValueError:
        return str(path)


def run_load(
    *,
    database_path: Path = DEFAULT_DATABASE_PATH,
    transform_dir: Path = DEFAULT_TRANSFORM_DIR,
    extract_manifest_path: Path = DEFAULT_EXTRACT_MANIFEST_PATH,
    metrics_path: Path | None = DEFAULT_LOAD_METRICS_PATH,
    source_git_commit: str | None = None,
) -> dict[str, Any]:
    """Load Fase 4 transform outputs into SQLite with idempotent upserts."""
    transform_manifest = read_json(transform_dir / "transform_manifest.json")
    if transform_manifest.get("quality_gate") != "passed":
        raise ValueError("transform quality gate must pass before load")

    dimensions = read_json(transform_dir / "dimensions_preview.json")
    fact_rows = read_fact_rows(transform_dir / "fact_statistik_preview.csv")
    extract_manifest = read_json(extract_manifest_path)
    snapshots = list(extract_manifest.get("snapshots") or [])

    run_id = f"load-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}"
    started_at = utc_now()
    source_git_commit = source_git_commit if source_git_commit is not None else _git_commit()

    conn = connect_database(database_path)
    try:
        conn.execute(
            """
            INSERT INTO etl_run_log
                (run_id, phase, status, started_at, indicator_count, raw_snapshot_count, fact_row_count, source_git_commit)
            VALUES (?, 'load', 'started', ?, 0, 0, 0, ?)
            """,
            (run_id, started_at, source_git_commit),
        )
        _insert_dimensions(conn, dimensions)
        raw_snapshot_count = _insert_raw_snapshots(conn, snapshots, run_id)
        _insert_fact_rows(conn, fact_rows, run_id)
        table_counts = _table_counts(conn)
        conn.execute(
            """
            UPDATE etl_run_log
            SET status='success', finished_at=?, indicator_count=?, raw_snapshot_count=?, fact_row_count=?, error_message=NULL
            WHERE run_id=?
            """,
            (
                utc_now(),
                table_counts["dim_indikator"],
                raw_snapshot_count,
                table_counts["fact_statistik"],
                run_id,
            ),
        )
        conn.commit()
    except Exception as exc:
        conn.rollback()
        raise
    finally:
        conn.close()

    summary = {
        "status": "success",
        "phase": "5 — Load Layer",
        "run_id": run_id,
        "started_at": started_at,
        "finished_at": utc_now(),
        "database_path": _display_path(database_path),
        "source_transform_manifest": _display_path(transform_dir / "transform_manifest.json"),
        "source_extract_manifest": _display_path(extract_manifest_path),
        "source_git_commit": source_git_commit,
        "indicator_count": table_counts["dim_indikator"],
        "raw_snapshot_count": raw_snapshot_count,
        "fact_row_count": table_counts["fact_statistik"],
        "table_counts": table_counts,
        "idempotent_keys": {
            "fact_statistik": "var_id + kode_wilayah + th_id + turvar_id + turth_id + source_domain",
            "raw_api_snapshot": "snapshot_id",
        },
    }
    if metrics_path is not None:
        write_json(metrics_path, summary)
    return summary
