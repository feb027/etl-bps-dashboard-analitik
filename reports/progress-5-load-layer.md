# Progress Fase 5 — Load Layer

## Status

Fase 5 load layer **approved**.

## What Changed

1. Menambahkan SQLite load implementation di `src/bps_etl/load/database.py`.
2. Menambahkan CLI `python3 scripts/run_etl.py --phase load --mode quick`.
3. Menambahkan tests Fase 5 di `tests/test_load_layer.py`.
4. Menjalankan load dari artifact transform Fase 4 ke `data/database/bps_etl.sqlite`.
5. Menulis metrics commit-safe di `results/database/load_metrics.json`.
6. Memperbarui dashboard agar menampilkan evidence load, tanpa membuat grafik statistik sebelum Fase 6.

## Metrics

| Table | Rows |
|---|---:|
| `dim_indikator` | 4 |
| `dim_wilayah` | 553 |
| `dim_waktu` | 3 |
| `dim_turvar` | 4 |
| `dim_turtahun` | 5 |
| `fact_statistik` | 2490 |
| `raw_api_snapshot` | 32 |
| `etl_run_log` | 1 |

## Validation

```bash
python3 -m py_compile scripts/*.py
python3 -m pytest -q
python3 scripts/run_etl.py --phase load --mode quick --database-path data/database/bps_etl.sqlite --metrics-path results/database/load_metrics.json
python3 -m json.tool results/database/load_metrics.json >/dev/null
```

Latest local result: `39 passed`.

## Notes

- Database file is intentionally not committed: `data/database/bps_etl.sqlite` is ignored by `.gitignore`.
- `results/database/load_metrics.json` is the committed evidence artifact.
- Dashboard chart arrays remain empty until Fase 6.

## Review

Codex lecturer/technical review: `92/100 — APPROVED` in `docs/REVIEW_phase5_load_layer.md`.
