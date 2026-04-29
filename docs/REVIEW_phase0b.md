# Review Fase 0A/0B

Tanggal review: 2026-04-29  
Peran review: dosen Rekayasa Data dan reviewer teknis  
Scope: scaffold lokal Fase 0A/0B, bukan evaluasi hasil eksperimen ETL.

## Verdict

Skor: **88/100**  
Verdict: **APPROVED** untuk scaffold lokal Fase 0A/0B, dengan catatan revisi penting sebelum menutup Fase 0B penuh dan masuk ke Fase 1.

Alasan verdict: tidak ada critical issue, validasi lokal lulus, struktur proyek sudah sesuai target Rekayasa Data, dan dashboard tidak menampilkan data palsu. Skor belum mencapai target kuat 90 karena ada gate eksternal Fase 0B yang belum selesai/terverifikasi dan ada satu pola test yang kurang ideal terhadap aturan "no secrets".

## Validasi yang Dijalankan

| Perintah | Hasil |
|---|---|
| `python3 -m py_compile scripts/*.py` | PASS |
| `python3 -m pytest -q` | PASS, 6 passed in 0.17s |
| `python3 -m json.tool dashboard/data/dashboard-data.json >/dev/null` | PASS |

Pemeriksaan tambahan:

- `git ls-files` tidak menunjukkan `.env`, database SQLite, raw data, cache Python, atau file besar data yang ter-track.
- Pencarian pola `BPS_API_KEY`, `api_key`, `key=`, `secret`, `token`, `dummy`, dan `fake` tidak menemukan API key nyata. Temuan hanya aturan/dokumentasi, placeholder `.env.example`, dan nilai test dummy pada `tests/test_helpers.py`.

## Critical Issues

Tidak ada critical issue.

## Important Issues

1. **Gate eksternal Fase 0B belum selesai/terverifikasi.**  
   `docs/phase-gates.md:23` masih menandai GitHub repo created/pushed sebagai belum selesai, dan `docs/phase-gates.md:33` masih menandai GitHub Pages HTTP 200 sebagai belum selesai. `docs/project-control.md:44-47` juga masih menempatkan commit/push, enable Pages, dan review gate sebagai next action. Ini bukan kegagalan scaffold lokal, tetapi Fase 0B belum boleh disebut selesai penuh sampai gate eksternal tersebut diverifikasi.  
   Actionable: setelah commit/push dan Pages aktif, update `docs/project-control.md` dan `docs/phase-gates.md` dengan status review dan bukti URL/HTTP 200.

2. **Test memakai literal `secret` sebagai nilai API key dummy.**  
   `tests/test_helpers.py:8` dan `tests/test_helpers.py:12` memakai string `"secret"` untuk menguji query param `key`. Ini bukan API key nyata, tetapi kurang selaras dengan aturan eksplisit `AGENTS.md:14` bahwa token/API key tidak di-hardcode di source/docs/tests.  
   Actionable: ganti dengan nama placeholder yang jelas tidak rahasia, misalnya konstanta `TEST_API_KEY_PLACEHOLDER = "test-placeholder-not-a-secret"`, atau gunakan fixture yang menegaskan nilai tersebut dummy.

## Minor Issues

1. **Type hint masih cukup longgar di beberapa fungsi scaffold.**  
   Contoh: `scripts/generate_dashboard_data.py:15` memakai return type `dict`, dan `src/bps_etl/extract/client.py:16` memakai `dict[str, Any]`. Untuk Fase 0B masih dapat diterima, tetapi Fase 1-3 sebaiknya mulai memakai tipe yang lebih spesifik atau typed structure agar kontrak data BPS lebih jelas.

2. **Referensi dan laporan masih placeholder.**  
   `references/source-log.md`, `references/literature-matrix.md`, `references/references.bib`, dan file `reports/` masih menandai status belum dikerjakan/planned. Ini sesuai fase awal dan bukan kegagalan, tetapi Fase 1 harus mengisi source log dengan bukti akses dokumentasi/API BPS yang benar.

3. **`docs/phase-gates.md:34` masih menyatakan review file belum ada.**  
   File review ini membuat artifact review tersedia, tetapi dokumen gate belum di-update karena instruksi review hanya mengizinkan penulisan ke `docs/REVIEW_phase0b.md`.  
   Actionable: update checklist pada langkah fix/docs berikutnya.

## Pemeriksaan Per Area

### 1. Kesesuaian Scaffold dengan Proyek Rekayasa Data

Scaffold sudah sesuai untuk proyek Rekayasa Data fase awal. README menjelaskan alur Web API BPS -> extract -> raw JSON evidence -> transform -> database SQLite -> generator dashboard -> dashboard statis (`README.md:14-32`). Struktur phase-gated juga jelas pada `docs/workflow.md:3-7` dan `docs/phase-gates.md:3-10`.

Penilaian: **baik**. Belum ada hasil eksperimen, dan itu wajar untuk Fase 0A/0B.

### 2. AGENTS.md, README, Project Control, Phase Gates, Workflow

- `AGENTS.md` sudah memuat prinsip evidence-first, no fake dashboard, no secrets, no raw large data, BPS API correctness, phase-gated workflow, dan academic honesty (`AGENTS.md:10-18`).
- README sudah menjelaskan status Fase 0B, struktur repo, setup lokal, validasi, dashboard lokal, aturan data, dan roadmap (`README.md:7-94`).
- `docs/project-control.md` sudah menyimpan keputusan arsitektur, blocker, artifact inventory, dan next action (`docs/project-control.md:10-47`).
- `docs/phase-gates.md` sudah punya done criteria per fase, termasuk BPS API research yang menekankan verifikasi `var`, `th`, `vervar`, `turvar`, `turth`, dan `datacontent` (`docs/phase-gates.md:36-47`).
- `docs/workflow.md` sudah menetapkan pola plan -> execute -> artifact -> docs -> review -> fix -> commit -> next phase (`docs/workflow.md:3-7`).

Penilaian: **baik**, dengan catatan gate eksternal dan status review perlu di-update setelah proses ini.

### 3. Struktur Source, Scripts, Tests, Dashboard, References, Reports

- `src/bps_etl` sudah terbagi menjadi `extract`, `transform`, `load`, dan `pipeline`, cukup tepat untuk modularisasi ETL.
- `scripts/` punya entry point untuk API verification, ETL runner, dan dashboard data generator.
- `tests/` berisi smoke test scaffold dan helper test dasar; cakupan sudah cukup untuk Fase 0B.
- `dashboard/` berisi static dashboard shell dengan `dashboard/data/dashboard-data.json` sebagai sumber data.
- `references/` dan `reports/` ada sebagai placeholder jujur untuk fase akademik berikutnya.

Penilaian: **baik** untuk scaffold. Jangan memperluas ETL besar sebelum Fase 1 membuktikan perilaku API BPS.

### 4. Keamanan dan Git Hygiene

`.gitignore` memblokir `.env`, `.env.*`, raw/processed/database data, SQLite, cache, virtualenv, log, dan editor files (`.gitignore:1-32`). `.env.example` hanya berisi nama variabel dan base URL, bukan secret. `src/bps_etl/config.py:17-25` mengambil API key dari environment dan error jika kosong.

Penilaian: **baik**. Satu catatan minor/penting: literal `"secret"` di test sebaiknya diganti agar tidak menimbulkan false positive saat audit no-secrets.

### 5. Dashboard dan Anti-Fake-Data

Dashboard tidak menampilkan grafik/table dummy. `dashboard/data/dashboard-data.json:7-17` berisi count nol dan array chart kosong. `dashboard/data/dashboard-data.json:22-24` menyatakan empty state sampai artifact ETL nyata tersedia. UI juga menyatakan "Data statistik belum tersedia" pada `dashboard/index.html:29-32`.

Penilaian: **baik**. Empty state jujur dan tidak ada klaim hasil analitik palsu.

### 6. BPS API Correctness

Scaffold belum melakukan network request BPS, dan itu tepat untuk Fase 0B. `scripts/verify_bps_api.py:14` sudah mencantumkan model yang perlu diverifikasi pada Fase 1, termasuk `var`, `th`, `vervar`, `turvar`, `turth`, `unit`, dan `data`. `results/api/bps_api_probe_summary.json:2-12` berstatus planned, bukan klaim hasil.

Penilaian: **baik**. Jangan mengisi data indikator atau grafik sebelum `datacontent` dan dimensi BPS terbukti dari artifact nyata.

## Rekomendasi Revisi Murah

1. Ganti literal `"secret"` di `tests/test_helpers.py` menjadi placeholder eksplisit non-secret.
2. Setelah review ini, update `docs/project-control.md` bagian Review Status dan `docs/phase-gates.md` checklist Fase 0B review file.
3. Setelah push dan GitHub Pages aktif, tambahkan bukti URL/HTTP 200 di `docs/project-control.md` atau artifact kecil di `results/metrics/`.

## Kesimpulan

Scaffold Fase 0A/0B layak dilanjutkan. Repo sudah menempatkan prinsip evidence-first dan no-fake-dashboard sebagai aturan inti, validasi lokal lulus, dan artifact awal tidak mengarang hasil eksperimen. Fase berikutnya harus fokus pada pembuktian API BPS secara kecil dan terdokumentasi sebelum membangun ETL yang lebih besar.
