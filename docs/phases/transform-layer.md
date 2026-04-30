# Transform Layer — Fase 4

Status: **approved implementation**.

Fase 4 mengubah raw `model=data` snapshots dari Fase 3 menjadi output transform yang siap untuk Fase 5 Load Layer. Fase ini belum membuat database SQLite dan belum menampilkan grafik statistik di dashboard.

## Input

| Artifact | Purpose |
|---|---|
| `results/api/extract/extract_manifest.json` | Daftar raw snapshots Fase 3 |
| `results/api/extract/data/*.json` | Payload BPS `model=data` commit-safe |
| `results/api/selected_indicators.json` | Mapping `var_id`, `indicator_key`, tema, tahun target |

## Decoder Rule

`datacontent` didecode dengan aturan komposit BPS yang sudah dibuktikan di Fase 1:

```text
vervar.val + var.val + turvar.val + tahun.val + turtahun.val
```

Implementasi tidak memakai slicing posisi tetap. Decoder membangun lookup dari seluruh kombinasi metadata lalu mencocokkan key `datacontent` secara exact.

## Output

| Artifact | Description |
|---|---|
| `results/tables/transform/fact_statistik_preview.csv` | Preview load-ready rows untuk `fact_statistik` |
| `results/tables/transform/dimensions_preview.json` | Preview rows untuk dimensi indikator, wilayah, waktu, turvar, turtahun |
| `results/tables/transform/transform_quality_metrics.json` | Ringkasan quality gate transform |
| `results/tables/transform/unmatched_datacontent_keys.json` | Daftar unmatched keys, kosong jika gate lulus |
| `results/tables/transform/transform_manifest.json` | Manifest Fase 4 dan ringkasan per snapshot |

## Run Summary

| Metric | Value |
|---|---:|
| Captured at | `2026-04-30T03:25:00Z` |
| Dynamic snapshots transformed | 12 |
| Raw datacontent keys | 2490 |
| Decoded keys | 2490 |
| Fact preview rows | 2490 |
| Unmatched keys | 0 |
| Duplicate fact grains | 0 |
| Null/non-numeric values | 0 |
| Quality gate | `passed` |

## Dimension Preview Counts

| Dimension | Rows |
|---|---:|
| `dim_indikator` | 4 |
| `dim_wilayah` | 553 |
| `dim_waktu` | 3 |
| `dim_turvar` | 4 |
| `dim_turtahun` | 5 |

## Reproduce

```bash
python3 scripts/run_etl.py --phase transform --mode quick
```

Transform quick mode berjalan offline dari artifact Fase 3 yang sudah committed dan tidak membutuhkan live BPS API key.

Validation:

```bash
python3 -m py_compile scripts/*.py
python3 -m pytest -q
python3 -m json.tool results/tables/transform/transform_manifest.json >/dev/null
python3 -m json.tool results/tables/transform/transform_quality_metrics.json >/dev/null
python3 -m json.tool results/tables/transform/dimensions_preview.json >/dev/null
```

## Phase Boundary

Fase 4 tidak mengklaim database load atau dashboard analitik selesai. Output ini adalah preview transform yang akan dipakai Fase 5 untuk load ke SQLite.

## Review Result

Codex lecturer/technical review: **93/100 — APPROVED** (`docs/reviews/REVIEW_phase4_transform_layer.md`).

Post-review improvements applied:

1. Added a duplicate-fact-grain regression test across two synthetic snapshots.
2. Documented that transform quick mode runs offline from committed Fase 3 artifacts and does not require a live BPS API key.
3. Documented that `artifact_path` and `snapshot_id` in fact preview are Fase 4 audit helper columns for Fase 5 mapping/ignore decisions.

`artifact_path` and `snapshot_id` are audit helper columns in the Fase 4 preview. The Fase 5 load layer can either ignore them for `fact_statistik` or map them through audit/load metadata.
