"""Fase 3 extract pipeline: fetch BPS metadata/data and persist raw evidence."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Iterable, Protocol

from bps_etl.config import RESULTS_DIR
from bps_etl.extract.metadata import ExtractTarget, TARGET_MODELS
from bps_etl.extract.snapshot import RawSnapshot, save_raw_snapshot

DEFAULT_EXTRACT_OUTPUT_DIR = RESULTS_DIR / "api" / "extract"


class ExtractClient(Protocol):
    def list_rows(
        self,
        model: str,
        *,
        domain: str = "0000",
        params: dict[str, Any] | None = None,
        max_pages: int | None = None,
    ) -> tuple[dict[str, Any], list[dict[str, Any]]]: ...

    def dynamic_data(self, var_id: int, th_id: int, *, domain: str = "0000") -> dict[str, Any]: ...


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def safe_indicator_key(value: str) -> str:
    return "".join(ch if ch.isalnum() or ch in {"_", "-"} else "_" for ch in value)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _metadata_snapshot_name(target: ExtractTarget, model: str) -> str:
    return f"metadata_{safe_indicator_key(target.indicator_key)}_{model}.json"


def _dynamic_snapshot_name(target: ExtractTarget) -> str:
    return f"dynamic_{safe_indicator_key(target.indicator_key)}_{target.year}.json"


def _payload_row_count(model: str, payload: dict[str, Any]) -> int:
    if model == "data":
        return len(payload.get("datacontent") or {})
    rows = payload.get("rows")
    return len(rows) if isinstance(rows, list) else 0


def fetch_metadata_snapshot(
    *,
    client: ExtractClient,
    target: ExtractTarget,
    model: str,
    output_dir: Path,
    captured_at: str,
) -> RawSnapshot:
    params: dict[str, Any] = {"var": target.var_id}
    meta, rows = client.list_rows(model, domain=target.domain, params=params)
    payload = {"metadata": meta, "rows": rows}
    return save_raw_snapshot(
        output_dir=output_dir / "metadata",
        model=model,
        domain=target.domain,
        params=params,
        payload=payload,
        artifact_name=_metadata_snapshot_name(target, model),
        row_count=len(rows),
        artifact_group="metadata",
        captured_at=captured_at,
    )


def fetch_dynamic_snapshot(*, client: ExtractClient, target: ExtractTarget, output_dir: Path, captured_at: str) -> RawSnapshot:
    params = {"var": target.var_id, "th": target.th_id}
    payload = client.dynamic_data(target.var_id, target.th_id, domain=target.domain)
    return save_raw_snapshot(
        output_dir=output_dir / "data",
        model="data",
        domain=target.domain,
        params=params,
        payload=payload,
        artifact_name=_dynamic_snapshot_name(target),
        row_count=_payload_row_count("data", payload),
        artifact_group="data",
        captured_at=captured_at,
    )


def _unique_indicator_targets(targets: Iterable[ExtractTarget]) -> list[ExtractTarget]:
    seen: set[tuple[str, int, str]] = set()
    unique: list[ExtractTarget] = []
    for target in targets:
        key = (target.indicator_key, target.var_id, target.domain)
        if key in seen:
            continue
        seen.add(key)
        unique.append(target)
    return unique


def _display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(Path.cwd().resolve()))
    except ValueError:
        return str(path)


def run_extract(
    *,
    client: ExtractClient,
    targets: list[ExtractTarget],
    output_dir: Path = DEFAULT_EXTRACT_OUTPUT_DIR,
    metadata_models: tuple[str, ...] = TARGET_MODELS,
) -> dict[str, Any]:
    """Run Fase 3 extraction and write raw snapshots plus manifest."""
    if not targets:
        raise ValueError("targets must not be empty")

    captured_at = utc_now()
    snapshots: list[RawSnapshot] = []

    for target in _unique_indicator_targets(targets):
        for model in metadata_models:
            snapshots.append(
                fetch_metadata_snapshot(
                    client=client,
                    target=target,
                    model=model,
                    output_dir=output_dir,
                    captured_at=captured_at,
                )
            )

    for target in targets:
        snapshots.append(fetch_dynamic_snapshot(client=client, target=target, output_dir=output_dir, captured_at=captured_at))

    metadata_count = sum(1 for item in snapshots if item.model != "data")
    dynamic_count = sum(1 for item in snapshots if item.model == "data")
    total_rows = sum(item.row_count for item in snapshots)
    summary = {
        "status": "success",
        "phase": "3 — Extract Layer",
        "captured_at": captured_at,
        "target_count": len(targets),
        "metadata_snapshot_count": metadata_count,
        "dynamic_snapshot_count": dynamic_count,
        "total_snapshots": len(snapshots),
        "total_raw_rows": total_rows,
        "output_dir": _display_path(output_dir),
        "snapshots": [item.asdict() for item in snapshots],
    }
    write_json(output_dir / "extract_manifest.json", summary)
    return summary
