# Extract Layer — Fase 3

Status: **approved implementation**.

Fase 3 mengubah proof Fase 1 menjadi extract layer yang bisa dijalankan ulang. Output masih berupa raw snapshot dan manifest; transform/load/dashboard statistik tetap berada di Fase 4–6.

## Entry Point

```bash
python3 scripts/run_etl.py --phase extract --mode quick
```

Mode `quick` membaca target dari:

```text
results/api/selected_indicators.json
```

## Komponen

| Komponen | Path | Fungsi |
|---|---|---|
| BPS client | `src/bps_etl/extract/client.py` | Request Web API BPS dengan timeout dan retry. |
| Target planner | `src/bps_etl/extract/metadata.py` | Membuat target extract dari `indicator_key`, `var_id`, tahun, dan `th_id`. |
| Snapshot writer | `src/bps_etl/extract/snapshot.py` | Menyimpan raw API payload secara commit-safe tanpa API key. |
| Extract pipeline | `src/bps_etl/extract/pipeline.py` | Mengambil metadata + dynamic data lalu menulis manifest. |
| Runner | `scripts/run_etl.py` | CLI untuk menjalankan Fase 3. |

## Request Scope

Fase 3 mengambil:

- metadata models: `th`, `vervar`, `turvar`, `turth`, `unit`
- dynamic data model: `data`
- domain: `0000`
- target indikator: 4 indikator dari Fase 1
- target tahun: 2021, 2022, 2023

`model=data` tetap memakai `th_id`, bukan literal tahun.

## Output Snapshot

Folder output:

```text
results/api/extract/
```

Manifest:

```text
results/api/extract/extract_manifest.json
```

Ringkasan run terakhir:

| Metric | Value |
|---|---:|
| Target dynamic data | 12 |
| Metadata snapshots | 20 |
| Dynamic snapshots | 12 |
| Total snapshots | 32 |
| Total raw rows/keys | 3642 |
| Captured at | `2026-04-29T16:35:03Z` |

## Security Rules

- API key hanya dibaca dari `.env` atau environment variable `BPS_API_KEY`.
- Snapshot tidak menyimpan query param `key`.
- Manifest menyimpan sanitized params, request fingerprint, path artifact relatif, checksum SHA-256, dan row count.
- `.env` tetap ignored dan tidak boleh masuk Git.

## Validation

Test coverage Fase 3 mencakup:

1. client retry saat transient `URLError`,
2. request fingerprint stabil dan mengecualikan API key,
3. snapshot writer tidak menyimpan key,
4. target planner membaca `period_ids` dari Fase 1,
5. pipeline menulis metadata + dynamic snapshots dan manifest,
6. CLI parser mendukung `--phase extract --mode quick`.

## Review Result

Fase 3 review: **91/100 — APPROVED** (`docs/REVIEW_phase3_extract_layer.md`). Cheap fixes from the review were applied before commit: permanent HTTP client errors are not retried, dashboard copy is current, target planner has a missing-`period_ids` regression test, and manifest entries include `artifact_group`.
