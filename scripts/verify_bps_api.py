#!/usr/bin/env python3
"""Fase 1: verify BPS Web API dynamic data behavior and save evidence.

This script intentionally writes small, commit-safe evidence artifacts. It never
stores the API key or request URL containing the key.
"""

from __future__ import annotations

import csv
import json
import os
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bps_etl.config import BPS_BASE_URL
from bps_etl.extract.client import BPSClient
from bps_etl.extract.dynamic_data import decode_datacontent

RESULTS_API = ROOT / "results" / "api"
RESULTS_TABLES = ROOT / "results" / "tables"
REPORTS = ROOT / "reports"
SOURCE_LOG = ROOT / "references" / "source-log.md"

TARGET_YEARS = ["2023", "2022", "2021"]
TARGET_INDICATORS = [
    {
        "indicator_key": "poverty_rate",
        "var_id": 192,
        "theme": "Kemiskinan",
        "reason": "Persentase penduduk miskin, indikator inti sosial-ekonomi.",
    },
    {
        "indicator_key": "open_unemployment_rate",
        "var_id": 543,
        "theme": "Ketenagakerjaan",
        "reason": "Tingkat pengangguran terbuka, indikator pasar kerja.",
    },
    {
        "indicator_key": "mean_years_schooling_new_method",
        "var_id": 415,
        "theme": "Pendidikan",
        "reason": "Rata-rata lama sekolah metode baru, indikator pendidikan.",
    },
    {
        "indicator_key": "human_development_index_new_method",
        "var_id": 494,
        "theme": "Pembangunan Manusia",
        "reason": "IPM metode baru, indikator pembangunan sosial-ekonomi.",
    },
]


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"\''))


def require_api_key() -> str:
    load_env_file(ROOT / ".env")
    api_key = os.getenv("BPS_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("BPS_API_KEY is missing. Copy .env.example to .env and fill the key.")
    return api_key


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name, "") for name in fieldnames})


def period_map(client: BPSClient, var_id: int) -> dict[str, int]:
    _, periods = client.list_rows("th", params={"var": var_id})
    return {str(row.get("th")): int(row["th_id"]) for row in periods if row.get("th_id") is not None}


def collect_metadata_endpoint_evidence(client: BPSClient, selected_var_ids: set[int]) -> dict[str, Any]:
    """Collect explicit endpoint-list evidence for Fase 1 metadata models."""
    var_meta, var_rows = client.list_rows("var", max_pages=1)
    first_var_id = min(selected_var_ids)

    evidence: dict[str, Any] = {
        "note": "Explicit BPS list endpoint proof for metadata models. API key and full request URLs are intentionally omitted. Selected indicator metadata is stored in metadata_*.json from model=data responses.",
        "models_checked": ["var", "th", "vervar", "turvar", "turth", "unit"],
        "var": {
            "metadata": var_meta,
            "sample_rows": var_rows[:10],
            "sample_row_count": len(var_rows[:10]),
        },
    }

    for model in ["th", "vervar", "turvar", "turth"]:
        meta, rows = client.list_rows(model, params={"var": first_var_id})
        evidence[model] = {
            "sample_var_id": first_var_id,
            "metadata": meta,
            "sample_rows": rows[:10],
            "sample_row_count": len(rows[:10]),
        }

    unit_meta, unit_rows = client.list_rows("unit", max_pages=1)
    evidence["unit"] = {
        "metadata": unit_meta,
        "sample_rows": unit_rows[:10],
        "sample_row_count": len(unit_rows[:10]),
    }
    return evidence


def run_probe() -> dict[str, Any]:
    client = BPSClient(api_key=require_api_key(), base_url=os.getenv("BPS_BASE_URL", BPS_BASE_URL))
    RESULTS_API.mkdir(parents=True, exist_ok=True)
    RESULTS_TABLES.mkdir(parents=True, exist_ok=True)

    # Documentation proof from public docs, without using the API key.
    docs_evidence = {
        "source": "BPS Web API Documentation",
        "url": "https://webapi.bps.go.id/documentation/",
        "relevant_models": ["var", "th", "vervar", "turvar", "turth", "unit", "data"],
        "note": "Fase 1 uses official BPS dynamic data models and stores API responses without the API key.",
    }
    write_json(RESULTS_API / "bps_api_documentation_evidence.json", docs_evidence)

    selected_indicators: list[dict[str, Any]] = []
    probe_rows: list[dict[str, Any]] = []
    normalized_rows: list[dict[str, Any]] = []
    sample_dynamic_response: dict[str, Any] | None = None
    metadata_samples: dict[str, Any] = {}

    for indicator in TARGET_INDICATORS:
        indicator_key = indicator["indicator_key"]
        var_id = int(indicator["var_id"])
        year_to_th = period_map(client, var_id)
        available_target_years = [year for year in TARGET_YEARS if year in year_to_th]
        if len(available_target_years) < 3:
            raise RuntimeError(f"Indicator {indicator_key} var_id={var_id} has insufficient target years: {available_target_years}")

        metadata_samples[indicator_key] = {
            "var_id": var_id,
            "available_target_years": available_target_years,
            "period_ids": {year: year_to_th[year] for year in available_target_years},
        }

        first_payload_for_indicator: dict[str, Any] | None = None
        total_decoded = 0
        total_unmatched = 0
        label = ""
        unit = ""
        subject = ""

        for year in available_target_years:
            th_id = year_to_th[year]
            payload = client.dynamic_data(var_id, th_id)
            records, unmatched = decode_datacontent(payload, indicator_key=indicator_key, domain="0000")
            if first_payload_for_indicator is None:
                first_payload_for_indicator = payload
            if sample_dynamic_response is None:
                sample_dynamic_response = payload

            normalized_rows.extend(records)
            total_decoded += len(records)
            total_unmatched += len(unmatched)

            var_meta = (payload.get("var") or [{}])[0]
            label = var_meta.get("label", label)
            unit = var_meta.get("unit", unit)
            subject = var_meta.get("subj", subject)

            probe_rows.append(
                {
                    "indicator_key": indicator_key,
                    "theme": indicator["theme"],
                    "var_id": var_id,
                    "indicator_label": label,
                    "unit": unit,
                    "subject": subject,
                    "year": year,
                    "th_id": th_id,
                    "data_availability": payload.get("data-availability"),
                    "record_count": len(payload.get("datacontent") or {}),
                    "decoded_count": len(records),
                    "unmatched_count": len(unmatched),
                    "vervar_count": len(payload.get("vervar") or []),
                    "turvar_count": len(payload.get("turvar") or []),
                    "turth_count": len(payload.get("turtahun") or []),
                    "last_update": payload.get("last_update"),
                }
            )

            write_json(
                RESULTS_API / f"dynamic_{indicator_key}_{year}.json",
                {
                    "indicator_key": indicator_key,
                    "var_id": var_id,
                    "year": year,
                    "th_id": th_id,
                    "payload": payload,
                    "decoded_count": len(records),
                    "unmatched_keys": unmatched[:20],
                    "unmatched_count": len(unmatched),
                },
            )

        selected_indicators.append(
            {
                **indicator,
                "indicator_label": label,
                "unit": unit,
                "subject": subject,
                "target_years": available_target_years,
                "period_ids": {year: year_to_th[year] for year in available_target_years},
                "decoded_records": total_decoded,
                "unmatched_keys": total_unmatched,
            }
        )

        if first_payload_for_indicator is not None:
            write_json(
                RESULTS_API / f"metadata_{indicator_key}.json",
                {
                    "indicator_key": indicator_key,
                    "var_id": var_id,
                    "var": first_payload_for_indicator.get("var"),
                    "vervar_sample": (first_payload_for_indicator.get("vervar") or [])[:10],
                    "turvar": first_payload_for_indicator.get("turvar"),
                    "tahun": first_payload_for_indicator.get("tahun"),
                    "turtahun": first_payload_for_indicator.get("turtahun"),
                    "datacontent_key_rule": "vervar.val + var.val + turvar.val + tahun.val + turtahun.val",
                },
            )

    metadata_endpoint_evidence = collect_metadata_endpoint_evidence(
        client,
        {int(indicator["var_id"]) for indicator in TARGET_INDICATORS},
    )
    write_json(RESULTS_API / "metadata_endpoint_evidence.json", metadata_endpoint_evidence)

    write_json(RESULTS_API / "selected_indicators.json", selected_indicators)
    if sample_dynamic_response is not None:
        write_json(RESULTS_API / "sample_dynamic_response.json", sample_dynamic_response)
    write_json(RESULTS_API / "metadata_probe_samples.json", metadata_samples)

    probe_fields = [
        "indicator_key", "theme", "var_id", "indicator_label", "unit", "subject", "year", "th_id",
        "data_availability", "record_count", "decoded_count", "unmatched_count", "vervar_count",
        "turvar_count", "turth_count", "last_update",
    ]
    normalized_fields = [
        "indicator_key", "var_id", "indikator", "unit", "subject", "source_domain", "kode_wilayah",
        "nama_wilayah", "turvar_id", "turvar_label", "th_id", "tahun", "turth_id", "turth_label",
        "nilai", "data_key", "last_update",
    ]
    write_csv(RESULTS_TABLES / "bps_api_probe_results.csv", probe_rows, probe_fields)
    write_csv(RESULTS_TABLES / "normalized_sample.csv", normalized_rows, normalized_fields)

    summary = {
        "status": "success",
        "base_url": BPS_BASE_URL,
        "target_years": TARGET_YEARS,
        "indicator_count": len(selected_indicators),
        "probe_rows": len(probe_rows),
        "normalized_record_count": len(normalized_rows),
        "unmatched_key_count": sum(row["unmatched_count"] for row in probe_rows),
        "selected_indicator_keys": [item["indicator_key"] for item in selected_indicators],
        "key_findings": [
            "BPS model=data uses th_id values from model=th, not plain year strings such as 2021:2023.",
            "BPS datacontent keys are composite keys generated from vervar + var + turvar + tahun + turtahun metadata values.",
            "The selected four indicators have real dynamic data for 2021, 2022, and 2023.",
        ],
        "artifacts": {
            "selected_indicators": "results/api/selected_indicators.json",
            "sample_dynamic_response": "results/api/sample_dynamic_response.json",
            "metadata_endpoint_evidence": "results/api/metadata_endpoint_evidence.json",
            "probe_results": "results/tables/bps_api_probe_results.csv",
            "normalized_sample": "results/tables/normalized_sample.csv",
        },
    }
    write_json(RESULTS_API / "bps_api_probe_summary.json", summary)
    write_progress_report(summary, selected_indicators, probe_rows)
    update_source_log()
    return summary


def write_progress_report(summary: dict[str, Any], selected: list[dict[str, Any]], probe_rows: list[dict[str, Any]]) -> None:
    lines = [
        "# Progress 1 — BPS API Research & Proof",
        "",
        "## Status",
        "",
        "Fase 1 membuktikan perilaku dasar Web API BPS untuk dynamic data sebelum ETL penuh dibangun.",
        "",
        "## Ringkasan Hasil",
        "",
        f"- Status probe: **{summary['status']}**",
        f"- Jumlah indikator valid: **{summary['indicator_count']}**",
        f"- Tahun target: **{', '.join(summary['target_years'])}**",
        f"- Baris probe: **{summary['probe_rows']}**",
        f"- Record normalized sample: **{summary['normalized_record_count']}**",
        f"- Unmatched datacontent keys: **{summary['unmatched_key_count']}**",
        "",
        "## Temuan Penting API BPS",
        "",
        "1. `model=data` menggunakan `th_id` dari `model=th`, bukan string tahun langsung seperti `2021:2023`.",
        "2. Field `datacontent` memakai composite key: `vervar.val + var.val + turvar.val + tahun.val + turtahun.val`.",
        "3. Decode tidak boleh dilakukan dengan slicing tetap karena panjang tiap dimensi bisa berbeda.",
        "4. Decode yang aman dilakukan dengan membangun lookup dari semua kombinasi metadata response.",
        "",
        "## Indikator Terpilih",
        "",
        "| Key | var_id | Tema | Label | Tahun | Record Decoded |",
        "|---|---:|---|---|---|---:|",
    ]
    for item in selected:
        lines.append(
            f"| `{item['indicator_key']}` | {item['var_id']} | {item['theme']} | {item['indicator_label']} | "
            f"{', '.join(item['target_years'])} | {item['decoded_records']} |"
        )
    lines.extend([
        "",
        "## Artifact Evidence",
        "",
        "| Artifact | Isi |",
        "|---|---|",
        "| `results/api/bps_api_probe_summary.json` | Ringkasan hasil probe |",
        "| `results/api/selected_indicators.json` | Daftar indikator valid |",
        "| `results/api/sample_dynamic_response.json` | Contoh response dynamic data BPS |",
        "| `results/api/metadata_endpoint_evidence.json` | Bukti eksplisit endpoint metadata `var`, `th`, `vervar`, `turvar`, `turth`, `unit` |",
        "| `results/api/dynamic_*_*.json` | Evidence response per indikator/tahun |",
        "| `results/api/metadata_*.json` | Metadata dimensi per indikator |",
        "| `results/tables/bps_api_probe_results.csv` | Tabel hasil probe |",
        "| `results/tables/normalized_sample.csv` | Sample hasil decode tabular |",
        "",
        "## Implikasi untuk Fase 2",
        "",
        "- Schema harus menyimpan `th_id` dan label tahun.",
        "- Transform layer harus punya decoder composite key berbasis metadata lookup.",
        "- `turvar` dan `turtahun` perlu disimpan sebagai kategori karena beberapa indikator punya dimensi tambahan seperti Perkotaan/Perdesaan atau Februari/Agustus/Tahunan.",
        "- Dashboard harus mengambil data dari tabel hasil decode, bukan langsung dari raw `datacontent`.",
        "",
        "## Validasi",
        "",
        "Validasi dijalankan setelah implementasi:",
        "",
        "```bash",
        "python3 -m py_compile scripts/*.py",
        "python3 -m pytest -q",
        "python3 -m json.tool dashboard/data/dashboard-data.json >/dev/null",
        "python3 -m json.tool results/api/bps_api_probe_summary.json >/dev/null",
        "```",
        "",
    ])
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "progress-1-api-research.md").write_text("\n".join(lines), encoding="utf-8")


def update_source_log() -> None:
    SOURCE_LOG.write_text(
        "# Source Log\n\n"
        "| Date | Source | URL/DOI | Purpose | Status |\n"
        "|---|---|---|---|---|\n"
        "| 2026-04-29 | BPS Web API Documentation | https://webapi.bps.go.id/documentation/ | Official API model reference for `var`, `th`, `vervar`, `turvar`, `turth`, `unit`, and `data` | Checked |\n",
        encoding="utf-8",
    )


def main() -> int:
    summary = run_probe()
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
