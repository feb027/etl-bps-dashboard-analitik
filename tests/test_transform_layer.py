from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from bps_etl.transform.normalize import infer_region_level, transform_dynamic_payload
from bps_etl.transform.pipeline import run_transform


def sample_payload() -> dict:
    return {
        "last_update": "2026-01-01",
        "var": [{"val": 192, "label": "Persentase Penduduk Miskin", "unit": "Persen", "subj": "Kemiskinan"}],
        "vervar": [{"val": 1100, "label": "<b>ACEH</b>"}],
        "turvar": [{"val": 434, "label": "Jumlah"}],
        "tahun": [{"val": 123, "label": "2023"}],
        "turtahun": [{"val": 63, "label": "Tahunan"}],
        "datacontent": {"110019243412363": "14,45"},
    }


def test_transform_dynamic_payload_builds_fact_dimensions_and_quality():
    result = transform_dynamic_payload(
        sample_payload(),
        indicator_key="poverty_rate",
        theme="Kemiskinan",
        source_domain="0000",
        artifact_path="results/api/extract/data/dynamic_poverty_rate_2023.json",
        snapshot_id="bps-data-test",
    )

    assert result.quality["raw_datacontent_count"] == 1
    assert result.quality["decoded_count"] == 1
    assert result.quality["unmatched_count"] == 0
    assert result.quality["duplicate_fact_key_count"] == 0
    assert result.quality["null_value_count"] == 0
    assert result.fact_rows[0]["nilai"] == 14.45
    assert result.fact_rows[0]["data_key"] == "110019243412363"
    assert result.dimensions["dim_indikator"][0]["indicator_key"] == "poverty_rate"
    assert result.dimensions["dim_wilayah"][0]["nama_wilayah"] == "ACEH"
    assert result.dimensions["dim_waktu"][0]["tahun"] == 2023


def test_transform_dynamic_payload_quality_tracks_unmatched_and_null_values():
    payload = sample_payload()
    payload["datacontent"] = {
        "110019243412363": None,
        "999999999": 1.0,
    }

    result = transform_dynamic_payload(
        payload,
        indicator_key="poverty_rate",
        theme="Kemiskinan",
        source_domain="0000",
        artifact_path="artifact.json",
        snapshot_id="snapshot",
    )

    assert result.quality["raw_datacontent_count"] == 2
    assert result.quality["decoded_count"] == 1
    assert result.quality["unmatched_count"] == 1
    assert result.quality["null_value_count"] == 1
    assert result.quality["quality_gate"] == "failed"
    assert result.unmatched_keys == ["999999999"]


def test_infer_region_level_labels_common_bps_codes():
    assert infer_region_level("0") == "nasional"
    assert infer_region_level("1100") == "provinsi"
    assert infer_region_level("1101") == "kabupaten_kota"
    assert infer_region_level("1101010") == "unknown"


def test_run_transform_writes_normalized_artifacts_from_phase3_extract(tmp_path: Path):
    root = Path(__file__).resolve().parents[1]
    summary = run_transform(
        extract_manifest_path=root / "results/api/extract/extract_manifest.json",
        selected_indicators_path=root / "results/api/selected_indicators.json",
        output_dir=tmp_path,
    )

    assert summary["status"] == "success"
    assert summary["phase"] == "4 — Transform Layer"
    assert summary["dynamic_snapshot_count"] == 12
    assert summary["fact_row_count"] == 2490
    assert summary["unmatched_count"] == 0
    assert summary["duplicate_fact_key_count"] == 0
    assert summary["null_value_count"] == 0
    assert summary["quality_gate"] == "passed"
    assert summary["dimension_counts"]["dim_indikator"] == 4
    assert summary["dimension_counts"]["dim_wilayah"] >= 34
    assert summary["dimension_counts"]["dim_waktu"] == 3

    fact_path = tmp_path / "fact_statistik_preview.csv"
    quality_path = tmp_path / "transform_quality_metrics.json"
    dimensions_path = tmp_path / "dimensions_preview.json"
    manifest_path = tmp_path / "transform_manifest.json"

    assert fact_path.exists()
    assert quality_path.exists()
    assert dimensions_path.exists()
    assert manifest_path.exists()

    rows = list(csv.DictReader(fact_path.open(encoding="utf-8")))
    assert len(rows) == 2490
    assert {row["indicator_key"] for row in rows} == {
        "poverty_rate",
        "open_unemployment_rate",
        "mean_years_schooling_new_method",
        "human_development_index_new_method",
    }
    assert json.loads(quality_path.read_text(encoding="utf-8"))["quality_gate"] == "passed"


def test_run_transform_rejects_duplicate_fact_grain_across_snapshots(tmp_path: Path):
    extract_dir = tmp_path / "extract"
    data_dir = extract_dir / "data"
    data_dir.mkdir(parents=True)
    artifact = {
        "request": {"domain": "0000", "params": {"var": 192, "th": 123}},
        "payload": sample_payload(),
    }
    (data_dir / "a.json").write_text(json.dumps(artifact), encoding="utf-8")
    (data_dir / "b.json").write_text(json.dumps(artifact), encoding="utf-8")
    manifest = {
        "snapshots": [
            {"model": "data", "domain": "0000", "artifact_group": "data", "artifact_path": "a.json", "snapshot_id": "a"},
            {"model": "data", "domain": "0000", "artifact_group": "data", "artifact_path": "b.json", "snapshot_id": "b"},
        ]
    }
    manifest_path = extract_dir / "extract_manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    selected = [{"indicator_key": "poverty_rate", "var_id": 192, "theme": "Kemiskinan"}]
    selected_path = tmp_path / "selected_indicators.json"
    selected_path.write_text(json.dumps(selected), encoding="utf-8")

    with pytest.raises(ValueError, match="duplicate_fact_key_count"):
        run_transform(
            extract_manifest_path=manifest_path,
            selected_indicators_path=selected_path,
            output_dir=tmp_path / "transform",
        )
