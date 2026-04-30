"""Small BPS Web API client used by the ETL proof phase."""

from __future__ import annotations

from dataclasses import dataclass
import json
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from bps_etl.config import BPS_BASE_URL


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


def parse_bps_list_response(payload: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Parse standard BPS list response shape: data = [metadata, rows]."""
    raw = payload.get("data")
    if isinstance(raw, list) and len(raw) >= 2 and isinstance(raw[0], dict) and isinstance(raw[1], list):
        return raw[0], raw[1]
    return {}, []


class BPSClient:
    """Minimal stdlib-only BPS API client.

    The project intentionally keeps the Fase 1 client simple so API behavior is
    transparent and easy to audit.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = BPS_BASE_URL,
        timeout: int = 30,
        retries: int = 2,
        retry_backoff: float = 1.0,
    ) -> None:
        if not api_key:
            raise ValueError("api_key is required")
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self.retries = retries
        self.retry_backoff = retry_backoff

    def request(self, bps_request: BPSRequest) -> dict[str, Any]:
        params = build_query_params(bps_request, api_key=self.api_key)
        url = f"{self.base_url}?{urlencode(params)}"
        req = Request(url, headers={"User-Agent": "etl-bps-dashboard-analitik/0.1"})
        last_error: Exception | None = None

        for attempt in range(self.retries + 1):
            try:
                with urlopen(req, timeout=self.timeout) as response:
                    return json.loads(response.read().decode("utf-8"))
            except HTTPError as exc:
                last_error = exc
                retryable = exc.code == 429 or exc.code >= 500
                if not retryable:
                    raise RuntimeError(f"BPS request failed with permanent HTTP {exc.code}: {exc.reason}") from exc
                if attempt >= self.retries:
                    break
                if self.retry_backoff > 0:
                    time.sleep(self.retry_backoff * (2 ** attempt))
            except (TimeoutError, URLError) as exc:
                last_error = exc
                if attempt >= self.retries:
                    break
                if self.retry_backoff > 0:
                    time.sleep(self.retry_backoff * (2 ** attempt))

        raise RuntimeError(f"BPS request failed after {self.retries + 1} attempts: {last_error}")

    def list_rows(
        self,
        model: str,
        *,
        domain: str = "0000",
        params: dict[str, Any] | None = None,
        max_pages: int | None = None,
    ) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        """Fetch all pages for BPS list-style metadata endpoints."""
        page = 1
        all_rows: list[dict[str, Any]] = []
        first_meta: dict[str, Any] = {}

        while True:
            payload = self.request(BPSRequest(model=model, domain=domain, params={**(params or {}), "page": page}))
            meta, rows = parse_bps_list_response(payload)
            if page == 1:
                first_meta = meta
            all_rows.extend(rows)

            total_pages = int(meta.get("pages") or 1)
            if max_pages is not None:
                total_pages = min(total_pages, max_pages)
            if page >= total_pages:
                break
            page += 1

        return first_meta, all_rows

    def dynamic_data(self, var_id: int, th_id: int, *, domain: str = "0000") -> dict[str, Any]:
        """Fetch dynamic table data for one variable and one BPS period id."""
        return self.request(BPSRequest(model="data", domain=domain, params={"var": var_id, "th": th_id}))
