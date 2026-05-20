# Review Brutal Laporan Akhir - Dosen Penguji Rekayasa Data

## Metadata Review

- Tanggal review: Mon May 11 11:14:02 UTC 2026
- Reviewer: Dosen Penguji Rekayasa Data Informatika
- PDF: `docs/001_007_029_Kelompok 17_Laporan Projek Akhir Rekayasa Data-1.pdf`
- Teks ekstraksi: `/tmp/etl_bps_final_report_text.txt`
- Metadata halaman: `/tmp/etl_bps_final_report_meta.json`
- Screenshot yang diperiksa: `/tmp/etl_bps_final_report_pages/page_01.png`, `page_05.png`, `page_08.png`
- Ground truth repo: `/home/aqua/etl-bps-dashboard-analitik`
- Artifact fact-check utama:
  - `dashboard/data/dashboard-data.json`
  - `results/api/extract/extract_manifest.json`
  - `results/tables/transform/transform_quality_metrics.json`
  - `results/database/load_metrics.json`
  - `src/bps_etl/load/schema.sql`

## Executive Verdict

Verdict: **LAYAK DENGAN REVISI**

Laporan ini tidak palsu dan sebagian besar angka inti cocok dengan artifact proyek. Ini poin penting. Angka 6 indikator, periode 2021-2024, 579 wilayah/kategori, 4.292 fact rows, 54 snapshot JSON, quality gate `passed`, 0 unmatched key, 0 duplicate fact grain, 0 null, dan struktur SQLite utama valid terhadap artifact.

Namun, sebagai laporan akhir untuk sidang, naskah ini masih punya kesalahan fatal yang akan langsung ditembak penguji: typo teknis `truth` untuk `turth`, rumus composite key salah (`turvar.var`), `run_id` load tidak cocok dengan artifact aktual, abstrak mencampur hasil ekstraksi dengan hasil transform/fact, dan tidak ada bagian **Kesimpulan** yang eksplisit sebelum Daftar Pustaka. Ini bukan sekadar typo bahasa; ini menyentuh kredibilitas pemahaman BPS API dan reproducibility.

## Skor Total

**78/100**

| Aspek | Skor | Catatan |
|---|---:|---|
| Kesesuaian dengan proyek aktual dan artifact | 18/25 | Angka utama banyak valid, tetapi `run_id` load salah dan beberapa klaim tidak diberi artifact/command. |
| Ketepatan BPS API dan ETL | 16/25 | Konsep `th_id`, metadata, quality gate sudah benar, tetapi ada salah tulis `truth` dan rumus `turvar.var` yang fatal. |
| Hasil, pembahasan, dan dashboard | 17/20 | Hasil dashboard dan metrik kuat, tetapi beberapa gambar terlalu kecil dan klaim performa/idempotensi perlu bukti eksplisit. |
| Reproducibility dan testing | 5/10 | Artifact disebut, tetapi baseline `pytest 41 passed` dan command validasi tidak masuk laporan. |
| Struktur akademik | 5/10 | Tidak ada section Kesimpulan eksplisit; ini kelemahan struktur besar. |
| Format IEEE dua kolom dan layout | 8/10 | Dua kolom sudah ada, tetapi footer placeholder IEEE, ordinal author salah, tabel pecah/terlalu padat. |
| Kajian literatur dan referensi | 9/10 | Relevan, tetapi beberapa referensi perlu dirapikan gaya IEEE dan klaim gap perlu lebih tajam. |

## Blocker/Fatal Issues

1. **Tidak ada bagian Kesimpulan eksplisit.**
   - Setelah keterbatasan pada Evaluasi Pipeline, laporan langsung masuk `DAFTAR PUSTAKA`.
   - Untuk laporan akhir, ini fatal. Penguji akan bertanya: "Apa kontribusi akhir dan apa jawaban terhadap tujuan penelitian?"
   - Minimal harus ada `V. KESIMPULAN` berisi capaian ETL, validasi, dashboard, keterbatasan, dan saran.

2. **Salah tulis endpoint BPS: `truth` seharusnya `turth`.**
   - Lokasi: Hasil Ekstraksi Data, sekitar halaman 6.
   - Teks laporan: `th, vervar, turvar, truth, unit, dan data`.
   - Ground truth BPS/project: model metadata adalah `th`, `vervar`, `turvar`, `turth`, `unit`; tidak ada model `truth`.
   - Ini fatal karena menunjukkan potensi tidak paham endpoint yang dipakai.

3. **Rumus composite key salah pada hasil transformasi.**
   - Lokasi: halaman 7.
   - Teks laporan menulis: `vervar.val + var.val + turvar.var + tahun.val + turtahun.val`.
   - Ground truth: `vervar.val + var.val + turvar.val + tahun.val + turtahun.val`.
   - `turvar.var` salah. Untuk proyek BPS API, kesalahan satu field pada decoding `datacontent` merusak argumentasi teknis.

4. **`run_id` dan timestamp load di laporan tidak cocok dengan artifact aktual.**
   - Laporan: `load-20260501T064612Z-8f5abc4f`, waktu `2026-05-01T06:46:12Z`.
   - Artifact `results/database/load_metrics.json`: `load-20260430T060939Z-6d746583`, waktu `2026-04-30T06:09:39Z`.
   - Dashboard JSON juga memakai `load-20260430T060939Z-6d746583`.
   - Ini masalah evidence-first. Jika diuji, mahasiswa harus bisa menunjuk artifact yang sama dengan naskah.

5. **Abstrak menyatakan "Proses ekstraksi menghasilkan 4.292 rekaman data", padahal extract manifest mencatat `total_raw_rows = 5744`.**
   - 4.292 adalah `raw_datacontent_count`/`fact_row_count` setelah dynamic `datacontent` didekode menjadi fact rows.
   - 5.744 adalah total raw rows extract dari seluruh snapshot metadata + dynamic data.
   - Harus dibedakan: ekstraksi menghasilkan 54 snapshot dan 5.744 raw rows; transform menghasilkan 4.292 fact rows.

## Major Issues

1. **Istilah "tingkat nasional" berpotensi menyesatkan.**
   - Laporan menyebut data "pada tingkat nasional" dan "domain nasional (0000)".
   - Artifact menunjukkan 579 wilayah/kategori dari metadata `vervar`; dashboard menampilkan provinsi dan kategori turunan.
   - Lebih tepat: "domain nasional BPS (0000) yang memuat wilayah/kategori provinsi, nasional, dan turunan sesuai metadata indikator."

2. **Tabel III.2 salah nomor menjadi `TABEL I.2`.**
   - Lokasi: halaman 5.
   - Ini kesalahan format akademik yang sangat terlihat.
   - Judul `HASIL INDIKATOR RESPONS API` juga kurang tepat; tabel itu ringkasan indikator dan jumlah record per indikator.

3. **Inkonsistensi "enam model endpoint" vs "Kelima model endpoint".**
   - Teks menyebut memakai enam model: `th`, `vervar`, `turvar`, `turth`, `data`, `unit`.
   - Kalimat berikutnya menyebut "Kelima model endpoint".
   - Harus konsisten: enam model endpoint, dengan lima metadata dan satu dynamic data.

4. **Deskripsi model `unit` pada Tabel III.1 keliru.**
   - Laporan: `unit` berfungsi "Mengambil nilai statistik aktual".
   - Seharusnya: mengambil metadata satuan/unit/deskripsi satuan indikator.
   - Artifact `extract_manifest.json` menunjukkan snapshot `unit` adalah metadata, bukan nilai statistik aktual.

5. **Parameter `unit` tidak cocok dengan manifest.**
   - Laporan menulis parameter `unit`: `var, th, domain`.
   - Artifact manifest untuk `unit` hanya menyimpan params `var` pada metadata snapshot.
   - Jangan menulis parameter yang tidak dibuktikan oleh implementasi.

6. **Klaim performa "durasi di bawah satu detik" tidak diberi bukti metrik.**
   - `load_metrics.json` punya timestamp mulai dan selesai sama pada detik yang sama, tetapi tidak ada durasi presisi.
   - Jika ingin klaim efisiensi, berikan metrik runtime dari log atau tulis lebih hati-hati: "tercatat mulai dan selesai pada timestamp detik yang sama".

7. **Klaim retry/exponential backoff "berfungsi efektif" belum dibuktikan dengan artifact run.**
   - Ada implementasi/test, tetapi laporan tidak menampilkan evidence test atau log retry.
   - Revisi: tulis sebagai fitur implementasi, bukan hasil efektivitas runtime, kecuali ada log/test yang dikutip.

8. **Reproducibility belum kuat.**
   - Ground truth menyebut pytest baseline: `41 passed`.
   - Laporan tidak mencantumkan command validasi: `python3 -m py_compile scripts/*.py`, `python3 -m pytest -q`, dan `python3 -m json.tool dashboard/data/dashboard-data.json`.
   - Untuk Rekayasa Data, hasil ETL tanpa command re-run dan test baseline belum cukup.

9. **Gambar dashboard terlalu kecil untuk dibaca.**
   - Screenshot halaman 8 menunjukkan Gambar IV.3-IV.6 kecil; teks dashboard tidak terbaca jelas.
   - Gambar boleh menjadi bukti visual, tetapi harus dapat dibaca. Saat ini lebih seperti thumbnail.

10. **Tabel IV.3 pecah dan selnya rusak secara layout.**
    - Pada screenshot halaman 8 terlihat pemenggalan seperti `BP S`, `snapsh ot`, `Perkotaan/Per desaan`.
    - Ini menurunkan profesionalitas format IEEE dua kolom.

11. **Belum ada eksplisit mapping artifact ke klaim hasil.**
    - Laporan menyebut file artifact, tetapi tidak membuat tabel "klaim -> artifact".
    - Padahal proyek ini evidence-first. Harus ada tabel ringkas yang mengikat `extract_manifest`, `transform_quality_metrics`, `load_metrics`, dan `dashboard-data.json`.

12. **Source traceability di dashboard perlu dipertegas.**
    - Laporan menyebut kolom Sumber kombinasi domain, `var_id`, `th_id`, dan `turth_id`.
    - Artifact `table_rows` juga memuat `data_key`, `region_code`, `turvar_id`, `run_id`.
    - Untuk traceability baris individual, `data_key` dan `run_id` harus disebut; kombinasi yang ditulis belum cukup menjelaskan keterlacakan satu baris.

13. **Pembahasan keterbatasan bagus, tetapi tidak ditutup dengan implikasi.**
    - Keterbatasan SQLite, batch manual, dan static JSON sudah disebut.
    - Belum ada saran teknis konkret: scheduler, PostgreSQL, incremental extract, CI artifact validation.

## Minor Issues

1. Footer halaman 1 masih placeholder: `XXX-X-XXXX-XXXX-X/XX/$XX.00 ©20XX IEEE`.
2. Ordinal author salah: `2st` dan `3st`; jika memakai bahasa Inggris, seharusnya `2nd` dan `3rd`, atau hilangkan ordinal.
3. Inkonsistensi `ditunjukan` vs `ditunjukkan`; gunakan `ditunjukkan`.
4. Penulisan istilah bercampur: `snapshot`, `records`, `fact rows`, `baris fakta`, `rekaman data`. Definisikan sekali dan konsisten.
5. `SQLite dengan star schema` perlu ditulis sebagai implementasi analitik skala kecil, bukan data warehouse penuh.
6. Referensi cukup banyak, tetapi gaya IEEE belum rapi sepenuhnya: kapitalisasi judul tidak konsisten, beberapa metadata jurnal/halaman lemah.
7. Bagian abstrak terlalu panjang dan memuat detail implementasi yang bisa dipadatkan.
8. Tabel indikator memotong `indicator_key` sehingga sulit dibaca; gunakan label pendek atau pindahkan detail ke lampiran.
9. Beberapa gambar/caption tidak konsisten kapitalisasinya: `GAMBAR` vs `Gambar`.
10. Simbol centang pada Tabel IV.4 sebaiknya diganti teks `OK`/`Passed` agar aman untuk template IEEE dan ekstraksi PDF.

## Pertanyaan Dosen Saat Ujian

1. Jelaskan kenapa `model=data` harus memakai `th_id`, bukan tahun kalender 2021-2024 langsung.
2. Dari mana angka 5.744 raw rows berasal, dan mengapa berbeda dari 4.292 fact rows?
3. Tunjukkan artifact yang membuktikan 54 snapshot terdiri dari 30 metadata dan 24 dynamic data.
4. Apa formula `datacontent` key BPS yang benar? Mengapa tidak boleh slicing string posisi tetap?
5. Apa perbedaan `turvar` dan `turth`?
6. Mengapa `dim_wilayah` berisi 579 baris padahal provinsi Indonesia tidak sebanyak itu?
7. Apa grain dari `fact_statistik`, dan bagaimana uniqueness/idempotency dijamin?
8. Mengapa SQLite dipilih, dan kapan pilihan ini tidak layak?
9. Bagaimana membuktikan dashboard tidak memakai dummy data?
10. Bagaimana cara menjalankan ulang pipeline dari awal sampai dashboard JSON?
11. Apa yang terjadi jika BPS mengubah struktur respons API?
12. Apa bukti bahwa tests lulus? Mana output `pytest 41 passed`?
13. Kenapa laporan menulis `truth`? Apakah endpoint itu benar-benar ada?
14. Kenapa `run_id` di laporan berbeda dengan `load_metrics.json`?

## Bagian Yang Sudah Kuat

1. **Angka inti hasil ETL valid terhadap artifact.**
   - 6 indikator: valid.
   - 2021-2024: valid.
   - 579 wilayah/kategori: valid.
   - 4.292 fact rows: valid.
   - 54 snapshot JSON: valid.
   - 30 metadata + 24 dynamic data: valid.
   - `total_raw_rows = 5744`: valid pada `extract_manifest.json`.

2. **Quality gate dilaporkan sesuai artifact.**
   - `raw_datacontent_count = 4292`
   - `decoded_count = 4292`
   - `fact_row_count = 4292`
   - `unmatched_count = 0`
   - `duplicate_fact_key_count = 0`
   - `null_value_count = 0`
   - `quality_gate = passed`

3. **Schema analitik sesuai implementasi.**
   - `dim_indikator`, `dim_wilayah`, `dim_waktu`, `dim_turvar`, `dim_turtahun`, `fact_statistik`, `raw_api_snapshot`, `etl_run_log` sesuai `schema.sql` dan `load_metrics.json`.

4. **Dashboard tidak terlihat dummy.**
   - `dashboard-data.json` memuat `quality.no_dummy_data = true`, summary 6/579/4/4292, dan `table_rows` dari SQLite.

5. **Pembahasan keterbatasan cukup jujur.**
   - Batch manual, SQLite file-based, static JSON, dan dependensi API BPS sudah disebut. Ini bagus dan harus dipertahankan.

## Risiko Nilai Jika Tidak Direvisi

- Jika typo `truth` dan `turvar.var` dibiarkan: nilai teknis ETL bisa jatuh karena dianggap tidak memahami API BPS.
- Jika `run_id` salah dibiarkan: nilai evidence/reproducibility turun tajam karena artifact dan laporan tidak konsisten.
- Jika tidak ada Kesimpulan: laporan terlihat belum selesai.
- Jika abstrak tetap menyebut extract menghasilkan 4.292 record: penguji akan mempertanyakan perbedaan dengan 5.744 raw rows di Tabel IV.4.
- Jika gambar/tabel tetap kecil dan rusak: nilai format IEEE turun meskipun proyeknya benar.

Estimasi nilai jika tidak direvisi: **70-75**. Dengan revisi P0 dan P1 yang benar, laporan realistis naik ke **86-90**.

## Kesimpulan Kelayakan

Secara substansi proyek, laporan ini **layak dipertahankan** karena berbasis artifact nyata dan hasil ETL-nya dapat diverifikasi. Secara naskah final, laporan ini **belum siap submit final tanpa revisi**. Revisi wajib difokuskan pada kebenaran istilah BPS API, konsistensi angka artifact, penambahan Kesimpulan, dan bukti reproducibility.

Verdict akhir: **LAYAK DENGAN REVISI**.
