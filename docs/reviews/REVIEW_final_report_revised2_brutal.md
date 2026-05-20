# Review Brutal PDF Revisi 2 - Dosen Penguji Rekayasa Data

## Metadata Review

- Tanggal review: Mon May 11 15:31:49 UTC 2026
- Reviewer: Dosen Penguji Rekayasa Data Informatika
- PDF direview: `docs/001_007_029_Kelompok 17_Laporan Projek Akhir Rekayasa Data (2).pdf`
- Teks ekstraksi: `/tmp/etl_bps_revised2_text.txt`
- Metadata halaman: `/tmp/etl_bps_revised2_meta.json`
- Screenshot halaman: `/tmp/etl_bps_revised2_pages/page_01.png` s.d. `page_12.png`
- Ground truth repo: `/home/aqua/etl-bps-dashboard-analitik`
- Artifact fact-check:
  - `dashboard/data/dashboard-data.json`
  - `results/api/extract/extract_manifest.json`
  - `results/tables/transform/transform_quality_metrics.json`
  - `results/database/load_metrics.json`
  - `src/bps_etl/load/schema.sql`

## Executive Verdict

Verdict: **LAYAK DENGAN REVISI**

Revisi ini jauh lebih kuat daripada versi sebelumnya. Blocker teknis utama sudah ditutup: istilah BPS API sudah benar memakai `turth`, formula decoding `datacontent` sudah memakai `turvar.val`, angka extract dan transform sudah dipisahkan dengan lebih benar, bagian `V. KESIMPULAN` sudah ada, nama tabel `fact_statistik` konsisten, upsert sudah ditulis `ON CONFLICT`, dan `run_id` load yang terlihat di halaman 7 sudah sesuai artifact `load_metrics.json`.

Namun, ini belum layak disebut submit-ready final. Masih ada cacat format dan alur naskah yang terlalu terlihat untuk laporan akhir: footer placeholder IEEE masih menempel di halaman 1, author line masih memakai ordinal salah `2st` dan `3st`, Tabel II.1 masih buruk secara layout, Tabel IV.3 dan IV.5 masih banyak word break jelek, dan yang paling mengganggu: halaman 6 meninggalkan kalimat menggantung "Command yang digunakan meliputi:" lalu langsung lompat ke BAB IV. Itu membuat metodologi validasi terlihat terpotong.

Secara substansi Rekayasa Data: **sudah layak dipertahankan**. Secara dokumen final: **masih perlu revisi kecil-menengah sebelum dikumpulkan**.

## Score and Breakdown

**Skor total: 87/100**

| Aspek | Skor | Catatan brutal |
|---|---:|---|
| Kesesuaian dengan artifact proyek | 23/25 | Angka inti cocok dengan ground truth: 6 indikator, 2021-2024, 579 wilayah/kategori, 4.292 fact rows, 54 snapshot, 5.744 raw rows, quality gate passed. |
| Ketepatan BPS API dan ETL | 23/25 | Perbaikan `turth`, `turvar.val`, `th_id`, dan `datacontent` sudah benar. Masih perlu lebih rapi pada penjelasan evidence command. |
| Hasil, pembahasan, dan dashboard | 18/20 | Dashboard dan metrik sudah berbasis artifact. Visual tabel/gambar masih mengurangi profesionalitas. |
| Reproducibility dan testing | 8/10 | Tabel IV.5 sudah mencantumkan artifact dan `41 passed`; command validasi ada. Masalahnya satu kalimat metodologi menggantung dan command wrap buruk. |
| Struktur akademik | 8/10 | Kesimpulan sudah ada dan substansial. Alur dari validasi metodologi ke hasil masih pecah di halaman 6. |
| Format IEEE, layout, dan kerapian | 4/10 | Ini titik terlemah: placeholder, ordinal author salah, tabel pecah, path artifact terpotong, dan beberapa word break buruk. |
| Kajian literatur dan referensi | 3/5 | Cukup untuk laporan proyek, tetapi Tabel II.1 masih tidak nyaman dibaca. |

## Fixed Issues from Previous Review

1. **Typo fatal `truth` sudah hilang.**
   - Hasil cek teks: `truth` 0 kemunculan, `turth` 10 kemunculan.
   - Ini memperbaiki kredibilitas teknis BPS API.

2. **Formula composite key sudah diperbaiki.**
   - Teks sekarang menulis `vervar.val + var.val + turvar.val + tahun.val + turtahun.val`.
   - Hasil cek teks: `turvar.var` 0 kemunculan, `turvar.val` ada.
   - Ini sesuai semantik decoding `datacontent` BPS.

3. **Bagian `V. KESIMPULAN` sudah ditambahkan.**
   - Lokasi: halaman 11.
   - Kesimpulan sudah menyebut ETL end-to-end, 54 snapshot, 5.744 raw rows, 4.292 fact rows, quality gate, SQLite, dashboard statis, dan no dummy data.

4. **Perbedaan 5.744 raw rows dan 4.292 fact rows sudah lebih jelas.**
   - Abstrak dan kesimpulan sekarang membedakan extract menghasilkan 54 snapshot dengan total 5.744 raw rows, sedangkan transform mendekode 4.292 entri `datacontent` menjadi fact rows.

5. **Nama tabel fakta sudah konsisten `fact_statistik`.**
   - Hasil cek teks: `fact_statistic` 0, `fact_statistik` muncul berkali-kali.

6. **Mekanisme upsert sudah ditulis sesuai implementasi.**
   - Hasil cek teks: `INSERT OR REPLACE` 0, `ON CONFLICT` muncul.
   - Ini lebih sesuai `schema.sql` dan implementasi load.

7. **`run_id` load sudah cocok dengan artifact.**
   - Halaman 7 menulis `load-20260430T060939Z-6d746583`, terbelah baris tetapi nilainya benar.
   - Artifact `results/database/load_metrics.json` juga mencatat `load-20260430T060939Z-6d746583`.

8. **Evidence table sudah ditambahkan.**
   - Tabel IV.5 mengaitkan klaim hasil dengan artifact seperti `extract_manifest.json`, `transform_quality_metrics.json`, `load_metrics.json`, `dashboard-data.json`, dan output `python3 -m pytest -q`.

9. **Baseline test sudah muncul secara visual.**
   - Tabel IV.5 menampilkan `41 passed`.
   - Ini memperbaiki kelemahan reproducibility versi sebelumnya.

## Remaining Blocker Issues

### B1. Kalimat validasi menggantung di halaman 6

- Lokasi: halaman 6, bagian `F. Validasi dan Evaluasi`.
- Teks: `Command yang digunakan meliputi:` lalu langsung masuk `IV. HASIL DAN PEMBAHASAN`.
- Masalah: ini terlihat seperti konten hilang. Pembaca akan mengira command validasi terpotong, padahal command baru muncul di halaman 10 pada bagian IV.E.
- Dampak: mengganggu struktur metodologi dan reproducibility. Ini bukan typo kecil; ini cacat alur dokumen.
- Perbaikan konkret:
  - Hapus kalimat `Command yang digunakan meliputi:` dari halaman 6, atau
  - Lengkapi langsung dengan tiga command validasi di bagian metodologi, atau
  - Ubah menjadi: `Command validasi dan hasil eksekusinya dilaporkan pada bagian Evaluasi Pipeline.`

### B2. Placeholder IEEE masih terlihat di halaman pertama

- Lokasi: halaman 1, footer kiri atas/area bawah hasil ekstraksi teks.
- Teks: `XXX-X-XXXX-XXXX-X/XX/$XX.00 ©20XX IEEE`.
- Masalah: ini template placeholder mentah. Untuk laporan akhir, ini sangat memalukan karena menunjukkan PDF belum dibersihkan.
- Perbaikan konkret:
  - Hapus seluruh footer placeholder IEEE jika tidak submit ke IEEE.
  - Jangan mengganti dengan nomor palsu. Kosongkan saja.

### B3. Ordinal author salah masih muncul

- Lokasi: halaman 1, baris penulis.
- Teks: `2st Renasya Malkahaq`, `3st Febnawan Fatur Rochman`.
- Masalah: kesalahan bahasa dasar di halaman pertama. Penguji tidak perlu membaca isi untuk menemukan ini.
- Perbaikan konkret:
  - Gunakan `1st`, `2nd`, `3rd`, atau lebih baik hapus ordinal seluruhnya dan tulis nama penulis biasa.

## Remaining Major Issues

### M1. Tabel II.1 masih buruk untuk layout dua kolom

- Lokasi: halaman 3, `TABEL II.1 Penelitian Terdahulu`.
- Masalah: tabel mulai di bawah kolom kiri lalu berlanjut ke atas kolom kanan. Header memang terlihat, tetapi reading order aneh dan sel terasa penuh.
- Dampak: kajian literatur terlihat dipaksakan ke format IEEE dua kolom.
- Perbaikan konkret:
  - Ringkas kolom menjadi: `Peneliti`, `Fokus`, `Metode/Data`, `Relevansi`.
  - Kurangi teks naratif di dalam sel.
  - Jika tetap panjang, ubah menjadi tabel satu kolom lebar di bagian atas/bawah halaman.

### M2. Tabel IV.3 masih banyak word break jelek

- Lokasi: halaman 8, `TABEL IV.3 Hasil Load Metrics`.
- Contoh pemenggalan: `BP S`, `raw_api_snapsh ot`, `Perkotaan/Per desaan`.
- Masalah: tabel terbaca, tetapi tampilan tidak profesional.
- Perbaikan konkret:
  - Gunakan font lebih kecil khusus tabel.
  - Pendekkan label, misalnya `raw_api_snapshot` menjadi `raw snapshot`.
  - Hindari path/nama tabel panjang dalam sel sempit; pindahkan detail teknis ke catatan bawah tabel.

### M3. Tabel IV.5 sudah berguna tetapi format command dan path masih buruk

- Lokasi: halaman 10, `TABEL IV.5 Ringkasan antara Klaim Hasil dan Artifact Proyek`.
- Contoh: `transform_quality_metr ics.json`, command `python3 -m json.tool ... >/dev/null` wrap jelek.
- Masalah: substansinya benar, presentasinya belum layak final.
- Perbaikan konkret:
  - Gunakan nama artifact pendek di tabel: `extract_manifest`, `transform_quality`, `load_metrics`, `dashboard_data`.
  - Tambahkan catatan bawah tabel yang memetakan nama pendek ke path lengkap.
  - Format command sebagai blok monospace terpisah, bukan isi tabel yang dipaksa wrap.

### M4. Command reproducibility muncul dua kali dengan alur kurang rapi

- Lokasi: halaman 6 dan halaman 10.
- Masalah: halaman 6 menjanjikan command tetapi tidak menampilkan; halaman 10 baru menampilkan command. Ini membuat pembaca merasa ada potongan hilang.
- Perbaikan konkret:
  - Di metodologi, jelaskan jenis validasi saja.
  - Di hasil/evaluasi, tampilkan command dan hasilnya.
  - Pastikan urutannya: metode validasi -> artifact/command -> hasil.

### M5. Klaim "retry berfungsi efektif" masih perlu kehati-hatian

- Lokasi: pembahasan extract/evaluasi pipeline.
- Masalah: implementasi retry boleh diklaim ada, tetapi "berfungsi efektif" sebagai hasil runtime membutuhkan log/test yang eksplisit. Laporan belum menampilkan log retry.
- Perbaikan konkret:
  - Jika tidak ada artifact retry runtime, tulis: `pipeline mengimplementasikan retry dengan exponential backoff`.
  - Hindari klaim efektivitas operasional kecuali menyertakan test/log.

### M6. Dashboard evidence kuat, tetapi traceability baris bisa lebih tajam

- Lokasi: pembahasan dashboard dan Gambar IV.10.
- Masalah: laporan sudah menyebut `var_id`, `th_id`, `turvar_id`, `turth_id`, tetapi untuk audit baris individual sebaiknya eksplisit menyebut `data_key`, `run_id`, dan source artifact/snapshot.
- Perbaikan konkret:
  - Tambahkan satu kalimat: `Setiap baris dapat ditelusuri melalui data_key, run_id, var_id, kode_wilayah, th_id, turvar_id, turth_id, dan source_domain.`

## Remaining Minor Issues

1. **Abstrak terlalu padat.**
   - Lokasi: halaman 1.
   - Masih bisa diterima, tetapi terlalu banyak detail angka dan implementasi dalam satu blok. Jika target IEEE-style, abstrak sebaiknya lebih ringkas.

2. **Beberapa caption tidak konsisten kapitalisasinya.**
   - Contoh: `GAMBAR III.1`, `Gambar III.2`, `GAMBAR IV.10`.
   - Pilih satu gaya dan konsisten.

3. **Simbol centang pada Tabel IV.4 mungkin tidak aman untuk template.**
   - Lokasi: halaman 10.
   - Jika rendering/font bermasalah, ganti dengan `OK` atau `Passed`.

4. **Path artifact terlalu panjang untuk dua kolom.**
   - Lokasi: Tabel IV.5.
   - Gunakan alias pendek dan footnote.

5. **Istilah campuran Indonesia-Inggris masih padat.**
   - Contoh: `raw rows`, `fact rows`, `records`, `artifact`, `quality gate`.
   - Ini masih wajar untuk Rekayasa Data, tetapi definisikan sekali agar tidak terlihat asal campur.

6. **Tabel IV.4 menyebut "5 tabel lengkap" untuk dimensi, tetapi load metrics juga punya tabel audit/log.**
   - Ini tidak salah karena konteksnya dimensi, tetapi penguji bisa bertanya. Tambahkan catatan bahwa skema terdiri atas 5 dimensi, 1 fakta, dan 2 audit/log.

7. **`domain nasional (0000)` perlu terus dijaga agar tidak dibaca sebagai satu agregat nasional saja.**
   - Karena data mencakup 579 wilayah/kategori, kalimat yang paling aman adalah: `domain nasional BPS (0000) yang menyediakan metadata wilayah/kategori untuk indikator terkait`.

## Exact Locations and Suggested Fixes

| Lokasi | Masalah | Fix langsung |
|---|---|---|
| Halaman 1 | Footer `XXX-X-XXXX-XXXX-X/XX/$XX.00 ©20XX IEEE` | Hapus placeholder. Jangan isi nomor palsu. |
| Halaman 1 | `2st`, `3st` | Ubah ke `2nd`, `3rd`, atau hapus ordinal semua penulis. |
| Halaman 3 | Tabel II.1 pecah dan reading order buruk | Ringkas tabel atau buat tabel satu kolom lebar. |
| Halaman 6 | `Command yang digunakan meliputi:` menggantung | Hapus atau ganti dengan rujukan ke bagian Evaluasi Pipeline. |
| Halaman 8 | Tabel IV.3 word break buruk | Pendekkan label, kecilkan font tabel, pindahkan detail panjang ke catatan. |
| Halaman 10 | Tabel IV.5 path artifact terpotong | Gunakan alias artifact dan footnote path lengkap. |
| Halaman 10 | Command validasi wrap buruk | Pindahkan ke blok monospace di luar tabel. |
| Halaman 11 | Kesimpulan sudah baik, tetapi bisa tambah saran teknis | Tambah satu kalimat saran: scheduler, PostgreSQL, incremental update, CI validation. |

## Brutal Examiner Questions Still Likely

1. Kenapa halaman 6 menulis "Command yang digunakan meliputi:" tetapi command-nya tidak ada di situ?
2. Mengapa footer placeholder IEEE masih ada di PDF final?
3. Kenapa penulis kedua dan ketiga ditulis `2st` dan `3st`?
4. Jelaskan perbedaan 5.744 raw rows dan 4.292 fact rows tanpa membaca slide.
5. Dari artifact mana angka 54 snapshot berasal?
6. Mengapa 54 snapshot terdiri dari 30 metadata dan 24 dynamic data?
7. Kenapa `model=data` memakai `th_id`, bukan tahun 2021, 2022, 2023, 2024 langsung?
8. Tuliskan formula `datacontent` key BPS yang benar.
9. Apa beda `turvar` dan `turth`?
10. Mengapa `dim_wilayah` berisi 579 baris padahal jumlah provinsi Indonesia jauh lebih sedikit?
11. Apa grain dari `fact_statistik`?
12. Bagaimana `ON CONFLICT DO UPDATE` mencegah duplikasi fact rows?
13. Bagaimana membuktikan dashboard tidak memakai dummy data?
14. Di mana bukti `pytest 41 passed` dan kapan command itu dijalankan?
15. Jika BPS mengubah struktur response JSON, bagian pipeline mana yang paling mungkin rusak?
16. Kenapa memilih SQLite, dan pada kondisi apa harus pindah ke PostgreSQL/data warehouse?

## Final Checklist Before Submit

- [ ] Hapus footer placeholder IEEE di halaman 1.
- [ ] Perbaiki `2st` dan `3st` atau hilangkan ordinal author.
- [ ] Hilangkan kalimat menggantung `Command yang digunakan meliputi:` di halaman 6.
- [ ] Rapikan Tabel II.1 agar reading order tidak aneh.
- [ ] Rapikan Tabel IV.3 agar tidak ada word break seperti `BP S` dan `raw_api_snapsh ot`.
- [ ] Rapikan Tabel IV.5 dengan alias artifact pendek.
- [ ] Pindahkan command validasi ke blok monospace agar tidak wrap buruk.
- [ ] Pastikan `python3 -m json.tool dashboard/data/dashboard-data.json >/dev/null` tampil utuh.
- [ ] Pertahankan angka inti: 6 indikator, 2021-2024, 579 wilayah/kategori, 54 snapshot, 5.744 raw rows, 4.292 fact rows.
- [ ] Pertahankan semantik BPS API: `model=data` memakai `th_id`; key `datacontent` didekode dengan `vervar.val + var.val + turvar.val + tahun.val + turtahun.val`.
- [ ] Pertahankan evidence table, tetapi perbaiki layout-nya.
- [ ] Export ulang PDF dan cek visual halaman 1, 3, 6, 8, 10, 11 sebelum submit.

## Conclusion

Revisi 2 ini **sudah menyelesaikan blocker teknis utama** dan secara substansi proyek sudah kuat. Evidence ETL cocok dengan artifact nyata, angka inti konsisten, dashboard tidak terlihat dummy, dan kesimpulan sudah hadir.

Tetapi PDF ini **belum submit-ready** karena masih ada cacat visual dan alur yang terlalu jelas untuk laporan final: placeholder IEEE, ordinal author salah, kalimat validasi menggantung, dan tabel-tabel yang masih pecah. Jika dikumpulkan sekarang, nilainya masih bisa baik karena substansi kuat, tetapi penguji akan tetap menandai kerapian dokumen sebagai kelemahan serius.

Verdict akhir: **LAYAK DENGAN REVISI**.
