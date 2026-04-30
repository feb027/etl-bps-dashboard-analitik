# Progress Fase 6.1 — Data Expansion

## Status

Fase 6.1 **implemented**. Scope data diperluas dari proof dashboard awal menjadi 6 indikator sosial-ekonomi, 4 tahun, dan 4.292 fact rows. Semua output dashboard tetap digenerate dari SQLite lokal hasil ETL, tanpa dummy/fake data.

## Scope Perluasan

- Tahun target: 2021, 2022, 2023, 2024.
- Indikator target: 6 indikator dari Web API BPS pusat.
- Pipeline rerun end-to-end: API probe → extract → transform → load → dashboard generator.
- Dashboard JSON dan screenshot evidence diperbarui dari hasil load terbaru.

## Indikator

| Key | var_id | Tema | Peran |
|---|---:|---|---|
| `poverty_rate` | 192 | Kemiskinan | Indikator kemiskinan sosial-ekonomi |
| `open_unemployment_rate` | 543 | Ketenagakerjaan | Indikator pasar kerja |
| `mean_years_schooling_new_method` | 415 | Pendidikan | Indikator pendidikan/IPM |
| `human_development_index_new_method` | 494 | Pembangunan Manusia | Indikator pembangunan manusia |
| `gini_ratio` | 98 | Ketimpangan | Indikator ketimpangan pendapatan |
| `regional_gdp_growth_constant_2010` | 291 | Ekonomi Regional | Indikator pertumbuhan ekonomi wilayah |

## Data Evidence

| Metric | Value |
|---|---:|
| API probe rows | 24 |
| Normalized records | 4.292 |
| Extract targets | 24 |
| Metadata snapshots | 30 |
| Dynamic snapshots | 24 |
| Total snapshots | 54 |
| Total raw rows/keys | 5.744 |
| Transform fact rows | 4.292 |
| Transform unmatched keys | 0 |
| Duplicate fact grains | 0 |
| Null/non-numeric values | 0 |
| SQLite indicators | 6 |
| SQLite regions | 579 |
| SQLite years | 4 |
| SQLite fact rows | 4.292 |
| Raw snapshot audit rows | 54 |
| Dashboard table rows | 4.292 |

## Artifact Utama

- `results/api/selected_indicators.json`
- `results/api/bps_api_probe_summary.json`
- `results/api/extract/extract_manifest.json`
- `results/tables/transform/transform_quality_metrics.json`
- `results/tables/transform/transform_manifest.json`
- `results/database/load_metrics.json`
- `dashboard/data/dashboard-data.json`
- `results/figures/dashboard-phase6-full.png`

## Commands

```bash
python3 scripts/verify_bps_api.py
python3 scripts/run_etl.py --phase extract --mode quick
python3 scripts/run_etl.py --phase transform --mode quick
python3 scripts/run_etl.py --phase load --mode quick
python3 scripts/generate_dashboard_data.py
```

## Validation

```bash
python3 -m py_compile scripts/*.py
python3 -m pytest -q
python3 -m json.tool dashboard/data/dashboard-data.json >/dev/null
python3 -m json.tool results/api/bps_api_probe_summary.json >/dev/null
python3 -m json.tool results/api/extract/extract_manifest.json >/dev/null
python3 -m json.tool results/tables/transform/transform_quality_metrics.json >/dev/null
python3 -m json.tool results/database/load_metrics.json >/dev/null
node --check dashboard/scripts/*.js
git diff --check
```

## Kesimpulan

Perluasan ini membuat proyek lebih sesuai dengan judul sosial-ekonomi karena mencakup dimensi kemiskinan, ketenagakerjaan, pendidikan, pembangunan manusia, ketimpangan, dan pertumbuhan ekonomi regional. Scope tetap terkendali untuk laporan akademik dan semua klaim berbasis artifact ETL.
