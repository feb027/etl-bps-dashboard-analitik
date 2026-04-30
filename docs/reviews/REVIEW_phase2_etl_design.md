# Review Fase 2 - ETL Architecture & Schema

Tanggal review: 2026-04-29
Reviewer role: Dosen Rekayasa Data dan technical reviewer
Branch: `phase-2-etl-architecture-schema`
Scope: desain arsitektur ETL dan schema, bukan implementasi full extract/transform/load.

## Verdict

**APPROVED** dengan catatan perbaikan sebelum/selama Fase 3-5.

Score: **88/100**

Tidak ada critical issue yang menghalangi kelulusan Fase 2. Desain sudah cukup kuat untuk dilanjutkan karena berbasis artifact Fase 1, schema executable, dan test memvalidasi constraint utama. Beberapa aspek integritas audit dan konsistensi `indicator_key` perlu diperkuat sebelum load layer dipakai untuk dashboard final.

## Artifact Check

| Artifact | Status | Catatan |
|---|---|---|
| `docs/architecture/etl-architecture.md` | Ada | Alur ETL jelas dari extract, metadata probe, transform, load, sampai dashboard JSON. |
| `docs/architecture/database-schema.md` | Ada | Menjelaskan tabel dimensi, fact, audit, grain, FK, dan idempotensi. |
| `docs/architecture/transform-rules.md` | Ada | Menjelaskan decode `datacontent`, extraction dimensi, construction fact, dan quality gates. |
| `docs/architecture/data-dictionary.md` | Ada | Field dictionary cukup lengkap dan konsisten dengan schema utama. |
| `src/bps_etl/load/schema.sql` | Ada | DDL SQLite dapat dieksekusi dan memuat dim/fact/audit tables. |
| `src/bps_etl/load/models.py` | Ada | Helper metadata schema sederhana dan cukup untuk test Fase 2. |
| `tests/test_schema.py` | Ada | Memvalidasi tabel, FK, unique grain, sample insert, dan duplicate grain rejection. |
| `reports/progress-2-etl-design.md` | Ada | Ringkasan Fase 2 sesuai artifact. |
| `docs/project/phase-gates.md` | Ada | Fase 2 tinggal review approval. |
| `docs/project/project-control.md` | Ada | Snapshot Fase 2 tercatat. |

## Validation Evidence

Validasi yang dijalankan pada repo lokal:

| Command | Result |
|---|---|
| `python3 -m py_compile scripts/*.py` | PASS |
| `python3 -m pytest -q` | PASS, `17 passed in 0.32s` |
| `python3 -m json.tool dashboard/data/dashboard-data.json >/dev/null` | PASS; JSON valid dan masih empty state jujur |
| `python3 -m json.tool results/api/bps_api_probe_summary.json >/dev/null` | PASS; JSON valid |
| `python3 -m json.tool results/api/metadata_endpoint_evidence.json >/dev/null` | PASS; JSON valid |

Fase 1 evidence yang dirujuk masih tersedia dan valid: 4 indikator, 12 probe rows, 2490 normalized records, dan 0 unmatched `datacontent` keys.

## Assessment

Arsitektur ETL cocok untuk konteks Rekayasa Data. Dokumen `docs/architecture/etl-architecture.md` memisahkan responsibilities extract, transform, load, audit, dan dashboard generator dengan benar. Desain juga mengikuti temuan Fase 1 yang paling penting: `model=data` memakai `th_id` dari `model=th`, `datacontent` adalah dictionary composite-key, dan decoder tidak boleh memakai fixed slicing.

Schema SQLite masuk akal untuk skala proyek ini. Tersedia 5 tabel dimensi (`dim_indikator`, `dim_wilayah`, `dim_waktu`, `dim_turvar`, `dim_turtahun`), 1 fact table (`fact_statistik`), dan 2 audit tables (`raw_api_snapshot`, `etl_run_log`). Grain fact table jelas: `var_id + kode_wilayah + th_id + turvar_id + turth_id + source_domain`. Unique constraint pada grain tersebut cukup untuk idempotent load, dan `data_key` juga dibuat unique sebagai bukti key asli BPS.

Foreign key pada `fact_statistik` mendukung integritas dimensi utama. Test executable membuktikan schema bisa dibuat di SQLite memory database, FK menolak fact tanpa dimension row, sample insert berhasil, dan duplicate grain ditolak.

Transform rules sudah memadai untuk batas Fase 2. Dokumen menjelaskan composite-key decoder berbasis metadata, label cleaning, dimension extraction, fact construction, dan quality gates. Gate `decoded_count == raw_datacontent_count`, `unmatched_count == 0`, dan `duplicate_fact_key_count == 0` sudah tepat untuk mencegah silent data corruption.

Batas fase juga tepat. Tidak ada tuntutan ETL penuh di Fase 2, dan artifact yang ada sudah cukup sebagai desain siap implementasi untuk Fase 3 extract, Fase 4 transform, dan Fase 5 load.

## Critical Issues

Tidak ada critical issue.

## Important Issues

1. **`fact_statistik.indicator_key` belum dijaga konsisten dengan `dim_indikator.var_id`.**
   Pada `src/bps_etl/load/schema.sql`, `fact_statistik` memiliki `indicator_key` dan `var_id`, tetapi FK hanya ada pada `var_id`. Ini memungkinkan row fact dengan `var_id=192` tetapi `indicator_key` yang salah, sementara dashboard kemungkinan memakai `indicator_key` sebagai filter/index. Sebelum Fase 5, pilih salah satu pendekatan: hapus `indicator_key` dari fact dan derive lewat join `dim_indikator`, atau tambahkan constraint/FK yang membuat pasangan `var_id` dan `indicator_key` konsisten.

2. **Audit `run_id` belum memiliki foreign key ke `etl_run_log`.**
   `fact_statistik.run_id` dan `raw_api_snapshot.run_id` ada sebagai kolom audit, tetapi belum direlasikan ke `etl_run_log.run_id`. Untuk audit trail akademik, orphan facts/snapshots sebaiknya dicegah atau minimal didokumentasikan sebagai nullable staging behavior. Sebelum Fase 5, tambahkan FK atau jelaskan lifecycle ketika row boleh tidak memiliki run log.

## Minor Issues

1. **Test belum mengeksekusi duplicate `data_key` rejection.**
   `tests/test_schema.py` sudah mengecek unique index `data_key` ada dan duplicate grain ditolak. Untuk coverage yang lebih kuat, tambahkan test yang memasukkan `data_key` sama dengan grain berbeda dan memastikan `sqlite3.IntegrityError`.

2. **Audit counters belum punya non-negative checks.**
   Kolom seperti `raw_api_snapshot.row_count`, `etl_run_log.indicator_count`, `raw_snapshot_count`, dan `fact_row_count` bertipe integer tetapi belum diberi `CHECK (... >= 0)`. Ini bukan blocker Fase 2, tetapi akan memperkuat data quality.

3. **Asumsi `dim_waktu.tahun UNIQUE` perlu dipertahankan sebagai scope decision.**
   Untuk 4 indikator Fase 1, mapping `th_id` ke tahun konsisten. Jika nanti scope melebar ke endpoint/subject lain dan BPS memberi `th_id` berbeda untuk tahun kalender yang sama, constraint ini bisa terlalu ketat. Catat asumsi ini atau revisi menjadi desain yang menyertakan domain/scope jika Fase 3 menemukan variasi.

4. **Worktree Fase 2 belum clean saat review.**
   Branch sudah benar, tetapi artifact Fase 2 masih tercatat sebagai modified/untracked pada saat review. Ini tidak mengubah penilaian desain, tetapi sebelum phase closure perubahan perlu di-commit sesuai aturan project.

## Recommendation

Fase 2 layak disetujui. Lanjutkan ke Fase 3 dengan syarat issue penting di atas masuk backlog wajib untuk Fase 5 load layer, terutama konsistensi `indicator_key` dan FK audit `run_id`. Jangan mulai menampilkan data dashboard dari database sebelum idempotent load dan audit trail benar-benar diuji dengan data nyata.

## Post-Review Fixes Applied

Setelah review, cheap fixes langsung diterapkan pada Fase 2:

1. `fact_statistik` sekarang memiliki composite FK `(var_id, indicator_key)` ke `dim_indikator(var_id, indicator_key)` agar slug indikator konsisten dengan `var_id`.
2. `fact_statistik.run_id` dan `raw_api_snapshot.run_id` sekarang memiliki FK ke `etl_run_log.run_id` dengan `ON DELETE SET NULL`.
3. Audit counters diberi `CHECK >= 0`.
4. `tests/test_schema.py` menambahkan coverage duplicate `data_key`, inconsistent `indicator_key`, raw snapshot run-log FK, dan negative audit counters.
5. Dokumentasi schema/data dictionary/progress diperbarui agar sesuai dengan schema final Fase 2.
