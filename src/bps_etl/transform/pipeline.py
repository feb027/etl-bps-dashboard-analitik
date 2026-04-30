"""Fase 4 transform pipeline: decode committed raw BPS extract snapshots."""

from __future__ import annotations

import csv
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from bps_etl.config import RESULTS_DIR
from bps_etl.extract.pipeline import write_json
from bps_etl.transform.normalize import DIMENSION_TABLES, FACT_GRAIN_FIELDS, fact_grain, transform_dynamic_payload

DEFAULT_TRANSFORM_OUTPUT_DIR = RESULTS_DIR / "tables" / "transform"
DEFAULT_EXTRACT_MANIFEST_PATH = RESULTS_DIR / "api" / "extract" / "extract_manifest.json"
DEFAULT_SELECTED_INDICATORS_PATH = RESULTS_DIR / "api" / "selected_indicators.json"

FACT_FIELDNAMES = [
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
    "artifact_path",
    "snapshot_id",
]

DIMENSION_KEYS: dict[str, tuple[str, ...]] = {
    "dim_indikator": ("var_id",),
    "dim_wilayah": ("kode_wilayah",),
    "dim_waktu": ("th_id",),
    "dim_turvar": ("turvar_id",),
    "dim_turtahun": ("turth_id",),
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def load_indicator_lookup(path: Path = DEFAULT_SELECTED_INDICATORS_PATH) -> dict[int, dict[str, Any]]:
    indicators = read_json(path)
    if not isinstance(indicators, list):
        raise ValueError("selected indicators artifact must be a JSON list")
    lookup: dict[int, dict[str, Any]] = {}
    for item in indicators:
        var_id = int(item["var_id"])
        lookup[var_id] = item
    return lookup


def _artifact_display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(Path.cwd().resolve()))
    except ValueError:
        return str(path)


def _snapshot_artifact_path(extract_manifest_path: Path, snapshot: dict[str, Any]) -> Path:
    group = snapshot.get("artifact_group") or ("data" if snapshot.get("model") == "data" else "metadata")
    return extract_manifest_path.parent / str(group) / str(snapshot["artifact_path"])


def _merge_dimension_rows(target: dict[str, dict[tuple[Any, ...], dict[str, Any]]], dimensions: dict[str, list[dict[str, Any]]]) -> None:
    for table in DIMENSION_TABLES:
        key_fields = DIMENSION_KEYS[table]
        bucket = target.setdefault(table, {})
        for row in dimensions.get(table, []):
            key = tuple(row.get(field) for field in key_fields)
            bucket.setdefault(key, row)


def _flatten_dimensions(dimensions: dict[str, dict[tuple[Any, ...], dict[str, Any]]]) -> dict[str, list[dict[str, Any]]]:
    flattened: dict[str, list[dict[str, Any]]] = {}
    for table in DIMENSION_TABLES:
        rows = list(dimensions.get(table, {}).values())
        flattened[table] = sorted(rows, key=lambda row: tuple(str(row.get(field, "")) for field in DIMENSION_KEYS[table]))
    return flattened


def _combined_duplicate_fact_key_count(fact_rows: list[dict[str, Any]]) -> int:
    counts: dict[tuple[Any, ...], int] = {}
    for row in fact_rows:
        key = fact_grain(row)
        counts[key] = counts.get(key, 0) + 1
    return sum(count - 1 for count in counts.values() if count > 1)


def _quality_gate(metrics: dict[str, int]) -> str:
    passed = (
        metrics["raw_datacontent_count"] > 0
        and metrics["decoded_count"] == metrics["raw_datacontent_count"]
        and metrics["unmatched_count"] == 0
        and metrics["duplicate_fact_key_count"] == 0
        and metrics["null_value_count"] == 0
    )
    return "passed" if passed else "failed"


def run_transform(
    *,
    extract_manifest_path: Path = DEFAULT_EXTRACT_MANIFEST_PATH,
    selected_indicators_path: Path = DEFAULT_SELECTED_INDICATORS_PATH,
    output_dir: Path = DEFAULT_TRANSFORM_OUTPUT_DIR,
) -> dict[str, Any]:
    """Run Fase 4 transform from committed Fase 3 raw extract snapshots."""
    manifest = read_json(extract_manifest_path)
    indicator_lookup = load_indicator_lookup(selected_indicators_path)
    dynamic_snapshots = [item for item in manifest.get("snapshots", []) if item.get("model") == "data"]
    if not dynamic_snapshots:
        raise ValueError("extract manifest contains no dynamic data snapshots")

    captured_at = utc_now()
    all_fact_rows: list[dict[str, Any]] = []
    merged_dimensions: dict[str, dict[tuple[Any, ...], dict[str, Any]]] = {table: {} for table in DIMENSION_TABLES}
    snapshot_summaries: list[dict[str, Any]] = []
    raw_datacontent_count = 0
    decoded_count = 0
    unmatched_count = 0
    null_value_count = 0
    unmatched_keys: list[dict[str, Any]] = []

    for snapshot in dynamic_snapshots:
        artifact_path = _snapshot_artifact_path(extract_manifest_path, snapshot)
        artifact = read_json(artifact_path)
        payload = artifact.get("payload") or {}
        var_meta = payload.get("var") or []
        if not var_meta:
            raise ValueError(f"missing var metadata in {artifact_path}")
        var_id = int(var_meta[0]["val"])
        indicator = indicator_lookup.get(var_id)
        if indicator is None:
            raise ValueError(f"missing selected indicator config for var_id={var_id}")

        result = transform_dynamic_payload(
            payload,
            indicator_key=str(indicator["indicator_key"]),
            theme=str(indicator.get("theme") or ""),
            source_domain=str(snapshot.get("domain") or artifact.get("request", {}).get("domain") or "0000"),
            artifact_path=_artifact_display_path(artifact_path),
            snapshot_id=str(snapshot.get("snapshot_id") or ""),
        )
        all_fact_rows.extend(result.fact_rows)
        _merge_dimension_rows(merged_dimensions, result.dimensions)
        raw_datacontent_count += int(result.quality["raw_datacontent_count"])
        decoded_count += int(result.quality["decoded_count"])
        unmatched_count += int(result.quality["unmatched_count"])
        null_value_count += int(result.quality["null_value_count"])
        for key in result.unmatched_keys:
            unmatched_keys.append({"artifact_path": _artifact_display_path(artifact_path), "data_key": key})
        snapshot_summaries.append(
            {
                "snapshot_id": snapshot.get("snapshot_id"),
                "artifact_path": _artifact_display_path(artifact_path),
                "indicator_key": indicator["indicator_key"],
                "var_id": var_id,
                **result.quality,
            }
        )

    duplicate_fact_key_count = _combined_duplicate_fact_key_count(all_fact_rows)
    quality_metrics = {
        "raw_datacontent_count": raw_datacontent_count,
        "decoded_count": decoded_count,
        "fact_row_count": len(all_fact_rows),
        "unmatched_count": unmatched_count,
        "duplicate_fact_key_count": duplicate_fact_key_count,
        "null_value_count": null_value_count,
    }
    quality_metrics["quality_gate"] = _quality_gate(quality_metrics)

    if quality_metrics["quality_gate"] != "passed":
        raise ValueError(f"transform quality gate failed: {quality_metrics}")

    dimensions = _flatten_dimensions(merged_dimensions)
    dimension_counts = {table: len(rows) for table, rows in dimensions.items()}

    output_dir.mkdir(parents=True, exist_ok=True)
    fact_path = output_dir / "fact_statistik_preview.csv"
    quality_path = output_dir / "transform_quality_metrics.json"
    dimensions_path = output_dir / "dimensions_preview.json"
    unmatched_path = output_dir / "unmatched_datacontent_keys.json"
    manifest_path = output_dir / "transform_manifest.json"

    write_csv(fact_path, sorted(all_fact_rows, key=lambda row: tuple(str(row.get(field, "")) for field in FACT_GRAIN_FIELDS)), FACT_FIELDNAMES)
    write_json(quality_path, quality_metrics)
    write_json(dimensions_path, dimensions)
    write_json(unmatched_path, unmatched_keys)

    summary = {
        "status": "success",
        "phase": "4 — Transform Layer",
        "captured_at": captured_at,
        "source_extract_manifest": _artifact_display_path(extract_manifest_path),
        "dynamic_snapshot_count": len(dynamic_snapshots),
        "fact_row_count": len(all_fact_rows),
        "dimension_counts": dimension_counts,
        "raw_datacontent_count": raw_datacontent_count,
        "decoded_count": decoded_count,
        "unmatched_count": unmatched_count,
        "duplicate_fact_key_count": duplicate_fact_key_count,
        "null_value_count": null_value_count,
        "quality_gate": quality_metrics["quality_gate"],
        "output_dir": _artifact_display_path(output_dir),
        "artifacts": {
            "fact_preview": _artifact_display_path(fact_path),
            "quality_metrics": _artifact_display_path(quality_path),
            "dimensions_preview": _artifact_display_path(dimensions_path),
            "unmatched_keys": _artifact_display_path(unmatched_path),
        },
        "snapshots": snapshot_summaries,
    }
    write_json(manifest_path, summary)
    return summary
