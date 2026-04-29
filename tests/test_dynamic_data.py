from pathlib import Path
import json

import pytest

from bps_etl.extract.dynamic_data import build_datacontent_key_index, clean_label, decode_datacontent


def sample_payload():
    return {
        "last_update": "2026-01-01",
        "var": [{"val": 192, "label": "Persentase Penduduk Miskin", "unit": "Persen", "subj": "Kemiskinan"}],
        "vervar": [{"val": 1100, "label": "<b>ACEH</b>"}],
        "turvar": [{"val": 434, "label": "Jumlah"}],
        "tahun": [{"val": 123, "label": "2023"}],
        "turtahun": [{"val": 63, "label": "Tahunan"}],
        "datacontent": {"110019243412363": 14.45},
    }


def test_clean_label_removes_html():
    assert clean_label("<b>ACEH</b>") == "ACEH"


def test_build_datacontent_key_index_uses_bps_composite_key_rule():
    index = build_datacontent_key_index(sample_payload())
    assert "110019243412363" in index
    dims = index["110019243412363"]
    assert dims["kode_wilayah"] == "1100"
    assert dims["var_id"] == 192
    assert dims["turvar_id"] == "434"
    assert dims["th_id"] == 123
    assert dims["turth_id"] == "63"


def test_decode_datacontent_returns_normalized_records():
    records, unmatched = decode_datacontent(sample_payload(), indicator_key="poverty_rate")
    assert unmatched == []
    assert len(records) == 1
    row = records[0]
    assert row["indicator_key"] == "poverty_rate"
    assert row["nama_wilayah"] == "ACEH"
    assert row["tahun"] == "2023"
    assert row["nilai"] == 14.45


def test_build_datacontent_key_index_fails_on_collision():
    payload = sample_payload()
    payload["vervar"].append({"val": 1100, "label": "ACEH DUPLICATE"})
    with pytest.raises(ValueError, match="Duplicate BPS datacontent composite key"):
        build_datacontent_key_index(payload)


def test_real_bps_artifact_decodes_without_unmatched_keys():
    artifact = Path(__file__).resolve().parents[1] / "results/api/dynamic_poverty_rate_2023.json"
    assert artifact.exists(), "Fase 1 API evidence artifact is missing"

    payload = json.loads(artifact.read_text(encoding="utf-8"))["payload"]
    records, unmatched = decode_datacontent(payload, indicator_key="poverty_rate")

    assert unmatched == []
    assert len(records) == 104
    assert records[0]["indicator_key"] == "poverty_rate"
