# Data Dictionary

Status: **Fase 2 schema design**. Final implementation may add operational columns, but keys and grain are fixed for the ETL pipeline.

## Fase 1 API Finding

Dynamic data from `model=data` returns numeric values in `datacontent`. The key is a composite string generated from BPS metadata values:

```text
vervar.val + var.val + turvar.val + tahun.val + turtahun.val
```

Example for `var_id=192`: `110019243412363` decodes as wilayah `1100`, variable `192`, turvar `434`, tahun `123`, and turtahun `63`. Because each component can have different string length, the transform layer must decode by metadata lookup, not fixed-position slicing. The decoder fails fast on generated composite-key collisions so ambiguous BPS responses are not silently loaded.

## Grain Definition

Satu fact row merepresentasikan satu nilai statistik BPS pada kombinasi unik:

```text
var_id + kode_wilayah + th_id + turvar_id + turth_id + source_domain
```

`data_key` asli dari BPS tetap disimpan sebagai audit key.

## `dim_indikator`

| Field | Type | Key | Nullable | Description | Source |
|---|---|---|---|---|---|
| `var_id` | INTEGER | PK | No | ID variabel/indikator BPS. | `payload.var.val`, `model=var` |
| `indicator_key` | TEXT | UNIQUE | No | Slug internal project. | config selected indicators |
| `nama_indikator` | TEXT | - | No | Nama indikator. | `payload.var.label` |
| `unit` | TEXT | - | Yes | Satuan statistik. | `payload.var.unit`, `model=unit` |
| `subject` | TEXT | - | Yes | Subjek statistik BPS. | `payload.var.subj` |
| `theme` | TEXT | - | Yes | Tema analitik project. | config selected indicators |
| `definisi` | TEXT | - | Yes | Definisi indikator. | `payload.var.def` |
| `catatan` | TEXT | - | Yes | Catatan BPS. | `payload.var.note` |
| `decimal_places` | INTEGER | - | Yes | Jumlah desimal yang disarankan. | `payload.var.decimal` |
| `source_model` | TEXT | - | No | Model sumber metadata. | default `data.var` |
| `created_at` | TEXT | - | No | Timestamp insert. | ETL load |
| `updated_at` | TEXT | - | No | Timestamp update. | ETL load |

## `dim_wilayah`

| Field | Type | Key | Nullable | Description | Source |
|---|---|---|---|---|---|
| `kode_wilayah` | TEXT | PK | No | Kode wilayah/kategori vertikal. | `payload.vervar.val` |
| `nama_wilayah` | TEXT | - | No | Nama wilayah/kategori. | `payload.vervar.label` |
| `level_wilayah` | TEXT | - | No | Level hasil inferensi (`provinsi`, `nasional`, `kabupaten_kota`, `unknown`). | transform rule |
| `group_ver_id` | TEXT | - | Yes | ID grup vertical variable. | `model=vervar` |
| `group_ver_name` | TEXT | - | Yes | Nama grup vertical variable. | `model=vervar` |
| `source_model` | TEXT | - | No | Model sumber metadata. | default `data.vervar` |
| `created_at` | TEXT | - | No | Timestamp insert. | ETL load |
| `updated_at` | TEXT | - | No | Timestamp update. | ETL load |

## `dim_waktu`

| Field | Type | Key | Nullable | Description | Source |
|---|---|---|---|---|---|
| `th_id` | INTEGER | PK | No | ID periode BPS. | `model=th.th_id`, `payload.tahun.val` |
| `tahun` | INTEGER | UNIQUE | No | Tahun kalender. | `model=th.th`, `payload.tahun.label` |
| `periode_label` | TEXT | - | No | Label periode. | `payload.tahun.label` |
| `source_model` | TEXT | - | No | Model sumber metadata. | default `th` |
| `created_at` | TEXT | - | No | Timestamp insert. | ETL load |
| `updated_at` | TEXT | - | No | Timestamp update. | ETL load |

## `dim_turvar`

| Field | Type | Key | Nullable | Description | Source |
|---|---|---|---|---|---|
| `turvar_id` | TEXT | PK | No | ID kategori turunan variabel. | `payload.turvar.val`, `model=turvar.turvar_id` |
| `turvar_label` | TEXT | - | No | Label kategori, misalnya Perkotaan/Perdesaan/Jumlah. | `payload.turvar.label` |
| `group_turvar_id` | TEXT | - | Yes | ID grup turvar. | `model=turvar` |
| `group_turvar_name` | TEXT | - | Yes | Nama grup turvar. | `model=turvar` |
| `source_model` | TEXT | - | No | Model sumber metadata. | default `turvar` |
| `created_at` | TEXT | - | No | Timestamp insert. | ETL load |
| `updated_at` | TEXT | - | No | Timestamp update. | ETL load |

## `dim_turtahun`

| Field | Type | Key | Nullable | Description | Source |
|---|---|---|---|---|---|
| `turth_id` | TEXT | PK | No | ID kategori turunan waktu. | `payload.turtahun.val`, `model=turth.turth_id` |
| `turth_label` | TEXT | - | No | Label kategori, misalnya Februari/Agustus/Tahunan. | `payload.turtahun.label` |
| `group_turth_id` | TEXT | - | Yes | ID grup turth. | `model=turth` |
| `group_turth_name` | TEXT | - | Yes | Nama grup turth. | `model=turth` |
| `source_model` | TEXT | - | No | Model sumber metadata. | default `turth` |
| `created_at` | TEXT | - | No | Timestamp insert. | ETL load |
| `updated_at` | TEXT | - | No | Timestamp update. | ETL load |

## `fact_statistik`

| Field | Type | Key | Nullable | Description | Source |
|---|---|---|---|---|---|
| `fact_id` | INTEGER | PK | No | Surrogate key fact. | SQLite autoincrement |
| `indicator_key` | TEXT | FK pair + INDEX | No | Slug indikator untuk dashboard; harus konsisten dengan `var_id`. | config selected indicators |
| `var_id` | INTEGER | FK + FK pair | No | FK indikator. | decoded metadata |
| `kode_wilayah` | TEXT | FK | No | FK wilayah/kategori. | decoded metadata |
| `th_id` | INTEGER | FK | No | FK waktu. | decoded metadata |
| `turvar_id` | TEXT | FK | No | FK turvar. | decoded metadata |
| `turth_id` | TEXT | FK | No | FK turtahun. | decoded metadata |
| `data_key` | TEXT | UNIQUE | No | Key asli dari `datacontent`. | `datacontent` key |
| `source_domain` | TEXT | UNIQUE grain | No | Domain BPS, default nasional `0000`. | request config |
| `nilai` | REAL | - | No | Nilai statistik. | `datacontent[data_key]` |
| `last_update` | TEXT | - | Yes | Last update dari BPS. | payload |
| `loaded_at` | TEXT | - | No | Timestamp load. | ETL load |
| `run_id` | TEXT | FK | Yes | ID run ETL jika tersedia. | `etl_run_log.run_id` |

Unique grain:

```text
UNIQUE (var_id, kode_wilayah, th_id, turvar_id, turth_id, source_domain)
```

## `raw_api_snapshot`

| Field | Type | Key | Nullable | Description | Source |
|---|---|---|---|---|---|
| `snapshot_id` | TEXT | PK | No | ID snapshot artifact. | ETL extract |
| `model` | TEXT | INDEX | No | Model BPS (`data`, `th`, dll.). | request metadata |
| `var_id` | INTEGER | INDEX | Yes | ID indikator jika relevan. | request metadata |
| `th_id` | INTEGER | INDEX | Yes | ID periode jika relevan. | request metadata |
| `source_domain` | TEXT | - | No | Domain BPS. | request metadata |
| `artifact_path` | TEXT | - | No | Path artifact raw/summary. | ETL extract |
| `artifact_sha256` | TEXT | - | Yes | Checksum artifact. | ETL extract |
| `row_count` | INTEGER | CHECK >= 0 | No | Jumlah rows/key dalam artifact. | ETL extract |
| `captured_at` | TEXT | - | No | Timestamp capture. | ETL extract |
| `run_id` | TEXT | FK | Yes | ID run ETL jika tersedia. | `etl_run_log.run_id` |

## `etl_run_log`

| Field | Type | Key | Nullable | Description | Source |
|---|---|---|---|---|---|
| `run_id` | TEXT | PK | No | ID eksekusi ETL. | ETL runner |
| `phase` | TEXT | - | No | Fase/jenis run. | ETL runner |
| `status` | TEXT | CHECK | No | `started`, `success`, atau `failed`. | ETL runner |
| `started_at` | TEXT | - | No | Waktu mulai. | ETL runner |
| `finished_at` | TEXT | - | Yes | Waktu selesai. | ETL runner |
| `indicator_count` | INTEGER | CHECK >= 0 | No | Jumlah indikator diproses. | ETL runner |
| `raw_snapshot_count` | INTEGER | CHECK >= 0 | No | Jumlah snapshot API. | ETL runner |
| `fact_row_count` | INTEGER | CHECK >= 0 | No | Jumlah fact rows. | ETL runner |
| `error_message` | TEXT | - | Yes | Pesan error jika gagal. | ETL runner |
| `source_git_commit` | TEXT | - | Yes | Commit sumber run. | git metadata |
