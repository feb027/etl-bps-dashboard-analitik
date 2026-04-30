# Transform Rules — Fase 2

Status: **implemented in Fase 4**, see `docs/transform-layer.md` and `results/tables/transform/transform_manifest.json`.

## Input Utama

Transform layer menerima payload BPS dari `model=data` dengan struktur utama:

```text
var, vervar, turvar, tahun, turtahun, datacontent
```

Fase 1 membuktikan bahwa `datacontent` adalah dictionary numeric dengan key gabungan, bukan list record siap pakai.

## Rule 1 — Composite Key Decoder

Key `datacontent` dibangun dari metadata response:

```text
vervar.val + var.val + turvar.val + tahun.val + turtahun.val
```

Transform tidak boleh memakai slicing posisi tetap karena panjang kode wilayah, `var_id`, `turvar_id`, `th_id`, dan `turth_id` dapat berbeda.

Langkah aman:

1. ambil semua nilai metadata dari `vervar`, `var`, `turvar`, `tahun`, `turtahun`,
2. generate semua kombinasi composite key,
3. buat lookup `key -> dimensi`,
4. cocokkan setiap key `datacontent` ke lookup,
5. catat unmatched keys,
6. fail-fast jika generated key collision.

## Rule 2 — Label Cleaning

Label BPS kadang memuat HTML ringan, misalnya `<b>ACEH</b>`. Transform harus:

- menghapus tag HTML,
- mengganti `&nbsp;` dan `\xa0` menjadi spasi,
- menormalkan whitespace berlebih.

## Rule 3 — Dimension Extraction

### `dim_indikator`

Sumber: `payload.var[0]` dan selected-indicator config.

Mapping:

| Target | Source |
|---|---|
| `var_id` | `var.val` |
| `indicator_key` | config project |
| `nama_indikator` | `var.label` |
| `unit` | `var.unit` |
| `subject` | `var.subj` |
| `definisi` | `var.def` |
| `catatan` | `var.note` |
| `decimal_places` | `var.decimal` |

### `dim_wilayah`

Sumber: `payload.vervar`.

Mapping:

| Target | Source |
|---|---|
| `kode_wilayah` | `vervar.val` |
| `nama_wilayah` | `vervar.label` |
| `level_wilayah` | transform inference (`provinsi`, `nasional`, `kabupaten_kota`, `unknown`) |
| `group_ver_id` | explicit metadata endpoint if available |
| `group_ver_name` | explicit metadata endpoint if available |

### `dim_waktu`

Sumber: `payload.tahun` dan `model=th` evidence.

Mapping:

| Target | Source |
|---|---|
| `th_id` | `tahun.val` / `model=th.th_id` |
| `tahun` | `tahun.label` / `model=th.th` |
| `periode_label` | `tahun.label` |

### `dim_turvar` dan `dim_turtahun`

Jika BPS mengembalikan kosong, gunakan default:

```text
turvar_id='0', turvar_label='Tidak ada'
turth_id='0', turth_label='Tahun'
```

## Rule 4 — Fact Row Construction

Satu row `fact_statistik` dihasilkan dari satu pasangan `data_key -> nilai`.

Mapping:

| Target | Source |
|---|---|
| `indicator_key` | config project |
| `var_id` | decoded key metadata |
| `kode_wilayah` | decoded key metadata |
| `th_id` | decoded key metadata |
| `turvar_id` | decoded key metadata |
| `turth_id` | decoded key metadata |
| `data_key` | original `datacontent` key |
| `source_domain` | BPS domain, default `0000` |
| `nilai` | `datacontent[data_key]` |
| `last_update` | payload `last_update` |

## Rule 5 — Data Quality Checks

Transform output harus menghitung minimal:

| Metric | Meaning |
|---|---|
| `raw_datacontent_count` | jumlah key dari BPS |
| `decoded_count` | jumlah record berhasil decode |
| `unmatched_count` | jumlah key tanpa metadata |
| `duplicate_fact_key_count` | duplicate unique grain |
| `null_value_count` | nilai null/tidak numerik |

Gate untuk lanjut load:

```text
raw_datacontent_count > 0
decoded_count == raw_datacontent_count
unmatched_count == 0
duplicate_fact_key_count == 0
```

## Rule 6 — No Silent Success

Pipeline tidak boleh melaporkan sukses jika:

- API response `list-not-available`,
- `datacontent` kosong untuk indikator wajib,
- semua normalized records kosong,
- foreign key dimension rows belum siap,
- unique constraint fact gagal karena duplicate tidak ditangani.

## Output Transform

Transform menghasilkan dua output:

1. `DimensionBundle` — rows untuk `dim_indikator`, `dim_wilayah`, `dim_waktu`, `dim_turvar`, `dim_turtahun`.
2. `FactRows` — rows untuk `fact_statistik`.

Implementasi detail class/function dilakukan pada Fase 4.
