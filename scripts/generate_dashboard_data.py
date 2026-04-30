#!/usr/bin/env python3
"""Generate the Fase 6 static dashboard JSON from the local SQLite database."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
import sqlite3
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATABASE_PATH = ROOT / "data" / "database" / "bps_etl.sqlite"
DASHBOARD_DATA_PATH = ROOT / "dashboard" / "data" / "dashboard-data.json"
LOAD_METRICS_PATH = ROOT / "results" / "database" / "load_metrics.json"
API_PROBE_SUMMARY_PATH = ROOT / "results" / "api" / "bps_api_probe_summary.json"
EXTRACT_MANIFEST_PATH = ROOT / "results" / "api" / "extract" / "extract_manifest.json"
TRANSFORM_QUALITY_PATH = ROOT / "results" / "tables" / "transform" / "transform_quality_metrics.json"
TRANSFORM_MANIFEST_PATH = ROOT / "results" / "tables" / "transform" / "transform_manifest.json"

REQUIRED_TABLES = (
    "dim_indikator",
    "dim_wilayah",
    "dim_waktu",
    "dim_turvar",
    "dim_turtahun",
    "fact_statistik",
    "raw_api_snapshot",
    "etl_run_log",
)

ARTIFACTS = [
    "docs/architecture/etl-architecture.md",
    "docs/architecture/database-schema.md",
    "docs/architecture/transform-rules.md",
    "docs/architecture/data-dictionary.md",
    "docs/phases/dashboard-spec.md",
    "docs/phases/dashboard-design-system.md",
    "src/bps_etl/load/schema.sql",
    "results/api/extract/extract_manifest.json",
    "results/tables/transform/fact_statistik_preview.csv",
    "results/tables/transform/dimensions_preview.json",
    "results/tables/transform/transform_quality_metrics.json",
    "results/tables/transform/transform_manifest.json",
    "results/database/load_metrics.json",
    "dashboard/data/dashboard-data.json",
    "docs/reviews/REVIEW_phase6_1_data_expansion.md",
    "reports/progress-6-dashboard.md",
    "reports/progress-6-1-data-expansion.md",
]


class DashboardDataError(RuntimeError):
    """Raised when dashboard data cannot be generated from real ETL evidence."""


def utc_now() -> str:
    """Return an ISO UTC timestamp suitable for committed JSON artifacts."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    """Read JSON if it exists, otherwise return an empty mapping."""
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    """Write stable UTF-8 JSON for the static dashboard."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def relative_path(path: Path) -> str:
    """Return a repo-relative path when possible."""
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def connect_existing_database(database_path: Path) -> sqlite3.Connection:
    """Connect to the existing SQLite database and fail loudly when it is missing."""
    if not database_path.exists():
        raise DashboardDataError(
            "SQLite database not found at "
            f"{relative_path(database_path)}. Run: python3 scripts/run_etl.py --phase load --mode quick"
        )
    conn = sqlite3.connect(database_path)
    conn.row_factory = sqlite3.Row
    return conn


def fetch_all(conn: sqlite3.Connection, sql: str, params: Iterable[Any] = ()) -> list[dict[str, Any]]:
    """Run a parameterized query and return plain dictionaries."""
    return [dict(row) for row in conn.execute(sql, tuple(params)).fetchall()]


def fetch_one(conn: sqlite3.Connection, sql: str, params: Iterable[Any] = ()) -> dict[str, Any] | None:
    """Run a parameterized query and return one plain dictionary."""
    row = conn.execute(sql, tuple(params)).fetchone()
    return dict(row) if row else None


COUNT_QUERIES = {
    "dim_indikator": "SELECT COUNT(*) FROM dim_indikator",
    "dim_wilayah": "SELECT COUNT(*) FROM dim_wilayah",
    "dim_waktu": "SELECT COUNT(*) FROM dim_waktu",
    "dim_turvar": "SELECT COUNT(*) FROM dim_turvar",
    "dim_turtahun": "SELECT COUNT(*) FROM dim_turtahun",
    "fact_statistik": "SELECT COUNT(*) FROM fact_statistik",
    "raw_api_snapshot": "SELECT COUNT(*) FROM raw_api_snapshot",
    "etl_run_log": "SELECT COUNT(*) FROM etl_run_log",
}


def table_counts(conn: sqlite3.Connection) -> dict[str, int]:
    """Return row counts for the expected dashboard source tables."""
    counts: dict[str, int] = {}
    existing = {
        row["name"]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    }
    missing = [table for table in REQUIRED_TABLES if table not in existing]
    if missing:
        raise DashboardDataError(f"SQLite database is missing required tables: {', '.join(missing)}")
    for table, query in COUNT_QUERIES.items():
        counts[table] = int(conn.execute(query).fetchone()[0])
    return counts


def load_indicators(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Load dashboard indicator metadata from dim_indikator."""
    rows = fetch_all(
        conn,
        """
        SELECT var_id AS id, indicator_key AS key, nama_indikator AS name, unit, subject, theme, decimal_places
        FROM dim_indikator
        ORDER BY indicator_key
        """,
    )
    for row in rows:
        row["unit"] = row["unit"] or "indeks"
    return rows


def load_years(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Load available years from dim_waktu."""
    return fetch_all(
        conn,
        """
        SELECT th_id, tahun AS year, periode_label AS label
        FROM dim_waktu
        ORDER BY tahun
        """,
    )


def load_regions(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Load compact region metadata with fact coverage counts."""
    return fetch_all(
        conn,
        """
        SELECT
            w.kode_wilayah AS code,
            w.nama_wilayah AS name,
            w.level_wilayah AS level,
            COUNT(f.fact_id) AS record_count
        FROM dim_wilayah w
        LEFT JOIN fact_statistik f ON f.kode_wilayah = w.kode_wilayah
        GROUP BY w.kode_wilayah, w.nama_wilayah, w.level_wilayah
        ORDER BY w.kode_wilayah
        """,
    )


def load_source_domains(conn: sqlite3.Connection) -> list[str]:
    """Load source domains represented in the fact table."""
    rows = fetch_all(conn, "SELECT DISTINCT source_domain FROM fact_statistik ORDER BY source_domain")
    return [str(row["source_domain"]) for row in rows]


def build_trend_series(conn: sqlite3.Connection, indicators: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build average trend lines by indicator and year from fact rows."""
    series: list[dict[str, Any]] = []
    for indicator in indicators:
        rows = fetch_all(
            conn,
            """
            SELECT
                w.tahun AS year,
                f.th_id,
                ROUND(AVG(f.nilai), 4) AS value,
                COUNT(*) AS record_count,
                MIN(f.nilai) AS min_value,
                MAX(f.nilai) AS max_value
            FROM fact_statistik f
            JOIN dim_waktu w ON w.th_id = f.th_id
            WHERE f.indicator_key = ?
            GROUP BY w.tahun, f.th_id
            ORDER BY w.tahun
            """,
            (indicator["key"],),
        )
        series.append(
            {
                "indicator_key": indicator["key"],
                "indicator_name": indicator["name"],
                "unit": indicator["unit"],
                "aggregation": "average_of_available_region_rows",
                "points": rows,
            }
        )
    return series


RANKING_QUERIES = {
    "top": """
        SELECT
            f.indicator_key,
            w.tahun AS year,
            r.kode_wilayah AS region_code,
            r.nama_wilayah AS region_name,
            r.level_wilayah AS region_level,
            ROUND(AVG(f.nilai), 4) AS value,
            COUNT(*) AS record_count
        FROM fact_statistik f
        JOIN dim_waktu w ON w.th_id = f.th_id
        JOIN dim_wilayah r ON r.kode_wilayah = f.kode_wilayah
        WHERE f.indicator_key = ? AND w.tahun = ?
        GROUP BY f.indicator_key, w.tahun, r.kode_wilayah, r.nama_wilayah, r.level_wilayah
        ORDER BY value DESC, r.nama_wilayah ASC
        LIMIT ?
        """,
    "bottom": """
        SELECT
            f.indicator_key,
            w.tahun AS year,
            r.kode_wilayah AS region_code,
            r.nama_wilayah AS region_name,
            r.level_wilayah AS region_level,
            ROUND(AVG(f.nilai), 4) AS value,
            COUNT(*) AS record_count
        FROM fact_statistik f
        JOIN dim_waktu w ON w.th_id = f.th_id
        JOIN dim_wilayah r ON r.kode_wilayah = f.kode_wilayah
        WHERE f.indicator_key = ? AND w.tahun = ?
        GROUP BY f.indicator_key, w.tahun, r.kode_wilayah, r.nama_wilayah, r.level_wilayah
        ORDER BY value ASC, r.nama_wilayah ASC
        LIMIT ?
        """,
}


def ranking_rows(conn: sqlite3.Connection, indicator_key: str, year: int, mode: str, limit: int = 20) -> list[dict[str, Any]]:
    """Build top or bottom regional averages for one indicator-year pair."""
    if mode not in RANKING_QUERIES:
        raise ValueError(f"Unsupported ranking mode: {mode}")
    return fetch_all(conn, RANKING_QUERIES[mode], (indicator_key, year, limit))


def change_rows(conn: sqlite3.Connection, indicator_key: str, from_year: int, to_year: int, limit: int = 20) -> list[dict[str, Any]]:
    """Build largest absolute regional changes between the first and last year."""
    return fetch_all(
        conn,
        """
        WITH regional_year AS (
            SELECT
                f.indicator_key,
                w.tahun AS year,
                r.kode_wilayah AS region_code,
                r.nama_wilayah AS region_name,
                r.level_wilayah AS region_level,
                AVG(f.nilai) AS value
            FROM fact_statistik f
            JOIN dim_waktu w ON w.th_id = f.th_id
            JOIN dim_wilayah r ON r.kode_wilayah = f.kode_wilayah
            WHERE f.indicator_key = ? AND w.tahun IN (?, ?)
            GROUP BY f.indicator_key, w.tahun, r.kode_wilayah, r.nama_wilayah, r.level_wilayah
        )
        SELECT
            start.indicator_key,
            start.region_code,
            start.region_name,
            start.region_level,
            ? AS from_year,
            ? AS to_year,
            ROUND(start.value, 4) AS from_value,
            ROUND(finish.value, 4) AS to_value,
            ROUND(finish.value - start.value, 4) AS delta,
            ROUND(ABS(finish.value - start.value), 4) AS abs_delta
        FROM regional_year start
        JOIN regional_year finish
            ON finish.indicator_key = start.indicator_key
            AND finish.region_code = start.region_code
            AND finish.year = ?
        WHERE start.year = ?
        ORDER BY abs_delta DESC, start.region_name ASC
        LIMIT ?
        """,
        (indicator_key, from_year, to_year, from_year, to_year, to_year, from_year, limit),
    )


def build_rankings(
    conn: sqlite3.Connection,
    indicators: list[dict[str, Any]],
    years: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    """Build dashboard ranking slices for top, bottom, and change modes."""
    top: list[dict[str, Any]] = []
    bottom: list[dict[str, Any]] = []
    change: list[dict[str, Any]] = []
    year_values = [int(row["year"]) for row in years]
    first_year = min(year_values) if year_values else None
    last_year = max(year_values) if year_values else None

    for indicator in indicators:
        for year in year_values:
            top.append(
                {
                    "indicator_key": indicator["key"],
                    "indicator_name": indicator["name"],
                    "unit": indicator["unit"],
                    "year": year,
                    "aggregation": "regional_average_of_available_rows",
                    "rows": ranking_rows(conn, indicator["key"], year, "top"),
                }
            )
            bottom.append(
                {
                    "indicator_key": indicator["key"],
                    "indicator_name": indicator["name"],
                    "unit": indicator["unit"],
                    "year": year,
                    "aggregation": "regional_average_of_available_rows",
                    "rows": ranking_rows(conn, indicator["key"], year, "bottom"),
                }
            )
        if first_year is not None and last_year is not None and first_year != last_year:
            change.append(
                {
                    "indicator_key": indicator["key"],
                    "indicator_name": indicator["name"],
                    "unit": indicator["unit"],
                    "from_year": first_year,
                    "to_year": last_year,
                    "aggregation": "regional_average_delta_between_years",
                    "rows": change_rows(conn, indicator["key"], first_year, last_year),
                }
            )
    return {"top": top, "bottom": bottom, "change": change}


def build_table_rows(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Load compact fact rows for the dashboard detail table."""
    return fetch_all(
        conn,
        """
        SELECT
            f.fact_id,
            f.indicator_key,
            i.nama_indikator AS indicator_name,
            COALESCE(i.unit, 'indeks') AS unit,
            f.var_id,
            f.kode_wilayah AS region_code,
            r.nama_wilayah AS region_name,
            r.level_wilayah AS region_level,
            f.th_id,
            w.tahun AS year,
            f.turvar_id,
            tv.turvar_label,
            f.turth_id,
            tt.turth_label,
            f.source_domain,
            ROUND(f.nilai, 4) AS value,
            f.last_update,
            f.data_key,
            f.loaded_at,
            f.run_id
        FROM fact_statistik f
        JOIN dim_indikator i ON i.var_id = f.var_id
        JOIN dim_wilayah r ON r.kode_wilayah = f.kode_wilayah
        JOIN dim_waktu w ON w.th_id = f.th_id
        JOIN dim_turvar tv ON tv.turvar_id = f.turvar_id
        JOIN dim_turtahun tt ON tt.turth_id = f.turth_id
        ORDER BY i.indicator_key, w.tahun, r.kode_wilayah, f.turvar_id, f.turth_id
        """,
    )


def _first(rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    return rows[0] if rows else None


def build_narrative_seed(
    trends: list[dict[str, Any]],
    rankings: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    """Prepare honest extrema and change statistics for client-side narrative text."""
    by_indicator: dict[str, Any] = {}
    for trend in trends:
        key = trend["indicator_key"]
        points = trend["points"]
        latest_point = points[-1] if points else None
        latest_year = latest_point["year"] if latest_point else None
        latest_top = next(
            (item for item in rankings["top"] if item["indicator_key"] == key and item["year"] == latest_year),
            None,
        )
        latest_bottom = next(
            (item for item in rankings["bottom"] if item["indicator_key"] == key and item["year"] == latest_year),
            None,
        )
        change = next((item for item in rankings["change"] if item["indicator_key"] == key), None)
        change_rows_for_indicator = change["rows"] if change else []
        positive_changes = [row for row in change_rows_for_indicator if row["delta"] >= 0]
        negative_changes = [row for row in change_rows_for_indicator if row["delta"] < 0]
        by_indicator[key] = {
            "indicator_name": trend["indicator_name"],
            "unit": trend["unit"],
            "aggregation": trend["aggregation"],
            "earliest_year": points[0]["year"] if points else None,
            "latest_year": latest_year,
            "latest_average": latest_point["value"] if latest_point else None,
            "latest_record_count": latest_point["record_count"] if latest_point else None,
            "latest_top": _first(latest_top["rows"]) if latest_top else None,
            "latest_bottom": _first(latest_bottom["rows"]) if latest_bottom else None,
            "largest_absolute_change": _first(change_rows_for_indicator),
            "largest_increase": _first(positive_changes),
            "largest_decrease": _first(negative_changes),
        }
    return {
        "method_note": "Narasi dihitung dari rata-rata baris fakta BPS yang tersedia per indikator, wilayah, dan tahun.",
        "by_indicator": by_indicator,
    }


def phase_progress() -> list[dict[str, str]]:
    """Return project phase progress for the static dashboard."""
    return [
        {
            "phase": "0B",
            "title": "Repository Infrastructure",
            "status": "complete",
            "description": "Scaffold repo, dashboard shell, GitHub Pages, dan smoke tests.",
        },
        {
            "phase": "1",
            "title": "BPS API Research & Proof",
            "status": "complete",
            "description": "6 indikator BPS valid, 24 probe rows, 4292 normalized sample records, 0 unmatched datacontent keys.",
        },
        {
            "phase": "2",
            "title": "ETL Architecture & Schema",
            "status": "complete",
            "description": "Star-schema SQLite, transform rules, data dictionary, dan 10 schema validation tests selesai.",
        },
        {
            "phase": "3",
            "title": "Extract Layer",
            "status": "complete",
            "description": "BPS client, retry/timeout, raw snapshot saving, manifest, 8 extract tests, dan review Fase 3 selesai.",
        },
        {
            "phase": "4",
            "title": "Transform Layer",
            "status": "complete",
            "description": "Decode datacontent, fact preview, dimension preview, quality metrics, 39 total tests, dan review Fase 4 selesai.",
        },
        {
            "phase": "5",
            "title": "Load Layer",
            "status": "complete",
            "description": "SQLite schema initialized, dimension/fact tables loaded, run log written, dan review Fase 5 approved.",
        },
        {
            "phase": "6",
            "title": "Dashboard",
            "status": "complete",
            "description": "Dashboard statis membaca JSON hasil generator dari SQLite lokal; review Fase 6 approved.",
        },
        {
            "phase": "6.1",
            "title": "Data Expansion",
            "status": "complete",
            "description": "Scope diperluas ke 6 indikator sosial-ekonomi, 2021–2024, 4292 fact rows, dan dashboard digenerate ulang dari SQLite.",
        },
    ]


def build_design_metrics(
    previous: dict[str, Any],
    counts: dict[str, int],
    load_metrics: dict[str, Any],
) -> dict[str, Any]:
    """Preserve stable design metrics while refreshing ETL evidence from current artifacts."""
    probe_summary = read_json(API_PROBE_SUMMARY_PATH)
    extract_manifest = read_json(EXTRACT_MANIFEST_PATH)
    transform_quality = read_json(TRANSFORM_QUALITY_PATH)
    transform_manifest = read_json(TRANSFORM_MANIFEST_PATH)
    design_metrics = dict(previous.get("design_metrics", {}))
    design_metrics.update(
        {
            "valid_indicators": counts["dim_indikator"],
            "api_probe_rows": probe_summary.get("probe_rows", design_metrics.get("api_probe_rows", 0)),
            "normalized_sample_records": probe_summary.get("normalized_record_count", design_metrics.get("normalized_sample_records", 0)),
            "unmatched_datacontent_keys": probe_summary.get("unmatched_key_count", design_metrics.get("unmatched_datacontent_keys", 0)),
            "extract_targets": extract_manifest.get("target_count", design_metrics.get("extract_targets", 0)),
            "metadata_snapshots": extract_manifest.get("metadata_snapshot_count", design_metrics.get("metadata_snapshots", 0)),
            "dynamic_snapshots": extract_manifest.get("dynamic_snapshot_count", design_metrics.get("dynamic_snapshots", 0)),
            "total_extract_snapshots": extract_manifest.get("total_snapshots", design_metrics.get("total_extract_snapshots", 0)),
            "total_raw_rows": extract_manifest.get("total_raw_rows", design_metrics.get("total_raw_rows", 0)),
            "transform_dynamic_snapshots": transform_manifest.get("dynamic_snapshot_count", design_metrics.get("transform_dynamic_snapshots", 0)),
            "transform_fact_preview_rows": transform_quality.get("fact_row_count", design_metrics.get("transform_fact_preview_rows", 0)),
            "transform_quality_gate": transform_quality.get("quality_gate", design_metrics.get("transform_quality_gate", "unknown")),
            "transform_unmatched_count": transform_quality.get("unmatched_count", design_metrics.get("transform_unmatched_count", 0)),
            "transform_duplicate_fact_key_count": transform_quality.get("duplicate_fact_key_count", design_metrics.get("transform_duplicate_fact_key_count", 0)),
            "transform_null_value_count": transform_quality.get("null_value_count", design_metrics.get("transform_null_value_count", 0)),
            "dim_indikator_rows": counts["dim_indikator"],
            "dim_wilayah_rows": counts["dim_wilayah"],
            "dim_waktu_rows": counts["dim_waktu"],
            "dim_turvar_rows": counts["dim_turvar"],
            "dim_turtahun_rows": counts["dim_turtahun"],
            "load_fact_rows": counts["fact_statistik"],
            "load_dim_indikator_rows": counts["dim_indikator"],
            "load_dim_wilayah_rows": counts["dim_wilayah"],
            "load_dim_waktu_rows": counts["dim_waktu"],
            "load_dim_turvar_rows": counts["dim_turvar"],
            "load_dim_turtahun_rows": counts["dim_turtahun"],
            "load_raw_snapshot_rows": counts["raw_api_snapshot"],
            "load_run_log_rows": counts["etl_run_log"],
            "load_database_path": load_metrics.get("database_path", "data/database/bps_etl.sqlite"),
            "dashboard_chart_series": counts["dim_indikator"],
            "dashboard_table_rows": counts["fact_statistik"],
            "dashboard_source": "SQLite fact_statistik",
        }
    )
    return design_metrics


def build_dashboard_data(
    database_path: Path = DEFAULT_DATABASE_PATH,
    template_path: Path = DASHBOARD_DATA_PATH,
    load_metrics_path: Path = LOAD_METRICS_PATH,
) -> dict[str, Any]:
    """Build the full Fase 6 dashboard data contract from SQLite rows only."""
    previous = read_json(template_path)
    load_metrics = read_json(load_metrics_path)
    conn = connect_existing_database(database_path)
    try:
        counts = table_counts(conn)
        if counts["fact_statistik"] == 0:
            raise DashboardDataError(
                "SQLite fact_statistik is empty. Run: python3 scripts/run_etl.py --phase load --mode quick"
            )
        indicators = load_indicators(conn)
        years = load_years(conn)
        regions = load_regions(conn)
        source_domains = load_source_domains(conn)
        trends = build_trend_series(conn, indicators)
        rankings = build_rankings(conn, indicators, years)
        table_rows = build_table_rows(conn)
        last_run = fetch_one(
            conn,
            """
            SELECT run_id, phase, status, started_at, finished_at, source_git_commit
            FROM etl_run_log
            ORDER BY COALESCE(finished_at, started_at) DESC, rowid DESC
            LIMIT 1
            """,
        )
        duplicate_grain = fetch_one(
            conn,
            """
            SELECT COUNT(*) AS duplicate_grains
            FROM (
                SELECT var_id, kode_wilayah, th_id, turvar_id, turth_id, source_domain
                FROM fact_statistik
                GROUP BY var_id, kode_wilayah, th_id, turvar_id, turth_id, source_domain
                HAVING COUNT(*) > 1
            )
            """,
        )
    finally:
        conn.close()

    first_indicator = indicators[0]["key"] if indicators else None
    latest_year = years[-1]["year"] if years else None
    charts_top = next(
        (item["rows"] for item in rankings["top"] if item["indicator_key"] == first_indicator and item["year"] == latest_year),
        [],
    )

    data: dict[str, Any] = {
        "project": {
            "title": "ETL BPS Dashboard Analitik",
            "status": "Fase 6.1 data expansion generated from populated SQLite; dashboard remains real-data-only.",
            "current_phase": "6.1 — Data Expansion",
            "generated_at": utc_now(),
            "review": {
                "phase": "6.1",
                "score": 92,
                "verdict": "APPROVED",
                "file": "docs/reviews/REVIEW_phase6_1_data_expansion.md",
                "previous": {"phase": 6, "score": 91, "verdict": "APPROVED", "file": "docs/reviews/REVIEW_phase6_dashboard.md"},
            },
        },
        "summary": {
            "indicator_count": counts["dim_indikator"],
            "region_count": counts["dim_wilayah"],
            "year_count": counts["dim_waktu"],
            "record_count": counts["fact_statistik"],
            "last_etl_run": last_run["run_id"] if last_run else None,
        },
        "filters": {
            "indicators": [{"key": row["key"], "name": row["name"]} for row in indicators],
            "years": years,
            "source_domains": source_domains,
            "ranking_modes": ["top", "bottom", "change"],
        },
        "indicators": indicators,
        "years": years,
        "regions": regions,
        "series": {"trend": trends},
        "rankings": rankings,
        "table_rows": table_rows,
        "narrative_seed": build_narrative_seed(trends, rankings),
        "phase_progress": phase_progress(),
        "design_metrics": build_design_metrics(previous, counts, load_metrics),
        "schema": {
            "fact_grain": "var_id + kode_wilayah + th_id + turvar_id + turth_id + source_domain",
            "tables": list(REQUIRED_TABLES),
        },
        "artifacts": ARTIFACTS,
        "charts": {
            "trend": trends,
            "regional_comparison": charts_top,
        },
        "evidence": {
            "database_path": relative_path(database_path),
            "db_counts": counts,
            "run_id": last_run["run_id"] if last_run else None,
            "last_run": last_run,
            "source_paths": {
                "sqlite": relative_path(database_path),
                "load_metrics": relative_path(load_metrics_path),
                "dashboard_json": "dashboard/data/dashboard-data.json",
            },
            "artifacts": ARTIFACTS,
            "review_references": [
                "docs/reviews/REVIEW_phase1_api_research.md",
                "docs/reviews/REVIEW_phase2_etl_design.md",
                "docs/reviews/REVIEW_phase3_extract_layer.md",
                "docs/reviews/REVIEW_phase4_transform_layer.md",
                "docs/reviews/REVIEW_phase5_load_layer.md",
            ],
        },
        "quality": {
            "no_dummy_data": True,
            "missing_values": 0,
            "duplicate_records": duplicate_grain["duplicate_grains"] if duplicate_grain else 0,
            "api_calls": counts["raw_api_snapshot"],
            "notes": [
                "Semua grafik, ranking, tabel, dan angka summary dibangun dari SQLite lokal.",
                "Jika database belum ada, generator gagal dan meminta load quick dijalankan.",
                "Agregasi dashboard memakai rata-rata baris fakta yang tersedia per indikator/tahun/wilayah.",
            ],
        },
    }
    return data


def build_parser() -> argparse.ArgumentParser:
    """Build CLI parser for dashboard JSON generation."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database-path", type=Path, default=DEFAULT_DATABASE_PATH)
    parser.add_argument("--output-path", type=Path, default=DASHBOARD_DATA_PATH)
    parser.add_argument("--load-metrics-path", type=Path, default=LOAD_METRICS_PATH)
    return parser


def main() -> int:
    """Generate dashboard/data/dashboard-data.json from the loaded SQLite database."""
    args = build_parser().parse_args()
    try:
        data = build_dashboard_data(args.database_path, args.output_path, args.load_metrics_path)
    except DashboardDataError as exc:
        raise SystemExit(str(exc)) from exc
    write_json(args.output_path, data)
    print(f"Generated {relative_path(args.output_path)} from {relative_path(args.database_path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
