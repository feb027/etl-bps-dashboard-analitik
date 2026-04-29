# Progress 2 — ETL Architecture & Schema

## Status

Fase 2 menyelesaikan desain arsitektur ETL, schema SQLite, data dictionary, transform rules, dan validation test untuk memastikan schema dapat dijalankan sebelum implementasi Extract/Transform/Load penuh.

## Input dari Fase 1

Fase 1 menghasilkan bukti API berikut:

| Evidence | Value |
|---|---:|
| Indikator valid | 4 |
| Probe rows | 12 |
| Normalized records | 2490 |
| Unmatched `datacontent` keys | 0 |

Temuan yang menjadi dasar desain:

1. `model=data` membutuhkan `th_id` dari `model=th`.
2. `datacontent` harus didecode dengan composite key `vervar + var + turvar + tahun + turtahun`.
3. `turvar` dan `turtahun` perlu menjadi dimensi karena beberapa indikator memiliki kategori tambahan.
4. Pipeline harus fail jika output fact kosong atau decode tidak lengkap.

## Artifact Fase 2

| Artifact | Fungsi |
|---|---|
| `docs/etl-architecture.md` | Desain alur ETL dan layer responsibilities. |
| `docs/database-schema.md` | Penjelasan schema SQLite, key, FK, grain, dan audit trail. |
| `docs/transform-rules.md` | Aturan decode, dimension extraction, fact construction, dan data quality gates. |
| `docs/data-dictionary.md` | Data dictionary lengkap per tabel dan field. |
| `src/bps_etl/load/schema.sql` | DDL SQLite untuk Fase 5 load layer. |
| `src/bps_etl/load/models.py` | Metadata tabel dan schema path helper. |
| `tests/test_schema.py` | Validasi executable schema di SQLite memory database. |

## Schema Ringkas

| Tabel | Jenis | Key Utama |
|---|---|---|
| `dim_indikator` | Dimension | `var_id` |
| `dim_wilayah` | Dimension | `kode_wilayah` |
| `dim_waktu` | Dimension | `th_id` |
| `dim_turvar` | Dimension | `turvar_id` |
| `dim_turtahun` | Dimension | `turth_id` |
| `fact_statistik` | Fact | `fact_id`, unique grain statistik |
| `raw_api_snapshot` | Audit | `snapshot_id` |
| `etl_run_log` | Audit | `run_id` |

Unique grain fact:

```text
var_id + kode_wilayah + th_id + turvar_id + turth_id + source_domain
```

## Validasi

Fase 2 menambahkan test schema yang memeriksa:

1. semua tabel target dibuat,
2. foreign key fact tersedia,
3. unique index fact tersedia,
4. sample insert valid berhasil,
5. duplicate fact ditolak,
6. duplicate `data_key` ditolak,
7. pasangan `var_id` dan `indicator_key` harus konsisten,
8. audit counters negatif ditolak.

Validation commands:

```bash
python3 -m py_compile scripts/*.py
python3 -m pytest -q
python3 -m json.tool dashboard/data/dashboard-data.json >/dev/null
python3 -m json.tool results/api/bps_api_probe_summary.json >/dev/null
python3 -m json.tool results/api/metadata_endpoint_evidence.json >/dev/null
```

## Batas Fase 2

Fase 2 belum menjalankan ETL ke database produksi. Tahap berikutnya:

1. Fase 3 — implementasi extract layer lengkap.
2. Fase 4 — implementasi transform production dan data quality metrics.
3. Fase 5 — implementasi load layer SQLite dan idempotent upsert.
