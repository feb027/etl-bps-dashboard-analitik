#!/usr/bin/env python3
"""Generate dashboard JSON from real artifacts/database.

Current Fase 0B behavior writes an honest empty-state JSON. Later phases will
populate this from SQLite and result artifacts.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def build_empty_dashboard_data() -> dict:
    return {
        "project": {
            "title": "ETL BPS Dashboard Analitik",
            "status": "Fase 0B scaffold; data statistik belum tersedia",
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
        "summary": {
            "indicator_count": 0,
            "region_count": 0,
            "year_count": 0,
            "record_count": 0,
            "last_etl_run": None,
        },
        "charts": {
            "trend": [],
            "regional_comparison": [],
        },
        "quality": {
            "missing_values": None,
            "duplicate_records": None,
            "api_calls": None,
            "notes": ["Dashboard intentionally shows empty state until real ETL artifacts exist."],
        },
    }


def main() -> int:
    path = Path("dashboard/data/dashboard-data.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(build_empty_dashboard_data(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
