"""Configuration helpers for BPS ETL.

No API key is hardcoded here. Runtime code must load BPS_API_KEY from the
environment or a local .env file.
"""

from __future__ import annotations

import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
RESULTS_DIR = ROOT_DIR / "results"
DASHBOARD_DATA_PATH = ROOT_DIR / "dashboard" / "data" / "dashboard-data.json"

BPS_BASE_URL = os.getenv("BPS_BASE_URL", "https://webapi.bps.go.id/v1/api/list")
BPS_API_KEY = os.getenv("BPS_API_KEY", "")


def require_bps_api_key() -> str:
    """Return BPS API key or raise a clear runtime error."""
    if not BPS_API_KEY:
        raise RuntimeError("BPS_API_KEY is not set. Copy .env.example to .env and fill the key.")
    return BPS_API_KEY
