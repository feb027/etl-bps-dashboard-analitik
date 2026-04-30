from __future__ import annotations

from pathlib import Path

import pytest

from bps_etl.load.database import run_load
from scripts.generate_dashboard_data import DashboardDataError, build_dashboard_data

ROOT = Path(__file__).resolve().parents[1]
TRANSFORM_DIR = ROOT / "results" / "tables" / "transform"
EXTRACT_MANIFEST = ROOT / "results" / "api" / "extract" / "extract_manifest.json"
LOAD_METRICS = ROOT / "results" / "database" / "load_metrics.json"


def populated_database(tmp_path: Path) -> Path:
    db_path = tmp_path / "bps.sqlite"
    run_load(
        database_path=db_path,
        transform_dir=TRANSFORM_DIR,
        extract_manifest_path=EXTRACT_MANIFEST,
        metrics_path=None,
        source_git_commit="dashboard-test",
    )
    return db_path


def test_generator_fails_loudly_when_database_is_missing(tmp_path: Path):
    missing_db = tmp_path / "missing.sqlite"

    with pytest.raises(DashboardDataError, match="python3 scripts/run_etl.py --phase load --mode quick"):
        build_dashboard_data(database_path=missing_db, template_path=tmp_path / "dashboard-data.json")


def test_generator_builds_chart_rankings_table_from_sqlite(tmp_path: Path):
    db_path = populated_database(tmp_path)

    data = build_dashboard_data(
        database_path=db_path,
        template_path=tmp_path / "dashboard-data.json",
        load_metrics_path=LOAD_METRICS,
    )

    assert data["project"]["current_phase"] == "6 — Dashboard"
    assert data["quality"]["no_dummy_data"] is True
    assert data["summary"]["indicator_count"] == 4
    assert data["summary"]["region_count"] == 553
    assert data["summary"]["year_count"] == 3
    assert data["summary"]["record_count"] == 2490
    assert data["summary"]["last_etl_run"].startswith("load-")
    assert data["evidence"]["db_counts"]["fact_statistik"] == 2490
    assert data["evidence"]["db_counts"]["dim_wilayah"] == 553
    assert len(data["series"]["trend"]) == 4
    assert all(series["points"] for series in data["series"]["trend"])
    assert data["rankings"]["top"]
    assert data["rankings"]["bottom"]
    assert data["rankings"]["change"]
    assert data["rankings"]["top"][0]["rows"][0]["value"] is not None
    assert len(data["table_rows"]) == 2490
    assert data["table_rows"][0]["data_key"]
    assert data["narrative_seed"]["by_indicator"]
    assert data["design_metrics"]["dashboard_table_rows"] == 2490
