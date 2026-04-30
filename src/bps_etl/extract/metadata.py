"""Metadata target planning for BPS dynamic table extraction."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from bps_etl.config import RESULTS_DIR

TARGET_MODELS = ("th", "vervar", "turvar", "turth", "unit")
DEFAULT_SELECTED_INDICATORS_PATH = RESULTS_DIR / "api" / "selected_indicators.json"


@dataclass(frozen=True)
class ExtractTarget:
    """One BPS dynamic-data extraction target."""

    indicator_key: str
    var_id: int
    theme: str
    year: str
    th_id: int
    domain: str = "0000"


def load_selected_indicators(path: Path = DEFAULT_SELECTED_INDICATORS_PATH) -> list[dict[str, Any]]:
    """Load selected indicators generated in Fase 1."""
    if not path.exists():
        raise FileNotFoundError(f"selected indicators not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("selected indicators artifact must be a JSON list")
    return data


def load_extract_targets(path: Path = DEFAULT_SELECTED_INDICATORS_PATH, *, domain: str = "0000") -> list[ExtractTarget]:
    """Build extraction targets from selected indicators and persisted year→th_id mapping."""
    targets: list[ExtractTarget] = []
    for indicator in load_selected_indicators(path):
        indicator_key = str(indicator["indicator_key"])
        var_id = int(indicator["var_id"])
        theme = str(indicator.get("theme") or "")
        period_ids = indicator.get("period_ids") or {}
        for year in indicator.get("target_years") or []:
            if str(year) not in period_ids:
                raise ValueError(f"missing th_id for {indicator_key} year={year}")
            targets.append(
                ExtractTarget(
                    indicator_key=indicator_key,
                    var_id=var_id,
                    theme=theme,
                    year=str(year),
                    th_id=int(period_ids[str(year)]),
                    domain=domain,
                )
            )
    if not targets:
        raise ValueError("no extract targets generated from selected indicators")
    return targets
