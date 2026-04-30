# Progress 1 — BPS API Research & Proof

## Status

Fase 1 membuktikan perilaku dasar Web API BPS untuk dynamic data sebelum ETL penuh dibangun.

## Ringkasan Hasil

- Status probe: **success**
- Jumlah indikator valid: **6**
- Tahun target: **2024, 2023, 2022, 2021**
- Baris probe: **24**
- Record normalized sample: **4292**
- Unmatched datacontent keys: **0**

## Temuan Penting API BPS

1. `model=data` menggunakan `th_id` dari `model=th`, bukan string tahun langsung seperti `2021:2023`.
2. Field `datacontent` memakai composite key: `vervar.val + var.val + turvar.val + tahun.val + turtahun.val`.
3. Decode tidak boleh dilakukan dengan slicing tetap karena panjang tiap dimensi bisa berbeda.
4. Decode yang aman dilakukan dengan membangun lookup dari semua kombinasi metadata response.

## Indikator Terpilih

| Key | var_id | Tema | Label | Tahun | Record Decoded |
|---|---:|---|---|---|---:|
| `poverty_rate` | 192 | Kemiskinan | Persentase Penduduk Miskin (P0) Menurut Provinsi dan Daerah | 2024, 2023, 2022, 2021 | 752 |
| `open_unemployment_rate` | 543 | Ketenagakerjaan | Tingkat Pengangguran Terbuka Menurut Provinsi | 2024, 2023, 2022, 2021 | 288 |
| `mean_years_schooling_new_method` | 415 | Pendidikan | [Metode Baru] Rata-rata Lama Sekolah | 2024, 2023, 2022, 2021 | 2200 |
| `human_development_index_new_method` | 494 | Pembangunan Manusia | [Metode Baru] Indeks Pembangunan Manusia (IPM) menurut Provinsi | 2024, 2023, 2022, 2021 | 152 |
| `gini_ratio` | 98 | Ketimpangan | Gini Ratio Menurut Provinsi dan Daerah | 2024, 2023, 2022, 2021 | 752 |
| `regional_gdp_growth_constant_2010` | 291 | Ekonomi Regional | [Seri 2010] Laju Pertumbuhan Produk Domestik Regional Bruto Atas Dasar Harga Konstan 2010  Menurut Provinsi | 2024, 2023, 2022, 2021 | 148 |

## Artifact Evidence

| Artifact | Isi |
|---|---|
| `results/api/bps_api_probe_summary.json` | Ringkasan hasil probe |
| `results/api/selected_indicators.json` | Daftar indikator valid |
| `results/api/sample_dynamic_response.json` | Contoh response dynamic data BPS |
| `results/api/metadata_endpoint_evidence.json` | Bukti eksplisit endpoint metadata `var`, `th`, `vervar`, `turvar`, `turth`, `unit` |
| `results/api/dynamic_*_*.json` | Evidence response per indikator/tahun |
| `results/api/metadata_*.json` | Metadata dimensi per indikator |
| `results/tables/bps_api_probe_results.csv` | Tabel hasil probe |
| `results/tables/normalized_sample.csv` | Sample hasil decode tabular |

## Implikasi untuk Fase 2

- Schema harus menyimpan `th_id` dan label tahun.
- Transform layer harus punya decoder composite key berbasis metadata lookup.
- `turvar` dan `turtahun` perlu disimpan sebagai kategori karena beberapa indikator punya dimensi tambahan seperti Perkotaan/Perdesaan atau Februari/Agustus/Tahunan.
- Dashboard harus mengambil data dari tabel hasil decode, bukan langsung dari raw `datacontent`.

## Validasi

Validasi dijalankan setelah implementasi:

```bash
python3 -m py_compile scripts/*.py
python3 -m pytest -q
python3 -m json.tool dashboard/data/dashboard-data.json >/dev/null
python3 -m json.tool results/api/bps_api_probe_summary.json >/dev/null
```
