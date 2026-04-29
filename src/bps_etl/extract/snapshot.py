"""Commit-safe raw BPS API snapshot persistence."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any

SECRET_PARAM_NAMES = {"key", "api_key", "token", "password", "secret"}


@dataclass(frozen=True)
class RawSnapshot:
    snapshot_id: str
    model: str
    artifact_group: str
    domain: str
    params: dict[str, Any]
    artifact_path: str
    artifact_sha256: str
    row_count: int
    captured_at: str
    request_fingerprint: str

    def asdict(self) -> dict[str, Any]:
        return asdict(self)


def sanitized_params(params: dict[str, Any] | None) -> dict[str, Any]:
    """Return request params with secrets removed."""
    clean: dict[str, Any] = {}
    for key, value in (params or {}).items():
        if str(key).lower() in SECRET_PARAM_NAMES:
            continue
        clean[str(key)] = value
    return clean


def request_fingerprint(*, model: str, domain: str, params: dict[str, Any] | None = None) -> str:
    """Stable sha256 for a BPS request identity, excluding API key-like params."""
    material = {
        "model": model,
        "domain": domain,
        "params": sanitized_params(params),
    }
    encoded = json.dumps(material, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def snapshot_id_for(*, model: str, domain: str, params: dict[str, Any] | None = None) -> str:
    return f"bps-{model}-{request_fingerprint(model=model, domain=domain, params=params)[:16]}"


def save_raw_snapshot(
    *,
    output_dir: Path,
    model: str,
    domain: str,
    params: dict[str, Any] | None,
    payload: dict[str, Any],
    artifact_name: str,
    row_count: int,
    artifact_group: str = "raw",
    captured_at: str | None = None,
) -> RawSnapshot:
    """Write a sanitized BPS raw snapshot and return manifest metadata."""
    output_dir.mkdir(parents=True, exist_ok=True)
    captured_at = captured_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    clean_params = sanitized_params(params)
    artifact = {
        "captured_at": captured_at,
        "request": {
            "model": model,
            "domain": domain,
            "params": clean_params,
        },
        "request_fingerprint": request_fingerprint(model=model, domain=domain, params=params),
        "row_count": row_count,
        "payload": payload,
    }
    path = output_dir / artifact_name
    path.write_text(json.dumps(artifact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    digest = sha256_file(path)
    return RawSnapshot(
        snapshot_id=snapshot_id_for(model=model, domain=domain, params=params),
        model=model,
        artifact_group=artifact_group,
        domain=domain,
        params=clean_params,
        artifact_path=artifact_name,
        artifact_sha256=digest,
        row_count=row_count,
        captured_at=captured_at,
        request_fingerprint=artifact["request_fingerprint"],
    )
