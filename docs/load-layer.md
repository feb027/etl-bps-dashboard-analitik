# Load Layer — Fase 5

Status: **implemented, pending review**.

Fase 5 memuat output transform Fase 4 ke SQLite lokal. Database berada di path ignored `data/database/bps_etl.sqlite`, sedangkan ringkasan commit-safe disimpan di `results/database/load_metrics.json`.

## Input

| Artifact | Purpose |
|---|---|
| `results/tables/transform/fact_statistik_preview.csv` | Fact rows hasil transform |
| `results/tables/transform/dimensions_preview.json` | Dimension rows hasil transform |
| `results/tables/transform/transform_manifest.json` | Quality gate/source transform manifest |
| `results/api/extract/extract_manifest.json` | Raw snapshot audit metadata |
| `src/bps_etl/load/schema.sql` | SQLite schema Fase 2 |

## Output

| Artifact | Description |
|---|---|
| `data/database/bps_etl.sqlite` | SQLite database lokal, ignored dari git |
| `results/database/load_metrics.json` | Commit-safe load summary dan table counts |

## Run Summary

| Metric | Value |
|---|---:|
| Evidence source | `results/database/load_metrics.json` |
| Metrics generated at | `2026-04-30T03:49:38Z` |
| `dim_indikator` rows | 4 |
| `dim_wilayah` rows | 553 |
| `dim_waktu` rows | 3 |
| `dim_turvar` rows | 4 |
| `dim_turtahun` rows | 5 |
| `fact_statistik` rows | 2490 |
| `raw_api_snapshot` rows | 32 |
| `etl_run_log` rows | 1 |

## Idempotency

Load layer memakai upsert keys:

| Table | Idempotent key |
|---|---|
| `fact_statistik` | `var_id + kode_wilayah + th_id + turvar_id + turth_id + source_domain` |
| `raw_api_snapshot` | `snapshot_id` |
| Dimension tables | Primary key masing-masing dimensi |

Tes membuktikan rerun tidak menggandakan fact/dimension/raw snapshot rows. `etl_run_log` bertambah satu row per run sebagai audit trail.

## Reproduce

```bash
python3 scripts/run_etl.py --phase load --mode quick --database-path data/database/bps_etl.sqlite --metrics-path results/database/load_metrics.json
```

Validation:

```bash
python3 -m py_compile scripts/*.py
python3 -m pytest -q
python3 -m json.tool results/database/load_metrics.json >/dev/null
```

## Phase Boundary

Fase 5 tidak mengklaim dashboard chart/grafik selesai. Database sudah terisi, tetapi dashboard statistik/charts tetap dijadwalkan untuk Fase 6.
