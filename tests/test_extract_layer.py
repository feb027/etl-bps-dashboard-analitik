from __future__ import annotations

import json
from pathlib import Path
from urllib.error import HTTPError, URLError

import pytest

from bps_etl.extract.client import BPSClient, BPSRequest
from bps_etl.extract.metadata import ExtractTarget, load_extract_targets
from bps_etl.extract.pipeline import run_extract
from bps_etl.extract.snapshot import request_fingerprint, save_raw_snapshot
from scripts.run_etl import build_parser


class FakeResponse:
    def __init__(self, payload: dict):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")


def test_bps_client_retries_transient_url_errors(monkeypatch):
    calls = {"count": 0}

    def fake_urlopen(request, timeout):
        calls["count"] += 1
        if calls["count"] == 1:
            raise URLError("temporary failure")
        return FakeResponse({"status": "ok", "data": [{"pages": 1}, []]})

    monkeypatch.setattr("bps_etl.extract.client.urlopen", fake_urlopen)
    client = BPSClient(api_key="test-api-key-placeholder", base_url="https://example.test/list", timeout=1, retries=2, retry_backoff=0)

    payload = client.request(BPSRequest(model="var"))

    assert payload["status"] == "ok"
    assert calls["count"] == 2


def test_bps_client_does_not_retry_permanent_http_client_errors(monkeypatch):
    calls = {"count": 0}

    def fake_urlopen(request, timeout):
        calls["count"] += 1
        raise HTTPError(url="https://example.test/list", code=404, msg="not found", hdrs=None, fp=None)

    monkeypatch.setattr("bps_etl.extract.client.urlopen", fake_urlopen)
    client = BPSClient(api_key="test-api-key-placeholder", base_url="https://example.test/list", timeout=1, retries=2, retry_backoff=0)

    with pytest.raises(RuntimeError, match="HTTP 404"):
        client.request(BPSRequest(model="data"))

    assert calls["count"] == 1


def test_request_fingerprint_is_stable_and_excludes_api_key():
    first = request_fingerprint(model="data", domain="0000", params={"var": 192, "th": 123, "key": "test-api-key-placeholder-a"})
    second = request_fingerprint(model="data", domain="0000", params={"th": 123, "var": 192, "key": "test-api-key-placeholder-b"})

    assert first == second
    assert "test-api-key-placeholder" not in first
    assert len(first) == 64


def test_save_raw_snapshot_writes_payload_and_manifest_without_api_key(tmp_path: Path):
    snapshot = save_raw_snapshot(
        output_dir=tmp_path,
        model="data",
        domain="0000",
        params={"var": 192, "th": 123, "key": "test-api-key-placeholder"},
        payload={"datacontent": {"110019243412363": 14.45}},
        artifact_name="dynamic_poverty_rate_2023.json",
        row_count=1,
        artifact_group="data",
    )

    artifact = json.loads((tmp_path / "dynamic_poverty_rate_2023.json").read_text(encoding="utf-8"))
    assert artifact["payload"]["datacontent"]["110019243412363"] == 14.45
    assert "key" not in artifact["request"]["params"]
    assert "test-api-key-placeholder" not in json.dumps(artifact, ensure_ascii=False)
    assert snapshot.artifact_sha256
    assert snapshot.row_count == 1
    assert snapshot.artifact_path == "dynamic_poverty_rate_2023.json"
    assert snapshot.artifact_group == "data"


def test_load_extract_targets_uses_selected_indicator_period_ids(tmp_path: Path):
    selected = [
        {
            "indicator_key": "poverty_rate",
            "var_id": 192,
            "theme": "Kemiskinan",
            "target_years": ["2023", "2022"],
            "period_ids": {"2023": 123, "2022": 122},
        }
    ]
    path = tmp_path / "selected_indicators.json"
    path.write_text(json.dumps(selected), encoding="utf-8")

    targets = load_extract_targets(path)

    assert targets == [
        ExtractTarget(indicator_key="poverty_rate", var_id=192, theme="Kemiskinan", year="2023", th_id=123, domain="0000"),
        ExtractTarget(indicator_key="poverty_rate", var_id=192, theme="Kemiskinan", year="2022", th_id=122, domain="0000"),
    ]


def test_load_extract_targets_rejects_missing_period_id(tmp_path: Path):
    selected = [
        {
            "indicator_key": "poverty_rate",
            "var_id": 192,
            "theme": "Kemiskinan",
            "target_years": ["2023"],
            "period_ids": {},
        }
    ]
    path = tmp_path / "selected_indicators.json"
    path.write_text(json.dumps(selected), encoding="utf-8")

    with pytest.raises(ValueError, match="missing th_id"):
        load_extract_targets(path)


class FakeClient:
    def list_rows(self, model, *, domain="0000", params=None, max_pages=None):
        return {"pages": 1}, [{"model": model, "var": (params or {}).get("var"), "value": "sample"}]

    def dynamic_data(self, var_id, th_id, *, domain="0000"):
        return {
            "data-availability": "available",
            "datacontent": {f"1100{var_id}434{th_id}63": 1.23},
            "var": [{"val": str(var_id), "label": "Sample Indicator"}],
            "vervar": [{"val": "1100", "label": "ACEH"}],
            "turvar": [{"val": "434", "label": "Jumlah"}],
            "tahun": [{"val": str(th_id), "label": "2023"}],
            "turtahun": [{"val": "63", "label": "Tahunan"}],
        }


def test_run_extract_writes_manifest_for_metadata_and_dynamic_snapshots(tmp_path: Path):
    target = ExtractTarget(indicator_key="poverty_rate", var_id=192, theme="Kemiskinan", year="2023", th_id=123)

    summary = run_extract(client=FakeClient(), targets=[target], output_dir=tmp_path, metadata_models=("th", "vervar"))

    manifest_path = tmp_path / "extract_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert summary["status"] == "success"
    assert summary["dynamic_snapshot_count"] == 1
    assert summary["metadata_snapshot_count"] == 2
    assert manifest["total_snapshots"] == 3
    assert all("artifact_sha256" in item for item in manifest["snapshots"])
    assert {item["artifact_group"] for item in manifest["snapshots"]} == {"metadata", "data"}
    assert all("key" not in json.dumps(item, ensure_ascii=False) for item in manifest["snapshots"])


def test_run_etl_parser_supports_extract_phase_and_quick_mode():
    args = build_parser().parse_args(["--phase", "extract", "--mode", "quick"])

    assert args.phase == "extract"
    assert args.mode == "quick"
