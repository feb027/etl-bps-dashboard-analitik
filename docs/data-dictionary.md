# Data Dictionary

Status: draft. Final fields will be updated after Fase 1 API research and Fase 2 schema design.

## Fase 1 API Finding

Dynamic data from `model=data` returns numeric values in `datacontent`. The key is a composite string generated from BPS metadata values:

```text
vervar.val + var.val + turvar.val + tahun.val + turtahun.val
```

Example for `var_id=192`: `110019243412363` decodes as wilayah `1100`, variable `192`, turvar `434`, tahun `123`, and turtahun `63`. Because each component can have different string length, the transform layer must decode by metadata lookup, not fixed-position slicing. The decoder fails fast on generated composite-key collisions so ambiguous BPS responses are not silently loaded.

## Target Tables

### dim_indikator

| Field | Description | Source |
|---|---|---|
| `var_id` | ID variabel BPS | `model=var` |
| `nama_indikator` | Nama indikator | `model=var` |
| `satuan` | Unit/satuan | `model=var` / `model=unit` |
| `subjek` | Subjek statistik | `model=var` |
| `definisi` | Definisi indikator | `model=var` |

### dim_wilayah

| Field | Description | Source |
|---|---|---|
| `kode_wilayah` | Kode wilayah/kategori vertikal | `model=vervar` / domain metadata |
| `nama_wilayah` | Nama wilayah | `model=vervar` |
| `level` | nasional/provinsi/kategori lain | transform rule |

### dim_waktu

| Field | Description | Source |
|---|---|---|
| `th_id` | ID tahun BPS | `model=th` |
| `tahun` | Tahun kalender | `model=th` |

### fact_statistik

| Field | Description | Source |
|---|---|---|
| `var_id` | FK indikator | decoded dynamic data |
| `kode_wilayah` | FK wilayah/kategori | decoded dynamic data |
| `th_id` | FK waktu | decoded dynamic data |
| `tahun` | Tahun | decoded dynamic data |
| `nilai` | Nilai statistik | `datacontent` |
| `satuan` | Satuan | metadata |
