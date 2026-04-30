#!/usr/bin/env python3
"""Generate dashboard JSON from committed ETL evidence artifacts.

Fase 5 behavior: publish load evidence from `results/database/load_metrics.json`
while keeping chart arrays empty until Fase 6 builds database-derived visuals.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_DATA_PATH = ROOT / "dashboard" / "data" / "dashboard-data.json"
LOAD_METRICS_PATH = ROOT / "results" / "database" / "load_metrics.json"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_dashboard_data(template_path: Path = DASHBOARD_DATA_PATH, load_metrics_path: Path = LOAD_METRICS_PATH) -> dict[str, Any]:
    data = read_json(template_path) if template_path.exists() else {}
    load_metrics = read_json(load_metrics_path)
    counts = load_metrics["table_counts"]

    data.setdefault("project", {})
    data.setdefault("summary", {})
    data.setdefault("design_metrics", {})
    data.setdefault("charts", {"trend": [], "regional_comparison": []})
    data.setdefault("quality", {})

    data["project"].update(
        {
            "title": "ETL BPS Dashboard Analitik",
            "status": "Fase 5 load layer implemented: SQLite berhasil terisi idempotent dari output transform; dashboard statistik/grafik masih ditahan untuk Fase 6.",
            "current_phase": "5 — Load Layer",
            "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "review": data["project"].get("review") or {"phase": 5, "score": None, "verdict": "PENDING", "file": None},
        }
    )
    data["summary"].update(
        {
            "indicator_count": counts["dim_indikator"],
            "region_count": counts["dim_wilayah"],
            "year_count": counts["dim_waktu"],
            "record_count": counts["fact_statistik"],
            "last_etl_run": load_metrics["run_id"],
        }
    )
    data["design_metrics"].update(
        {
            "load_fact_rows": counts["fact_statistik"],
            "load_dim_indikator_rows": counts["dim_indikator"],
            "load_dim_wilayah_rows": counts["dim_wilayah"],
            "load_dim_waktu_rows": counts["dim_waktu"],
            "load_dim_turvar_rows": counts["dim_turvar"],
            "load_dim_turtahun_rows": counts["dim_turtahun"],
            "load_raw_snapshot_rows": counts["raw_api_snapshot"],
            "load_run_log_rows": counts["etl_run_log"],
            "load_database_path": load_metrics["database_path"],
        }
    )
    data["charts"] = {"trend": [], "regional_comparison": []}
    data["quality"]["notes"] = [
        "SQLite load selesai dan fact_statistik terisi dari artifact BPS asli.",
        "Database SQLite berada di data/database/bps_etl.sqlite dan tidak dicommit karena aturan no .db in git.",
        "Dashboard tetap tidak menampilkan grafik statistik sampai Fase 6 generator dashboard/charts selesai.",
    ]
    return data


def main() -> int:
    data = build_dashboard_data()
    write_json(DASHBOARD_DATA_PATH, data)
    print(f"Generated {DASHBOARD_DATA_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
