# Database Schema — Fase 2

Status: **approved design candidate** untuk implementasi load layer pada Fase 5.

Schema fisik disimpan di:

```text
src/bps_etl/load/schema.sql
```

## Tujuan Schema

Schema ini dirancang untuk menyimpan hasil ETL data sosial ekonomi dari Web API BPS secara terstruktur, auditable, dan siap dipakai dashboard. Desainnya mengikuti temuan Fase 1: data asli BPS berasal dari `model=data`, menggunakan `th_id` dari `model=th`, dan nilai statistik berada pada `datacontent` yang harus didecode melalui metadata.

## Ringkasan Tabel

| Tabel | Jenis | Fungsi |
|---|---|---|
| `dim_indikator` | Dimension | Metadata indikator BPS (`var_id`, label, unit, subject, theme). |
| `dim_wilayah` | Dimension | Metadata wilayah/kategori vertikal dari `vervar`. |
| `dim_waktu` | Dimension | Mapping `th_id` BPS ke tahun kalender. |
| `dim_turvar` | Dimension | Kategori turunan variabel, misalnya Perkotaan/Perdesaan/Jumlah. |
| `dim_turtahun` | Dimension | Kategori turunan waktu, misalnya Februari/Agustus/Tahunan. |
| `fact_statistik` | Fact | Nilai statistik hasil decode `datacontent`. |
| `raw_api_snapshot` | Audit | Pointer artifact raw API commit-safe, bukan penyimpanan secret. |
| `etl_run_log` | Audit | Catatan eksekusi ETL dan jumlah baris. |

## Primary Key dan Unique Key

| Tabel | Primary Key | Unique Key Tambahan |
|---|---|---|
| `dim_indikator` | `var_id` | `indicator_key`; `(var_id, indicator_key)` |
| `dim_wilayah` | `kode_wilayah` | - |
| `dim_waktu` | `th_id` | `tahun` |
| `dim_turvar` | `turvar_id` | - |
| `dim_turtahun` | `turth_id` | - |
| `fact_statistik` | `fact_id` | `data_key`; `(var_id, kode_wilayah, th_id, turvar_id, turth_id, source_domain)` |
| `raw_api_snapshot` | `snapshot_id` | - |
| `etl_run_log` | `run_id` | - |

## Foreign Key

`fact_statistik` memiliki relasi ke semua dimensi utama:

```text
fact_statistik.var_id       → dim_indikator.var_id
fact_statistik.(var_id, indicator_key) → dim_indikator.(var_id, indicator_key)
fact_statistik.kode_wilayah → dim_wilayah.kode_wilayah
fact_statistik.th_id        → dim_waktu.th_id
fact_statistik.turvar_id    → dim_turvar.turvar_id
fact_statistik.turth_id     → dim_turtahun.turth_id
fact_statistik.run_id       → etl_run_log.run_id
raw_api_snapshot.run_id     → etl_run_log.run_id
```

Relasi ini membuat dashboard tidak membaca label dari raw JSON, tetapi dari tabel dimensi yang sudah dinormalisasi.

## Grain Fact Table

Satu baris pada `fact_statistik` merepresentasikan satu nilai statistik pada kombinasi:

```text
var_id + kode_wilayah + th_id + turvar_id + turth_id + source_domain
```

Contoh dari Fase 1:

```text
var_id=192, kode_wilayah=1100, th_id=123, turvar_id=434, turth_id=63
```

Artinya: indikator kemiskinan untuk ACEH tahun 2023 kategori Jumlah dan periode Tahunan/Semester terkait sesuai metadata BPS.

## Aturan Idempotensi

Load layer pada Fase 5 harus memakai pola upsert berdasarkan unique key fact. Tujuannya agar ETL bisa dijalankan ulang tanpa menggandakan baris.

Recommended upsert target:

```text
UNIQUE (var_id, kode_wilayah, th_id, turvar_id, turth_id, source_domain)
```

`data_key` tetap disimpan sebagai bukti langsung dari BPS dan juga dibuat unique karena key tersebut adalah composite key asli dari `datacontent`.

## Audit Trail

`raw_api_snapshot` tidak menyimpan API key atau signed URL. Tabel ini hanya menyimpan pointer artifact, misalnya:

```text
results/api/dynamic_poverty_rate_2023.json
```

`etl_run_log` menyimpan status run, jumlah indikator, jumlah raw snapshot, jumlah fact rows, error message jika gagal, dan commit sumber.

Audit counters (`indicator_count`, `raw_snapshot_count`, `fact_row_count`, `row_count`) diberi `CHECK >= 0` agar nilai jumlah baris tidak negatif. `run_id` pada fact dan snapshot bersifat nullable untuk mendukung staging/manual artifact, tetapi jika diisi wajib merujuk ke `etl_run_log`.

## Scope Decision: `dim_waktu.tahun UNIQUE`

Fase 1 menunjukkan `th_id` 121/122/123 konsisten untuk 2021/2022/2023 pada indikator terpilih. Karena itu Fase 2 memakai `tahun UNIQUE` agar dashboard time dimension sederhana. Jika Fase 3 menemukan variasi `th_id` berbeda untuk tahun yang sama pada domain/subject tertentu, schema perlu direvisi menjadi grain waktu yang menyertakan `source_domain` atau `calendar_scope`.

## Validasi Fase 2

Schema divalidasi oleh test otomatis yang menjalankan DDL di SQLite memory database dan memeriksa:

1. seluruh tabel target terbentuk,
2. primary key/unique index tersedia,
3. foreign key pada `fact_statistik` aktif,
4. sample insert valid bisa dilakukan,
5. duplicate fact dan duplicate `data_key` ditolak,
6. pasangan `var_id` dan `indicator_key` pada fact konsisten,
7. audit counters negatif ditolak.
