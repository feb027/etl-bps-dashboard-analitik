"""BPS API client scaffold.

Implementation will be completed in Fase 3 after Fase 1 proves exact endpoint behavior.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class BPSRequest:
    model: str
    domain: str = "0000"
    params: dict[str, Any] | None = None


def build_query_params(request: BPSRequest, api_key: str) -> dict[str, Any]:
    """Build BPS list endpoint query params without mutating input."""
    params = dict(request.params or {})
    params.update({"model": request.model, "domain": request.domain, "lang": "ind", "key": api_key})
    return params
