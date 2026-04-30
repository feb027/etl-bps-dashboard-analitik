from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from bps_etl.load.database import initialize_database, run_load
from bps_etl.load.models import TARGET_TABLES
from scripts.run_etl import build_parser


ROOT = Path(__file__).resolve().parents[1]
TRANSFORM_DIR = ROOT / "results" / "tables" / "transform"
EXTRACT_MANIFEST = ROOT / "results" / "api" / "extract" / "extract_manifest.json"


def table_counts(db_path: Path) -> dict[str, int]:
    conn = sqlite3.connect(db_path)
    try:
        return {table: conn.execute("SELECT COUNT(*) FROM " + table).fetchone()[0] for table in TARGET_TABLES}
    finally:
        conn.close()


def test_initialize_database_creates_expected_tables(tmp_path: Path):
    db_path = tmp_path / "bps.sqlite"

    initialize_database(db_path)

    conn = sqlite3.connect(db_path)
    try:
        tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    finally:
        conn.close()

    assert set(TARGET_TABLES).issubset(tables)


def test_run_load_populates_sqlite_tables_and_run_log(tmp_path: Path):
    db_path = tmp_path / "bps.sqlite"

    summary = run_load(
        database_path=db_path,
        transform_dir=TRANSFORM_DIR,
        extract_manifest_path=EXTRACT_MANIFEST,
        metrics_path=None,
        source_git_commit="test-commit",
    )

    counts = table_counts(db_path)
    assert summary["status"] == "success"
    assert summary["phase"] == "5 — Load Layer"
    assert summary["database_path"].endswith("bps.sqlite")
    assert summary["fact_row_count"] == 2490
    assert summary["raw_snapshot_count"] == 32
    assert summary["table_counts"]["fact_statistik"] == 2490
    assert counts["dim_indikator"] == 4
    assert counts["dim_wilayah"] == 553
    assert counts["dim_waktu"] == 3
    assert counts["dim_turvar"] == 4
    assert counts["dim_turtahun"] == 5
    assert counts["fact_statistik"] == 2490
    assert counts["raw_api_snapshot"] == 32
    assert counts["etl_run_log"] == 1

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute("SELECT status, fact_row_count, raw_snapshot_count, source_git_commit FROM etl_run_log").fetchone()
        assert dict(row) == {
            "status": "success",
            "fact_row_count": 2490,
            "raw_snapshot_count": 32,
            "source_git_commit": "test-commit",
        }
        sample = conn.execute(
            "SELECT indicator_key, tahun, nama_wilayah, nilai FROM fact_statistik "
            "JOIN dim_waktu USING (th_id) JOIN dim_wilayah USING (kode_wilayah) "
            "WHERE indicator_key='poverty_rate' AND tahun=2023 ORDER BY kode_wilayah LIMIT 1"
        ).fetchone()
        assert sample["indicator_key"] == "poverty_rate"
        assert sample["tahun"] == 2023
        assert sample["nama_wilayah"]
        assert sample["nilai"] > 0
    finally:
        conn.close()


def test_run_load_is_idempotent_for_fact_and_dimension_tables(tmp_path: Path):
    db_path = tmp_path / "bps.sqlite"

    first = run_load(database_path=db_path, transform_dir=TRANSFORM_DIR, extract_manifest_path=EXTRACT_MANIFEST, metrics_path=None)
    second = run_load(database_path=db_path, transform_dir=TRANSFORM_DIR, extract_manifest_path=EXTRACT_MANIFEST, metrics_path=None)

    assert first["table_counts"]["fact_statistik"] == 2490
    assert second["table_counts"]["fact_statistik"] == 2490
    assert second["table_counts"]["dim_wilayah"] == 553
    assert second["table_counts"]["raw_api_snapshot"] == 32
    assert second["table_counts"]["etl_run_log"] == 2


def test_run_load_writes_commit_safe_metrics_artifact(tmp_path: Path):
    db_path = tmp_path / "bps.sqlite"
    metrics_path = tmp_path / "load_metrics.json"

    summary = run_load(
        database_path=db_path,
        transform_dir=TRANSFORM_DIR,
        extract_manifest_path=EXTRACT_MANIFEST,
        metrics_path=metrics_path,
    )

    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    assert metrics["status"] == "success"
    assert metrics["fact_row_count"] == summary["fact_row_count"] == 2490
    assert metrics["table_counts"]["fact_statistik"] == 2490
    assert "BPS_API_KEY" not in json.dumps(metrics)


def test_run_etl_parser_supports_load_phase_and_database_path():
    args = build_parser().parse_args(["--phase", "load", "--database-path", "data/database/bps_etl.sqlite"])

    assert args.phase == "load"
    assert str(args.database_path).endswith("bps_etl.sqlite")
