# Aksi Perbaikan Laporan Akhir

## Prioritas P0 - Wajib Sebelum Submit

### P0.1 Tambahkan `V. KESIMPULAN`

- Lokasi laporan: setelah bagian keterbatasan pada `IV. HASIL DAN PEMBAHASAN`, sebelum `DAFTAR PUSTAKA`.
- Masalah: tidak ada section Kesimpulan eksplisit.
- Alasan: laporan akhir tanpa kesimpulan terlihat belum selesai dan mudah diserang saat sidang.
- Tindakan perbaikan: tambah section `V. KESIMPULAN` yang menjawab tujuan penelitian, merangkum hasil ETL, dashboard, validasi, keterbatasan, dan saran.
- Contoh kalimat:

```text
V. KESIMPULAN

Penelitian ini berhasil merancang dan mengimplementasikan pipeline ETL end-to-end berbasis Web API BPS untuk enam indikator sosial ekonomi pada periode 2021-2024. Proses extract menghasilkan 54 snapshot JSON yang terdiri dari 30 snapshot metadata dan 24 snapshot data dinamis dengan total 5.744 raw rows. Tahap transform berhasil mendekode 4.292 entri datacontent menjadi fact rows dengan quality gate passed, unmatched_count 0, duplicate_fact_key_count 0, dan null_value_count 0. Tahap load memuat data ke SQLite star schema yang terdiri atas lima tabel dimensi, satu tabel fakta, dan dua tabel audit/log.

Dashboard analitik statis berhasil dibangun menggunakan HTML, CSS, JavaScript, dan ECharts dengan sumber data dari dashboard/data/dashboard-data.json yang digenerasi dari SQLite. Dashboard menampilkan ringkasan cakupan data, tren indikator, ranking wilayah, narasi otomatis, dan tabel fakta tanpa menggunakan data dummy.

Keterbatasan penelitian ini adalah pipeline masih bersifat batch manual, basis data menggunakan SQLite, dan dashboard memakai JSON statis sehingga pembaruan data memerlukan eksekusi ulang pipeline dan generator dashboard. Pengembangan berikutnya dapat diarahkan pada penjadwalan otomatis, incremental extract, database server seperti PostgreSQL, serta validasi CI untuk artifact ETL dan dashboard.
```

- Estimasi effort: 20-30 menit.

### P0.2 Perbaiki `truth` menjadi `turth`

- Lokasi laporan: `IV.A Hasil Ekstraksi Data`, kalimat endpoint.
- Masalah: tertulis `truth`, padahal endpoint benar adalah `turth`.
- Alasan: ini typo teknis fatal pada konteks Web API BPS.
- Tindakan perbaikan:

```text
Sebelum:
th, vervar, turvar, truth, unit, dan data.

Sesudah:
th, vervar, turvar, turth, unit, dan data.
```

- Estimasi effort: 2 menit.

### P0.3 Perbaiki rumus composite key

- Lokasi laporan: `IV.B Hasil Transformasi dan Validasi Kualitas Data`, rumus halaman 7.
- Masalah: tertulis `turvar.var`.
- Alasan: field benar adalah `turvar.val`; kesalahan ini membuat decoding `datacontent` tampak salah.
- Tindakan perbaikan:

```text
Sebelum:
vervar.val + var.val + turvar.var + tahun.val + turtahun.val

Sesudah:
vervar.val + var.val + turvar.val + tahun.val + turtahun.val
```

- Estimasi effort: 2 menit.

### P0.4 Samakan `run_id` load dengan artifact aktual

- Lokasi laporan: `IV.C Hasil Pemuatan Data`.
- Masalah: laporan memakai `load-20260501T064612Z-8f5abc4f`, tetapi artifact aktual memakai `load-20260430T060939Z-6d746583`.
- Alasan: evidence-first. Laporan harus cocok dengan `results/database/load_metrics.json` dan `dashboard/data/dashboard-data.json`.
- Tindakan perbaikan:

```text
Sebelum:
run_id load-20260501T064612Z-8f5abc4f, dimulai dan selesai pada 2026-05-01T06:46:12Z.

Sesudah:
run_id load-20260430T060939Z-6d746583, dimulai dan selesai pada 2026-04-30T06:09:39Z.
```

- Estimasi effort: 5 menit.

### P0.5 Perbaiki abstrak agar tidak mencampur extract dan transform

- Lokasi laporan: Abstrak.
- Masalah: "Proses ekstraksi menghasilkan 4.292 rekaman data" tidak presisi. Extract manifest mencatat 5.744 raw rows; transform/fact menghasilkan 4.292 rows.
- Alasan: penguji akan membandingkan dengan Tabel IV.4 dan artifact.
- Tindakan perbaikan:

```text
Ganti kalimat:
Proses ekstraksi menghasilkan 4.292 rekaman data yang kemudian ditransformasi melalui dekoding composite key dan normalisasi nilai numerik.

Dengan:
Proses ekstraksi menghasilkan 54 snapshot JSON dengan total 5.744 raw rows, sedangkan tahap transform mendekode 4.292 entri datacontent menjadi fact rows melalui pemetaan composite key dan normalisasi nilai numerik.
```

- Estimasi effort: 10 menit.

## Prioritas P1 - Sangat Disarankan

### P1.1 Perjelas "domain nasional" vs "tingkat nasional"

- Lokasi laporan: Abstrak, Pendahuluan, Pengumpulan Data, Hasil Ekstraksi.
- Masalah: frasa "tingkat nasional" bisa dibaca sebagai hanya satu agregat Indonesia, padahal data memuat 579 wilayah/kategori.
- Alasan: artifact menunjukkan provinsi, nasional, dan kategori turunan dari metadata `vervar`.
- Tindakan perbaikan:

```text
Ganti:
pada tingkat nasional

Dengan:
pada domain nasional BPS (kode 0000) yang memuat wilayah/kategori sesuai metadata BPS, termasuk provinsi, nasional, dan kategori turunan indikator
```

- Estimasi effort: 10-15 menit.

### P1.2 Perbaiki Tabel III.2 yang salah nomor

- Lokasi laporan: halaman 5.
- Masalah: tertulis `TABEL I.2 HASIL INDIKATOR RESPONS API`.
- Alasan: nomor tabel salah dan judul kurang akademik.
- Tindakan perbaikan:

```text
TABEL III.2 RINGKASAN INDIKATOR DAN JUMLAH RECORD DATACONTENT
```

- Estimasi effort: 5 menit.

### P1.3 Konsistenkan "enam model endpoint" dan "lima metadata + satu data"

- Lokasi laporan: `III.C Pengumpulan Data`.
- Masalah: satu paragraf menyebut enam model, lalu "Kelima model endpoint".
- Alasan: inkonsistensi kecil tetapi terlihat.
- Tindakan perbaikan:

```text
Penelitian ini menggunakan enam model endpoint API, yaitu lima model metadata (th, vervar, turvar, turth, dan unit) serta satu model data dinamis (data).
```

- Estimasi effort: 5 menit.

### P1.4 Perbaiki deskripsi model `unit`

- Lokasi laporan: Tabel III.1.
- Masalah: fungsi `unit` tertulis mengambil nilai statistik aktual.
- Alasan: `unit` adalah metadata satuan, bukan data nilai statistik.
- Tindakan perbaikan:

| Model | Parameter | Fungsi | Output Utama |
|---|---|---|---|
| unit | var, domain | Mengambil metadata satuan/definisi satuan untuk variabel indikator | unit, deskripsi satuan |

- Catatan: jika implementasi hanya mengirim `var`, sesuaikan parameter menjadi `var` agar sama dengan manifest.
- Estimasi effort: 10 menit.

### P1.5 Tambahkan tabel evidence artifact

- Lokasi laporan: akhir Metode atau awal Hasil.
- Masalah: klaim hasil belum dipetakan eksplisit ke artifact.
- Alasan: proyek ini evidence-first; tabel ini membuat sidang lebih aman.
- Tindakan perbaikan:

| Klaim | Nilai | Artifact |
|---|---:|---|
| Metadata snapshots | 30 | `results/api/extract/extract_manifest.json` |
| Dynamic snapshots | 24 | `results/api/extract/extract_manifest.json` |
| Total raw rows extract | 5.744 | `results/api/extract/extract_manifest.json` |
| Fact rows transform | 4.292 | `results/tables/transform/transform_quality_metrics.json` |
| Quality gate | passed | `results/tables/transform/transform_quality_metrics.json` |
| SQLite fact rows | 4.292 | `results/database/load_metrics.json` |
| Dashboard no dummy data | true | `dashboard/data/dashboard-data.json` |
| Test baseline | 41 passed | output `python3 -m pytest -q` |

- Estimasi effort: 20-30 menit.

### P1.6 Tambahkan subsection reproducibility

- Lokasi laporan: `III.F Validasi dan Evaluasi` atau setelah Tabel IV.4.
- Masalah: belum ada command re-run dan test baseline.
- Alasan: Rekayasa Data menilai reproducibility, bukan hanya screenshot.
- Tindakan perbaikan:

```text
Validasi reproducibility dilakukan dengan menjalankan command:
1. python3 -m py_compile scripts/*.py
2. python3 -m pytest -q
3. python3 -m json.tool dashboard/data/dashboard-data.json >/dev/null

Hasil baseline pengujian menunjukkan 41 test passed, sehingga kode ETL, schema, transform, load, dan dashboard data generator dapat dijalankan tanpa error pada lingkungan pengujian proyek.
```

- Estimasi effort: 15 menit.

### P1.7 Kurangi klaim performa yang tidak punya metrik presisi

- Lokasi laporan: `IV.C Hasil Pemuatan Data`.
- Masalah: "durasi di bawah satu detik" tidak punya artifact durasi presisi.
- Alasan: timestamp detik sama bukan benchmark.
- Tindakan perbaikan:

```text
Ganti:
Proses pemuatan berhasil diselesaikan dalam durasi di bawah satu detik.

Dengan:
Pada artifact load_metrics.json, waktu mulai dan selesai tercatat pada timestamp detik yang sama, sehingga proses load untuk cakupan data ini relatif ringan. Laporan ini tidak melakukan benchmark performa presisi.
```

- Estimasi effort: 5 menit.

## Prioritas P2 - Perapian Format dan Nilai Tambahan

### P2.1 Perbesar gambar dashboard

- Lokasi laporan: Gambar IV.3 sampai IV.10.
- Masalah: beberapa screenshot terlalu kecil dan teks dashboard tidak terbaca.
- Tindakan perbaikan: gunakan crop per komponen, bukan screenshot full dashboard; pastikan setiap gambar minimal memperlihatkan label sumbu/angka.
- Estimasi effort: 30-45 menit.

### P2.2 Perbaiki Tabel IV.3 yang pecah

- Lokasi laporan: halaman 7-8.
- Masalah: sel tabel terpotong (`BP S`, `snapsh ot`, `Perkotaan/Per desaan`).
- Tindakan perbaikan: pecah menjadi dua tabel:
  - Tabel IV.3a: dimensi dan fact table.
  - Tabel IV.3b: audit/log table dan idempotency.
- Estimasi effort: 20-30 menit.

### P2.3 Bersihkan template IEEE

- Lokasi laporan: footer halaman 1 dan header author.
- Masalah: placeholder `XXX-X-XXXX-XXXX-X/XX/$XX.00 ©20XX IEEE`; ordinal `2st`, `3st`.
- Tindakan perbaikan:
  - hapus footer placeholder jika bukan prosiding IEEE resmi;
  - ubah `2st`/`3st` menjadi `2nd`/`3rd` atau hilangkan ordinal.
- Estimasi effort: 10 menit.

### P2.4 Rapikan referensi

- Lokasi laporan: Daftar Pustaka.
- Masalah: kapitalisasi judul campur, beberapa metadata kurang rapi.
- Tindakan perbaikan:
  - pastikan semua referensi punya author, judul, venue, volume/issue/pages jika ada, tahun, DOI/URL;
  - pastikan BPS API documentation tetap ada dengan access date;
  - hindari referensi yang tidak jelas venue-nya jika ada pengganti lebih kuat.
- Estimasi effort: 30-45 menit.

## Urutan Pengerjaan 1-N

1. Perbaiki `truth` -> `turth`.
2. Perbaiki formula composite key `turvar.var` -> `turvar.val`.
3. Samakan `run_id` dan timestamp load dengan `load_metrics.json`.
4. Revisi abstrak agar membedakan 5.744 raw rows extract dan 4.292 fact rows.
5. Tambahkan `V. KESIMPULAN`.
6. Perbaiki nomor dan judul Tabel III.2.
7. Perbaiki definisi model `unit` dan konsistensi "enam model endpoint".
8. Tambahkan tabel evidence artifact.
9. Tambahkan subsection reproducibility dan `pytest 41 passed`.
10. Perjelas "domain nasional BPS (0000)".
11. Rapikan Tabel IV.3.
12. Perbesar/crop gambar dashboard.
13. Bersihkan footer placeholder IEEE dan ordinal author.
14. Rapikan referensi.

## Quick Fixes 30 Menit

- `truth` -> `turth`.
- `turvar.var` -> `turvar.val`.
- Ganti `run_id` load ke `load-20260430T060939Z-6d746583`.
- Ganti timestamp load ke `2026-04-30T06:09:39Z`.
- Perbaiki abstrak: 54 snapshot, 5.744 raw rows, 4.292 fact rows.
- Ubah `TABEL I.2` menjadi `TABEL III.2`.
- Ubah `2st`/`3st` atau hilangkan ordinal author.

## Fixes 1-2 Jam

- Tambahkan `V. KESIMPULAN`.
- Tambahkan tabel evidence artifact.
- Tambahkan subsection reproducibility dengan command validasi dan `41 passed`.
- Revisi frasa "tingkat nasional" menjadi "domain nasional BPS (0000) yang memuat wilayah/kategori".
- Perbaiki Tabel III.1 untuk `unit`.
- Pecah Tabel IV.3 agar tidak rusak di dua kolom.

## Fixes Jika Masih Ada Waktu

- Crop ulang screenshot dashboard agar setiap gambar terbaca.
- Rapikan caption gambar/tabel agar konsisten.
- Rapikan Daftar Pustaka sesuai gaya IEEE.
- Tambahkan saran pengembangan teknis: scheduler, incremental extract, PostgreSQL, CI artifact validation.
- Kurangi klaim yang tidak punya artifact, terutama klaim performa dan efektivitas retry runtime.

## Checklist Final Sebelum Submit

- [ ] Ada section `V. KESIMPULAN`.
- [ ] Tidak ada kata `truth` untuk endpoint BPS; semuanya `turth`.
- [ ] Rumus composite key memakai `turvar.val`.
- [ ] `run_id` load sama dengan `results/database/load_metrics.json`.
- [ ] Abstrak membedakan 5.744 raw rows extract dan 4.292 fact rows.
- [ ] Angka 6 indikator, 2021-2024, 579 wilayah/kategori, 4.292 fact rows, 54 snapshot konsisten di seluruh laporan.
- [ ] Tabel III.2 bernomor benar.
- [ ] Model `unit` dijelaskan sebagai metadata satuan.
- [ ] Ada tabel evidence artifact.
- [ ] Ada command reproducibility dan hasil `pytest 41 passed`.
- [ ] Gambar dashboard terbaca.
- [ ] Tabel IV.3 tidak pecah secara buruk.
- [ ] Footer placeholder IEEE dihapus atau diisi sesuai aturan kampus/template.
- [ ] Referensi rapi dan semua sitasi di teks muncul di Daftar Pustaka.
