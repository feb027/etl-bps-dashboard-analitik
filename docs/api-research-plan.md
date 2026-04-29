# BPS API Research Plan

## Objective

Prove the correct way to retrieve and normalize dynamic table data from BPS Web API before implementing the full ETL pipeline.

## Endpoint Base

```text
https://webapi.bps.go.id/v1/api/list
```

## Models to Verify

| Model | Purpose | Required Evidence |
|---|---|---|
| `var` | daftar variabel/indikator | response sample + selected var_id |
| `th` | daftar periode/tahun | `th_id` to year mapping |
| `vervar` | variabel vertikal/wilayah/kategori | mapping sample |
| `turvar` | turunan variabel | mapping sample |
| `turth` | turunan periode | mapping sample |
| `data` | data statistik | real `datacontent` sample |

## Initial Indicator Themes

- Kemiskinan
- Pendidikan
- Ketenagakerjaan
- IPM/pembangunan manusia
- Kependudukan

Final `var_id` must be selected from API evidence.

## Expected Artifacts

```text
results/api/bps_api_probe_summary.json
results/api/selected_indicators.json
results/api/sample_dynamic_response.json
results/tables/bps_api_probe_results.csv
results/tables/normalized_sample.csv
reports/progress-1-api-research.md
```

## Key Risk from Old Repo

The old repo assumed `th=2021:2023`, but BPS dynamic data uses `th_id` for `model=data`. Fase 1 must document this clearly.
