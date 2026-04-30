"""Transform BPS dynamic table payloads into load-ready normalized rows."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from bps_etl.extract.dynamic_data import build_datacontent_key_index, clean_label


DIMENSION_TABLES = ("dim_indikator", "dim_wilayah", "dim_waktu", "dim_turvar", "dim_turtahun")
FACT_GRAIN_FIELDS = ("var_id", "kode_wilayah", "th_id", "turvar_id", "turth_id", "source_domain")


@dataclass(frozen=True)
class TransformResult:
    """Normalized rows and quality metrics for one BPS dynamic-data payload."""

    fact_rows: list[dict[str, Any]]
    dimensions: dict[str, list[dict[str, Any]]]
    quality: dict[str, Any]
    unmatched_keys: list[str]


def normalize_numeric_value(value: object) -> float | None:
    """Convert Indonesian/standard numeric value to float, returning None if invalid."""
    if value is None:
        return None
    try:
        return float(str(value).replace(",", ".").strip())
    except ValueError:
        return None


def _first(values: Any) -> dict[str, Any]:
    return values[0] if isinstance(values, list) and values and isinstance(values[0], dict) else {}


def _as_int(value: object) -> int | None:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


def infer_region_level(kode_wilayah: object) -> str:
    """Infer coarse BPS area level from `vervar.val`.

    This intentionally stays conservative. It only labels national, province,
    and kabupaten/kota patterns needed by the committed BPS artifacts; unknown
    codes stay explicit instead of being over-claimed.
    """
    code = str(kode_wilayah).strip()
    if code in {"0", "00", "0000", "9999"}:
        return "nasional"
    if len(code) == 4 and code.endswith("00"):
        return "provinsi"
    if len(code) == 4 and code.isdigit():
        return "kabupaten_kota"
    return "unknown"


def fact_grain(row: dict[str, Any]) -> tuple[Any, ...]:
    return tuple(row[field] for field in FACT_GRAIN_FIELDS)


def _empty_dimensions() -> dict[str, list[dict[str, Any]]]:
    return {name: [] for name in DIMENSION_TABLES}


def _quality_gate(quality: dict[str, int]) -> str:
    passed = (
        quality["raw_datacontent_count"] > 0
        and quality["decoded_count"] == quality["raw_datacontent_count"]
        and quality["unmatched_count"] == 0
        and quality["duplicate_fact_key_count"] == 0
        and quality["null_value_count"] == 0
    )
    return "passed" if passed else "failed"


def _unique_rows(rows: list[dict[str, Any]], key_fields: tuple[str, ...]) -> list[dict[str, Any]]:
    seen: set[tuple[Any, ...]] = set()
    unique: list[dict[str, Any]] = []
    for row in rows:
        key = tuple(row.get(field) for field in key_fields)
        if key in seen:
            continue
        seen.add(key)
        unique.append(row)
    return unique


def transform_dynamic_payload(
    payload: dict[str, Any],
    *,
    indicator_key: str,
    theme: str = "",
    source_domain: str = "0000",
    artifact_path: str = "",
    snapshot_id: str = "",
) -> TransformResult:
    """Decode one BPS `model=data` payload into fact/dimension rows.

    The decoder uses the verified BPS composite key rule:
    `vervar.val + var.val + turvar.val + tahun.val + turtahun.val`.
    """
    datacontent = payload.get("datacontent") or {}
    if not isinstance(datacontent, dict):
        datacontent = {}

    key_index = build_datacontent_key_index(payload)
    var_meta = _first(payload.get("var"))
    fact_rows: list[dict[str, Any]] = []
    unmatched_keys: list[str] = []
    dimensions = _empty_dimensions()
    decoded_rows: list[dict[str, Any]] = []
    null_value_count = 0

    for data_key, raw_value in sorted(datacontent.items()):
        dims = key_index.get(str(data_key))
        if dims is None:
            unmatched_keys.append(str(data_key))
            continue

        decoded_rows.append(dims)
        nilai = normalize_numeric_value(raw_value)
        if nilai is None:
            null_value_count += 1
            continue

        fact_rows.append(
            {
                "indicator_key": indicator_key,
                "var_id": dims["var_id"],
                "kode_wilayah": dims["kode_wilayah"],
                "th_id": dims["th_id"],
                "turvar_id": dims["turvar_id"],
                "turth_id": dims["turth_id"],
                "data_key": str(data_key),
                "source_domain": source_domain,
                "nilai": nilai,
                "last_update": payload.get("last_update"),
                "artifact_path": artifact_path,
                "snapshot_id": snapshot_id,
            }
        )

    if decoded_rows:
        dimensions["dim_indikator"].append(
            {
                "var_id": int(var_meta.get("val") or decoded_rows[0]["var_id"]),
                "indicator_key": indicator_key,
                "nama_indikator": clean_label(var_meta.get("label") or decoded_rows[0].get("indikator")),
                "unit": clean_label(var_meta.get("unit") or decoded_rows[0].get("unit")),
                "subject": clean_label(var_meta.get("subj") or decoded_rows[0].get("subject")),
                "theme": theme,
                "definisi": clean_label(var_meta.get("def")),
                "catatan": clean_label(var_meta.get("note")),
                "decimal_places": _as_int(var_meta.get("decimal")),
                "source_model": "data.var",
            }
        )

    for dims in decoded_rows:
        year = _as_int(dims.get("tahun"))
        dimensions["dim_wilayah"].append(
            {
                "kode_wilayah": dims["kode_wilayah"],
                "nama_wilayah": dims["nama_wilayah"],
                "level_wilayah": infer_region_level(dims["kode_wilayah"]),
                "group_ver_id": None,
                "group_ver_name": None,
                "source_model": "data.vervar",
            }
        )
        dimensions["dim_waktu"].append(
            {
                "th_id": dims["th_id"],
                "tahun": year,
                "periode_label": str(dims.get("tahun") or ""),
                "source_model": "data.tahun",
            }
        )
        dimensions["dim_turvar"].append(
            {
                "turvar_id": dims["turvar_id"],
                "turvar_label": dims["turvar_label"] or "Tidak ada",
                "group_turvar_id": None,
                "group_turvar_name": None,
                "source_model": "data.turvar",
            }
        )
        dimensions["dim_turtahun"].append(
            {
                "turth_id": dims["turth_id"],
                "turth_label": dims["turth_label"] or "Tahun",
                "group_turth_id": None,
                "group_turth_name": None,
                "source_model": "data.turtahun",
            }
        )

    dimensions["dim_indikator"] = _unique_rows(dimensions["dim_indikator"], ("var_id",))
    dimensions["dim_wilayah"] = _unique_rows(dimensions["dim_wilayah"], ("kode_wilayah",))
    dimensions["dim_waktu"] = _unique_rows(dimensions["dim_waktu"], ("th_id",))
    dimensions["dim_turvar"] = _unique_rows(dimensions["dim_turvar"], ("turvar_id",))
    dimensions["dim_turtahun"] = _unique_rows(dimensions["dim_turtahun"], ("turth_id",))

    grain_counts: dict[tuple[Any, ...], int] = {}
    for row in fact_rows:
        grain = fact_grain(row)
        grain_counts[grain] = grain_counts.get(grain, 0) + 1
    duplicate_fact_key_count = sum(count - 1 for count in grain_counts.values() if count > 1)

    quality = {
        "raw_datacontent_count": len(datacontent),
        "decoded_count": len(decoded_rows),
        "fact_row_count": len(fact_rows),
        "unmatched_count": len(unmatched_keys),
        "duplicate_fact_key_count": duplicate_fact_key_count,
        "null_value_count": null_value_count,
    }
    quality["quality_gate"] = _quality_gate(quality)

    return TransformResult(fact_rows=fact_rows, dimensions=dimensions, quality=quality, unmatched_keys=unmatched_keys)
