"""Decode BPS dynamic table `datacontent` into auditable tabular records."""

from __future__ import annotations

import re
from typing import Any


def is_datacontent_response(payload: dict[str, Any]) -> bool:
    """Return True if a payload looks like a BPS dynamic data response."""
    return isinstance(payload, dict) and isinstance(payload.get("datacontent"), dict)


def clean_label(value: object) -> str:
    """Remove simple HTML tags/entities often present in BPS labels."""
    if value is None:
        return ""
    text = str(value)
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("&nbsp;", " ").replace("\xa0", " ")
    return re.sub(r"\s+", " ", text).strip()


def _dimension_values(payload: dict[str, Any], name: str) -> list[dict[str, Any]]:
    values = payload.get(name)
    return values if isinstance(values, list) else []


def build_datacontent_key_index(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Build lookup for BPS datacontent composite keys.

    Empirical Fase 1 finding: BPS dynamic data keys are concatenations of:

    `vervar.val + var.val + turvar.val + tahun.val + turtahun.val`

    The values have variable widths, so direct slicing is unsafe. We generate
    all metadata combinations and match exact key strings.
    """
    var_values = _dimension_values(payload, "var")
    vervar_values = _dimension_values(payload, "vervar")
    turvar_values = _dimension_values(payload, "turvar") or [{"val": "0", "label": "Tidak ada"}]
    tahun_values = _dimension_values(payload, "tahun")
    turtahun_values = _dimension_values(payload, "turtahun") or [{"val": "0", "label": "Tahun"}]

    index: dict[str, dict[str, Any]] = {}
    for vervar in vervar_values:
        for var in var_values:
            for turvar in turvar_values:
                for tahun in tahun_values:
                    for turtahun in turtahun_values:
                        key = "".join(
                            str(part.get("val"))
                            for part in (vervar, var, turvar, tahun, turtahun)
                        )
                        if key in index:
                            raise ValueError(
                                "Duplicate BPS datacontent composite key generated: "
                                f"{key}. Decoder cannot safely map this response."
                            )
                        index[key] = {
                            "kode_wilayah": str(vervar.get("val")),
                            "nama_wilayah": clean_label(vervar.get("label")),
                            "var_id": int(var.get("val")),
                            "indikator": clean_label(var.get("label")),
                            "unit": clean_label(var.get("unit")),
                            "subject": clean_label(var.get("subj")),
                            "turvar_id": str(turvar.get("val")),
                            "turvar_label": clean_label(turvar.get("label")),
                            "th_id": int(tahun.get("val")),
                            "tahun": clean_label(tahun.get("label")),
                            "turth_id": str(turtahun.get("val")),
                            "turth_label": clean_label(turtahun.get("label")),
                        }
    return index


def decode_datacontent(payload: dict[str, Any], *, indicator_key: str, domain: str = "0000") -> tuple[list[dict[str, Any]], list[str]]:
    """Decode BPS datacontent into normalized records and unmatched keys."""
    datacontent = payload.get("datacontent") or {}
    if not isinstance(datacontent, dict):
        return [], []

    key_index = build_datacontent_key_index(payload)
    records: list[dict[str, Any]] = []
    unmatched: list[str] = []
    last_update = payload.get("last_update")

    for data_key, value in sorted(datacontent.items()):
        dims = key_index.get(str(data_key))
        if dims is None:
            unmatched.append(str(data_key))
            continue
        records.append(
            {
                "indicator_key": indicator_key,
                "data_key": str(data_key),
                "source_domain": domain,
                "last_update": last_update,
                **dims,
                "nilai": value,
            }
        )
    return records, unmatched
