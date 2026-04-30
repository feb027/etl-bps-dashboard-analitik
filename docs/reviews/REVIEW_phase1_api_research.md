# Review Fase 1 — BPS API Research & Proof

Reviewer: Dosen Rekayasa Data / Technical Reviewer
Tanggal review: 2026-04-29
Branch: `phase-1-bps-api-research`
Scope: API Research & Proof, bukan ETL/database/dashboard final.

## Verdict

**APPROVED** dengan skor **90/100**.

Fase 1 sudah membuktikan penggunaan Web API BPS untuk dynamic data secara memadai. Artifact menunjukkan data nyata dari BPS, mapping `model=th` ke `th_id`, penggunaan `model=data`, dan decoding `datacontent` berbasis metadata lookup tanpa fixed slicing. Tidak ada critical issue.

## Validasi yang Dijalankan

| Check | Result |
|---|---|
| `python3 -m py_compile scripts/*.py` | PASS |
| `python3 -m pytest -q` | PASS, `9 passed in 0.34s` |
| `python3 -m json.tool dashboard/data/dashboard-data.json >/dev/null` | PASS |
| `python3 -m json.tool results/api/bps_api_probe_summary.json >/dev/null` | PASS |

Catatan status repo: review dilakukan pada worktree lokal yang berisi perubahan Fase 1 belum ter-commit. Ini konsisten dengan review gate sebelum commit, tetapi commit final tetap perlu dilakukan setelah review/fix.

## Evidence Reviewed

Artifact utama yang tersedia dan direview:

| Artifact | Status | Catatan |
|---|---|---|
| `scripts/verify_bps_api.py` | Ada | Probe memakai API key dari `.env`, mengambil `model=th`, lalu `model=data`. |
| `src/bps_etl/extract/client.py` | Ada | Client minimal stdlib, query param menyertakan `model`, `domain`, `lang`, `key`. |
| `src/bps_etl/extract/dynamic_data.py` | Ada | Decoder membangun key index dari metadata response. |
| `tests/test_dynamic_data.py` | Ada | Unit test membuktikan composite key sintetis. |
| `results/api/bps_api_probe_summary.json` | Ada dan valid JSON | Ringkasan success, 4 indikator, 12 probe rows, 2490 normalized records, 0 unmatched. |
| `results/api/selected_indicators.json` | Ada | 4 indikator valid dengan `period_ids` tahun 2021-2023. |
| `results/tables/bps_api_probe_results.csv` | Ada | 12 baris indikator/tahun, semua `data_availability=available`, decoded sama dengan record count. |
| `results/tables/normalized_sample.csv` | Ada | 2490 baris data decoded nyata. |
| `reports/progress-1-api-research.md` | Ada | Mendokumentasikan temuan API dan artifact evidence. |
| `docs/project/phase-gates.md` | Ada | Fase 1 sebagian besar marked done, review masih pending sebelum file ini. |
| `docs/project/project-control.md` | Ada | Snapshot Fase 1 mencatat 4 indikator, 2490 records, 0 unmatched. |

## Assessment by Scope

### 1. Proof Web API BPS

**PASS.** `scripts/verify_bps_api.py` menggunakan `BPSClient` untuk memanggil endpoint list BPS, memilih indikator, mengambil periode dari `model=th`, lalu mengambil dynamic data dengan `model=data`. Artifact raw kecil per indikator/tahun tersedia di `results/api/dynamic_*_*.json`.

Bukti utama:

| Metric | Value |
|---|---:|
| Indicator count | 4 |
| Probe rows | 12 |
| Normalized records | 2490 |
| Unmatched keys | 0 |

CSV probe menunjukkan semua 12 kombinasi indikator/tahun berstatus `available`.

### 2. `model=th` dan `th_id`

**PASS.** `scripts/verify_bps_api.py` mengambil period map lewat `client.list_rows("th", params={"var": var_id})`, lalu memanggil dynamic data dengan `params={"var": var_id, "th": th_id}`.

Artifact membuktikan mapping tahun target:

| Tahun | `th_id` |
|---|---:|
| 2021 | 121 |
| 2022 | 122 |
| 2023 | 123 |

Mapping ini tersimpan di `results/api/selected_indicators.json`, `results/api/metadata_probe_samples.json`, `results/tables/bps_api_probe_results.csv`, dan file `dynamic_*_*.json`.

### 3. Decoder `datacontent`

**PASS.** Decoder di `src/bps_etl/extract/dynamic_data.py` membangun lookup dari kombinasi metadata:

`vervar.val + var.val + turvar.val + tahun.val + turtahun.val`

Implementasi tidak memakai fixed slicing. Ia menghasilkan semua kombinasi metadata response dan melakukan exact key lookup terhadap `datacontent`. Artifact metadata juga menyimpan rule ini di `results/api/metadata_*.json`.

Hasil decode artifact:

| Indicator | 2021 | 2022 | 2023 | Unmatched |
|---|---:|---:|---:|---:|
| `poverty_rate` | 208 | 208 | 104 | 0 |
| `open_unemployment_rate` | 70 | 70 | 70 | 0 |
| `mean_years_schooling_new_method` | 549 | 549 | 549 | 0 |
| `human_development_index_new_method` | 35 | 39 | 39 | 0 |

### 4. Minimal 3 Indikator Valid

**PASS.** Fase 1 memenuhi lebih dari minimum: 4 indikator valid untuk tahun 2021, 2022, dan 2023.

Indikator yang terbukti:

| Indicator | `var_id` | Tema | Records |
|---|---:|---|---:|
| `poverty_rate` | 192 | Kemiskinan | 520 |
| `open_unemployment_rate` | 543 | Ketenagakerjaan | 210 |
| `mean_years_schooling_new_method` | 415 | Pendidikan | 1647 |
| `human_development_index_new_method` | 494 | Pembangunan Manusia | 113 |

### 5. Security

**PASS.** Tidak ditemukan API key/token nyata pada source, artifact, atau output review yang discan. `.gitignore` mengabaikan `.env` dan `.env.*` kecuali `.env.example`. `.env.example` hanya berisi placeholder kosong.

Scan menemukan hanya referensi aman:

| Path | Catatan |
|---|---|
| `scripts/verify_bps_api.py` | Membaca API key dari environment/local `.env`. |
| `src/bps_etl/config.py` | Membaca `BPS_API_KEY` dari environment. |
| `tests/test_helpers.py` | Memakai placeholder `test-api-key-placeholder`. |

### 6. Code Quality, Tests, Reproducibility

**PASS dengan catatan minor/important.** Kode cukup sederhana dan auditable untuk Fase 1. Test suite lulus. Artifact cukup untuk mereproduksi klaim utama tanpa menampilkan dummy data. Re-run probe tetap membutuhkan `BPS_API_KEY` lokal sesuai aturan project.

## Critical Issues

Tidak ada.

## Important Issues

1. **Klaim verifikasi beberapa metadata model masih sebagian indirect.**
   `docs/project/phase-gates.md` menandai `model=var`, `model=vervar`, `turvar`, dan `turth` checked. Artifact saat ini paling kuat membuktikan `model=th` dan `model=data`; metadata `var/vervar/turvar/turtahun` memang muncul di payload dynamic data, tetapi tidak ada artifact raw eksplisit dari endpoint list masing-masing model. Ini tidak memblokir Fase 1 karena scope utama dynamic data sudah terbukti, tetapi untuk ketelitian akademik sebaiknya tambahkan catatan bahwa verifikasi metadata tersebut berasal dari payload `model=data`, atau tambahkan probe endpoint list metadata secara eksplisit.

2. **Test decoder belum memakai artifact BPS nyata sebagai regression fixture.**
   `tests/test_dynamic_data.py` membuktikan composite key dengan payload sintetis. Artifact nyata menunjukkan 0 unmatched, tetapi belum ada test yang membaca minimal satu `results/api/dynamic_*_*.json` dan memastikan decode tetap 0 unmatched. Ini penting untuk menjaga rule decoder tetap aman ketika Fase 2/4 mulai refactor transform layer.

## Minor Issues

1. **Progress report belum mencantumkan validasi summary JSON.**
   `reports/progress-1-api-research.md` mencantumkan `py_compile`, `pytest`, dan validasi dashboard JSON, tetapi belum mencantumkan `python3 -m json.tool results/api/bps_api_probe_summary.json >/dev/null`. Validasi ini sudah lulus saat review.

2. **Decoder belum mendeteksi collision composite key secara eksplisit.**
   Untuk artifact saat ini tidak ada collision dan semua `datacontent` decoded. Namun karena key BPS berupa concat tanpa delimiter, fungsi `build_datacontent_key_index` sebaiknya fail fast atau melaporkan duplicate generated key bila terjadi pada indikator lain.

3. **Branch/worktree belum menjadi artifact commit final.**
   Review ini dilakukan sebelum commit Fase 1. Setelah issue diputuskan/fix, perubahan Fase 1 perlu di-commit dengan conventional commit agar completion criteria terpenuhi.

## Final Decision

Fase 1 **APPROVED**.

Alasan approval: artifact membuktikan dynamic data BPS nyata, `model=th` ke `th_id` terdokumentasi dan tersimpan, decoder metadata lookup berjalan tanpa unmatched key, minimal 3 indikator valid terpenuhi, security scan tidak menemukan secret, dan validasi teknis lulus.
