# Review Brutal Kajian Literatur dan Metodologi

**Dokumen direview:** `docs/001_007_029_Kelompok 17_Laporan Projek Akhir Rekayasa Data.pdf`  
**Judul laporan:** Perancangan ETL Pipeline dan Dashboard Analitik Berbasis Web API Badan Pusat Statistik untuk Pemantauan Data Sosial Ekonomi Indonesia  
**Fokus review:** BAB II Kajian Literatur dan BAB III Metode Penelitian  
**Basis pembanding:** artifact proyek aktual di repo `etl-bps-dashboard-analitik`

---

## 1. Verdict Umum

Kajian literatur dan metodologi **sudah bisa diselamatkan**, bahkan sudah cukup dekat dengan proyek aktual. Namun versi saat ini **belum layak final** karena masih ada masalah teknis, format, dan ketajaman argumen.

Skor kasar:

| Bagian | Skor | Verdict |
|---|---:|---|
| Kajian Literatur | 78/100 | Cukup, tetapi masih terlalu umum/textbook |
| Metodologi | 82/100 | Relevan dengan proyek, tetapi ada inkonsistensi teknis |
| Format tabel/gambar | 65–70/100 | Perlu dirapikan serius |

Kesimpulan brutal: **isi besarnya sudah benar, tetapi belum bersih.** Masalah utama bukan karena topiknya salah, melainkan karena beberapa bagian masih terasa generik, beberapa klaim tidak akurat terhadap implementasi, dan layout tabel/gambar masih seperti draft.

---

## 2. Review Kajian Literatur

### 2.1 Yang Sudah Bagus

Struktur kajian literatur sudah masuk akal:

1. Data Sosial Ekonomi dan BPS.
2. ETL Pipeline.
3. Basis Data Analitik.
4. Dashboard Analitik.
5. Penelitian Terdahulu.

Bagian ini sudah relevan dengan proyek karena membahas BPS, ETL, basis data analitik, dashboard, dan penelitian terdahulu. Gap penelitian juga sudah mengarah ke integrasi ETL end-to-end berbasis Web API BPS.

Namun, masih perlu ditajamkan agar lebih spesifik ke proyek.

---

### 2.2 Masalah: Kajian Literatur Terlalu Textbook

Bagian ETL, basis data analitik, dan dashboard masih banyak berisi definisi umum. Contohnya, bagian ETL menjelaskan bahwa ETL terdiri dari extract, transform, dan load. Itu benar, tetapi masih terlalu dasar.

Masalahnya: laporan ini bukan sekadar menjelaskan apa itu ETL. Laporan ini harus menjelaskan **mengapa ETL dibutuhkan untuk kasus Web API BPS**.

#### Contoh bagian yang terlalu textbook

> Extract, Transform, Load (ETL) merupakan serangkaian tahapan yang mencakup pengambilan data dari berbagai sumber, pengolahan data melalui proses pembersihan dan standarisasi, serta pemuatan data ke dalam sistem penyimpanan yang terstruktur untuk mendukung keperluan analisis.

Kalimat ini benar, tetapi bisa muncul di laporan ETL mana pun. Belum menunjukkan konteks BPS.

#### Contoh perbaikan

> Dalam penelitian ini, konsep ETL digunakan untuk mengolah data statistik dari Web API BPS yang tersedia dalam format JSON. Tahap *extract* digunakan untuk mengambil metadata dan data dinamis dari beberapa model endpoint, seperti `th`, `vervar`, `turvar`, `turth`, `unit`, dan `data`. Tahap *transform* diperlukan karena nilai statistik pada `model=data` disajikan dalam objek `datacontent` yang perlu dipetakan kembali ke metadata wilayah, indikator, dan waktu. Setelah data berhasil dinormalisasi, tahap *load* memuat data ke dalam basis data SQLite agar dapat digunakan sebagai sumber dashboard analitik.

Kenapa versi ini lebih baik:

- langsung nyambung ke proyek;
- menyebut Web API BPS;
- menyebut endpoint yang benar;
- menyebut `datacontent`;
- menjelaskan alasan transformasi;
- tidak berhenti di definisi umum.

---

### 2.3 Masalah: Kajian BPS Belum Cukup Teknis

Bagian BPS sudah menyebut Web API, JSON, HTTP, tabel dinamis, tabel statis, publikasi, dan siaran pers. Itu bagus. Namun, inti teknis Web API BPS belum cukup dijelaskan.

Untuk proyek ini, hal yang penting bukan hanya “BPS menyediakan API”, tetapi:

- API BPS punya beberapa `model` endpoint;
- `model=data` tidak langsung menghasilkan tabel rapi;
- nilai statistik disimpan dalam `datacontent`;
- `datacontent` memakai composite key;
- parameter `th` pada `model=data` memakai `th_id`, bukan tahun kalender.

#### Contoh perbaikan subbagian baru

Tambahkan subbagian berikut di Kajian Literatur:

```text
B. Web API BPS dan Data Statistik Dinamis
```

Isi yang disarankan:

> Web API BPS menyediakan akses data statistik dalam format JSON melalui endpoint `https://webapi.bps.go.id/v1/api/list`. Layanan ini mendukung beberapa model data, seperti `th`, `vervar`, `turvar`, `turth`, `unit`, dan `data`. Model `th` digunakan untuk memperoleh daftar periode yang tersedia, sedangkan `vervar`, `turvar`, `turth`, dan `unit` digunakan untuk memperoleh metadata pendukung. Sementara itu, model `data` digunakan untuk mengambil nilai statistik aktual.
>
> Pada tabel dinamis BPS, nilai statistik tidak selalu tersedia dalam bentuk baris tabel siap pakai. Nilai tersebut disajikan dalam objek `datacontent` dengan kunci gabungan yang perlu dipetakan kembali ke metadata. Oleh karena itu, data dari Web API BPS membutuhkan proses transformasi sebelum dapat disimpan dalam basis data relasional dan digunakan pada dashboard analitik.

---

### 2.4 Masalah: Dashboard Menyebut Visualisasi yang Tidak Ada di Proyek

Di bagian Dashboard Analitik disebutkan contoh visualisasi seperti:

> grafik garis, peta koropleth, diagram batang, serta KPI

Masalahnya, dashboard proyek ini tidak memakai peta koropleth. Dashboard yang dibuat lebih tepat disebut menampilkan:

- KPI ringkas;
- grafik tren;
- ranking/peringkat wilayah;
- tabel detail;
- narasi otomatis;
- filter indikator, wilayah, dan tahun.

Kalau tetap menulis “peta koropleth”, dosen bisa bertanya: **“peta koropleth-nya mana?”**

#### Contoh perbaikan

Sebelum:

> Dashboard berperan sebagai lapisan presentasi yang mengubah data kompleks menjadi visualisasi yang mudah dipahami, seperti grafik garis, peta koropleth, diagram batang, serta indikator kinerja utama.

Sesudah:

> Dashboard berperan sebagai lapisan presentasi yang mengubah data statistik menjadi visualisasi yang lebih mudah dipahami, seperti grafik tren, diagram peringkat, tabel detail, narasi ringkas, serta indikator kinerja utama. Pada penelitian ini, dashboard digunakan untuk memantau enam indikator sosial ekonomi berdasarkan hasil proses ETL dari Web API BPS.

---

### 2.5 Masalah: Tabel Penelitian Terdahulu Terlalu Padat

Secara isi, tabel penelitian terdahulu sudah cukup bagus. Ada pembanding dari domain pendidikan, e-commerce, dan kesehatan. Gap-nya juga sudah diarahkan ke API publik, BPS, dan data sosial ekonomi.

Namun secara layout PDF, tabelnya bermasalah:

- tabel pecah antar kolom;
- header tidak diulang;
- teks `K-Means` terpotong menjadi `K-` dan `Means` di kolom berbeda;
- kolom terlalu sempit;
- isi terlalu panjang;
- sulit dibaca di format IEEE dua kolom.

#### Solusi format

Pilih salah satu:

1. Jadikan tabel full-width dua kolom.
2. Ringkas isi tabel.
3. Pindahkan detail panjang ke lampiran.
4. Di body laporan, tampilkan hanya ringkasan pendek.

#### Contoh tabel yang lebih rapi

| Penelitian | Domain | Pendekatan | Keterbatasan terhadap penelitian ini |
|---|---|---|---|
| Setiyawati dkk. [10] | Pendidikan | ETL untuk data penerimaan mahasiswa | Data berasal dari basis data internal, belum dari API publik dan tidak menghasilkan dashboard analitik sosial ekonomi. |
| Hutabalian dkk. [11] | E-commerce | ETL/ELT, PostgreSQL, Star Schema, Superset | Data berasal dari file ekspor statis, bukan Web API publik. Domain bukan data sosial ekonomi resmi. |
| Putri dkk. [28] | Kesehatan | Business Intelligence, ETL, OLAP, clustering | Data diperoleh dari laporan operasional/manual, belum memakai API publik dan belum fokus pada indikator sosial ekonomi BPS. |

Contoh narasi setelah tabel:

> Berdasarkan penelitian terdahulu, ETL dan dashboard telah digunakan pada berbagai domain, seperti pendidikan, e-commerce, dan kesehatan. Namun, sebagian besar penelitian tersebut masih menggunakan data internal, file statis, atau laporan manual. Penelitian ini berbeda karena menggunakan Web API BPS sebagai sumber data resmi, melakukan pemetaan metadata JSON, menerapkan validasi kualitas data, menyimpan hasil transformasi ke basis data SQLite, dan menyajikan hasilnya dalam dashboard berbasis web.

---

## 3. Review Metodologi

### 3.1 Yang Sudah Bagus

Metodologi sudah cukup dekat dengan proyek aktual. Bagian ini menyebut banyak detail yang benar:

- Web API BPS;
- endpoint `https://webapi.bps.go.id/v1/api/list`;
- `th_id`;
- `datacontent`;
- composite key BPS;
- SQLite;
- star schema;
- `dashboard-data.json`;
- HTML/CSS/JavaScript;
- enam indikator;
- periode 2021–2024;
- 4.292 records;
- 54 snapshot;
- quality gate.

Ini nilai plus besar. Metodologi tidak lagi mengawang-ngawang.

---

### 3.2 Masalah: Jumlah Lapisan Arsitektur Salah

Di laporan tertulis:

> terdiri atas empat lapisan utama

Tetapi setelah itu dijelaskan lima lapisan:

1. lapisan sumber data;
2. lapisan ETL pipeline;
3. lapisan basis data analitik;
4. lapisan jembatan data;
5. lapisan presentasi.

Ini inkonsisten.

#### Contoh perbaikan

> Arsitektur sistem yang dikembangkan dalam penelitian ini dirancang menggunakan pendekatan berlapis yang terdiri atas lima lapisan utama, yaitu lapisan sumber data, lapisan ETL pipeline, lapisan basis data analitik, lapisan jembatan data, dan lapisan presentasi. Pemisahan lapisan ini bertujuan agar proses pengambilan data, pengolahan, penyimpanan, dan penyajian informasi dapat dikembangkan serta divalidasi secara terpisah.

---

### 3.3 Masalah: Nama Tabel Fakta Salah

Di laporan tertulis:

```text
fact_statistic
```

Padahal di implementasi repo, nama tabel yang benar adalah:

```text
fact_statistik
```

Bukti dari schema:

```sql
CREATE TABLE IF NOT EXISTS fact_statistik (...)
```

#### Contoh perbaikan

Sebelum:

> terdiri dari satu tabel fakta (fact_statistic) dan tabel dimensi...

Sesudah:

> terdiri dari satu tabel fakta (`fact_statistik`) dan lima tabel dimensi, yaitu `dim_indikator`, `dim_wilayah`, `dim_waktu`, `dim_turvar`, dan `dim_turtahun`.

Pastikan juga gambar arsitektur dan tabel metodologi memakai nama yang sama.

---

### 3.4 Masalah: Endpoint `unit` Hilang

Di laporan tertulis:

> Penelitian ini menggunakan lima model endpoint API secara berurutan. Model th, vervar, turvar, dan turth digunakan untuk mengambil metadata dimensi, sedangkan model data digunakan untuk mengambil nilai statistik aktual.

Masalahnya, implementasi proyek juga mengambil metadata `unit`.

Bukti artifact:

```text
metadata_snapshot_count = 30
6 indikator × 5 model metadata = 30 snapshot
```

Model metadata yang dipakai:

- `th`
- `vervar`
- `turvar`
- `turth`
- `unit`

Model data:

- `data`

#### Contoh perbaikan

> Penelitian ini menggunakan enam model endpoint API BPS, yaitu `th`, `vervar`, `turvar`, `turth`, `unit`, dan `data`. Model `th` digunakan untuk memperoleh daftar periode dan `th_id`, `vervar` digunakan untuk memperoleh metadata wilayah atau kategori vertikal, `turvar` dan `turth` digunakan untuk memperoleh klasifikasi turunan, sedangkan `unit` digunakan untuk memperoleh satuan indikator. Model `data` digunakan untuk mengambil nilai statistik aktual berdasarkan kombinasi `var_id` dan `th_id`.

#### Contoh tabel endpoint yang benar

| Model | Parameter utama | Fungsi | Output utama |
|---|---|---|---|
| `th` | `var`, `domain` | Mengambil daftar periode yang tersedia untuk indikator | `th_id`, tahun, label periode |
| `vervar` | `var`, `domain` | Mengambil metadata wilayah/kategori vertikal | kode wilayah, nama wilayah |
| `turvar` | `var`, `domain` | Mengambil klasifikasi variabel turunan | `turvar_id`, label |
| `turth` | `var`, `domain` | Mengambil klasifikasi periode turunan | `turth_id`, label |
| `unit` | `var`, `domain` | Mengambil satuan atau unit indikator | unit, deskripsi satuan |
| `data` | `var`, `th`, `domain` | Mengambil nilai statistik aktual | `datacontent`, `last_update` |

---

### 3.5 Masalah: Penjelasan 54 Snapshot Ambigu

Di laporan tertulis:

> Total snapshot yang dihasilkan berjumlah 54 berkas JSON yang merepresentasikan 6 indikator × 4 tahun dengan kelima model metadata masing-masing.

Kalimat ini ambigu. Bisa terbaca sebagai:

```text
6 indikator × 4 tahun × 5 model metadata = 120 snapshot
```

Padahal jumlah sebenarnya:

```text
metadata: 6 indikator × 5 model metadata = 30 snapshot
data dinamis: 6 indikator × 4 tahun = 24 snapshot
total: 30 + 24 = 54 snapshot
```

#### Contoh perbaikan

> Total snapshot yang dihasilkan berjumlah 54 berkas JSON. Jumlah tersebut terdiri dari 30 snapshot metadata yang diperoleh dari 6 indikator × 5 model metadata (`th`, `vervar`, `turvar`, `turth`, dan `unit`), serta 24 snapshot data dinamis yang diperoleh dari 6 indikator × 4 tahun periode 2021–2024. Seluruh snapshot disimpan pada direktori `results/api/extract/` dengan checksum SHA-256 untuk mendukung keterlacakan data.

---

### 3.6 Masalah: Frasa “Penanganan Nilai Hilang” Kurang Tepat

Di metodologi tertulis bahwa transform mencakup:

> penanganan nilai hilang

Masalahnya, implementasi proyek tidak melakukan imputasi atau pengisian nilai hilang. Yang dilakukan adalah validasi agar nilai null tidak masuk ke data final.

Artifact kualitas data menunjukkan:

```json
{
  "null_value_count": 0,
  "quality_gate": "passed"
}
```

Artinya pipeline memvalidasi nilai hilang, bukan menangani dengan imputasi.

#### Contoh perbaikan

Sebelum:

> transform (pemetaan metadata, normalisasi, dan penanganan nilai hilang)

Sesudah:

> transform (decoding `datacontent`, pemetaan metadata, normalisasi nilai numerik, dan validasi nilai null)

Atau:

> transform mencakup validasi terhadap nilai hilang, bukan imputasi nilai.

---

### 3.7 Masalah: Klaim “Akurasi Data” Terlalu Berani

Di metodologi disebutkan validasi kualitas data mencakup:

> kelengkapan, konsistensi, dan akurasi

Masalahnya, sistem tidak membandingkan nilai dengan publikasi BPS manual atau sumber eksternal. Jadi klaim “akurasi” terlalu kuat.

Yang dibuktikan sistem adalah:

- raw data berhasil diambil dari API;
- jumlah raw `datacontent` sama dengan jumlah decoded row;
- tidak ada unmatched key;
- tidak ada nilai null;
- tidak ada duplikasi fact grain;
- jumlah load sesuai transform;
- snapshot punya checksum.

Itu lebih tepat disebut validasi struktur, konsistensi, kelengkapan, dan keterlacakan.

#### Contoh perbaikan

Sebelum:

> dilakukan validasi kualitas data mencakup aspek kelengkapan, konsistensi, dan akurasi.

Sesudah:

> dilakukan validasi kualitas data yang mencakup kelengkapan hasil ekstraksi, konsistensi struktur data, keterlacakan sumber data, kesesuaian jumlah baris hasil transformasi, serta ketiadaan nilai null dan duplikasi fact grain.

---

### 3.8 Masalah: Klaim `INSERT OR REPLACE` Tidak Sesuai Implementasi

Di laporan tertulis:

> Pemuatan data menggunakan mekanisme upsert berbasis INSERT OR REPLACE

Padahal implementasi memakai:

```sql
ON CONFLICT(...) DO UPDATE SET ...
```

Ini lebih tepat daripada `INSERT OR REPLACE` karena update dilakukan berdasarkan primary key atau fact grain.

#### Contoh perbaikan

> Pemuatan data menggunakan mekanisme upsert berbasis `ON CONFLICT DO UPDATE`. Pada tabel dimensi, konflik ditangani berdasarkan primary key masing-masing tabel. Pada tabel fakta, konflik ditangani berdasarkan fact grain `var_id + kode_wilayah + th_id + turvar_id + turth_id + source_domain`, sehingga pipeline dapat dijalankan ulang tanpa menghasilkan duplikasi baris bisnis.

---

### 3.9 Masalah: Domain Nasional `0000` Bisa Disalahpahami

Di laporan tertulis:

> domain nasional (kode 0000)

Ini tidak salah, tetapi bisa disalahpahami seolah-olah data hanya berisi satu agregat nasional. Padahal data hasil ETL mencakup 579 wilayah/kategori dari metadata `vervar`.

#### Contoh perbaikan

> Pengambilan data dilakukan pada domain BPS pusat (`0000`). Domain ini digunakan sebagai sumber API untuk indikator yang dipilih, dengan cakupan wilayah atau kategori yang diperoleh dari metadata `vervar` pada masing-masing indikator.

Atau:

> Meskipun endpoint menggunakan domain `0000`, data yang diperoleh tetap mencakup wilayah/kategori yang tersedia pada metadata BPS, bukan hanya satu baris agregat nasional.

---

### 3.10 Masalah: Validasi Dashboard Belum Dijelaskan Cukup

Metodologi sudah menjelaskan validasi transform dan load. Namun validasi dashboard belum cukup jelas.

Padahal proyek punya validasi dashboard:

- `dashboard-data.json` valid;
- `no_dummy_data = true`;
- `table_rows = 4292`;
- chart series tersedia;
- JavaScript syntax valid;
- dashboard live di GitHub Pages;
- test suite 41 passed.

#### Contoh tambahan metodologi

> Validasi dashboard dilakukan dengan memastikan file `dashboard-data.json` memiliki struktur yang sesuai dengan kontrak data dashboard, mencakup `indicators`, `years`, `regions`, `series`, `rankings`, dan `table_rows`. Selain itu, jumlah baris pada `table_rows` diverifikasi agar sesuai dengan jumlah baris pada tabel fakta, yaitu 4.292 baris. Sistem juga memeriksa flag `no_dummy_data` untuk memastikan dashboard tidak menggunakan data dummy. Validasi teknis dilakukan melalui pemeriksaan sintaks JavaScript, pengujian otomatis menggunakan `pytest`, dan verifikasi akses dashboard pada GitHub Pages.

---

### 3.11 Masalah: Tidak Ada Command Reproducibility

Metodologi akan jauh lebih kuat jika menyertakan alur command pipeline. Ini penting untuk mata kuliah Rekayasa Data karena menunjukkan bahwa pipeline dapat dijalankan ulang.

#### Contoh tambahan

```bash
python3 scripts/verify_bps_api.py
python3 scripts/run_etl.py --phase extract --mode quick
python3 scripts/run_etl.py --phase transform --mode quick
python3 scripts/run_etl.py --phase load --mode quick
python3 scripts/generate_dashboard_data.py
python3 -m pytest -q
```

Contoh narasi:

> Reproduksibilitas pipeline dijaga dengan menyediakan skrip eksekusi bertahap. Proses dimulai dari verifikasi API, ekstraksi snapshot, transformasi data, pemuatan ke SQLite, hingga pembangkitan file dashboard. Setiap tahap menghasilkan artifact yang dapat diperiksa ulang, seperti manifest ekstraksi, metrik kualitas transformasi, metrik load, dan file JSON dashboard.

---

## 4. Masalah Format yang Wajib Diperbaiki

### 4.1 Abstract dan Keywords Masih Template

Ini fatal jika belum diganti.

Saat ini masih ada teks:

> This electronic document is a “live” template...

Dan keywords:

> component, formatting, style, styling, insert

Ini harus diganti sebelum final.

#### Contoh abstract

> Abstract—Penelitian ini merancang ETL pipeline dan dashboard analitik untuk memantau data sosial ekonomi Indonesia berbasis Web API Badan Pusat Statistik (BPS). Data yang digunakan mencakup enam indikator, yaitu kemiskinan, tingkat pengangguran terbuka, rata-rata lama sekolah, indeks pembangunan manusia, gini ratio, dan pertumbuhan PDRB pada periode 2021–2024. Proses ETL dilakukan melalui tahap ekstraksi metadata dan data dinamis dari Web API BPS, transformasi `datacontent` menjadi tabel analitik, validasi kualitas data, serta pemuatan ke basis data SQLite dengan pendekatan star schema. Hasil pipeline menghasilkan 4.292 baris data fakta dari 54 snapshot JSON dengan quality gate berstatus passed. Data yang telah dimuat kemudian disajikan melalui dashboard statis berbasis HTML, CSS, dan JavaScript. Dashboard menampilkan ringkasan indikator, tren, peringkat wilayah, tabel detail, dan narasi analitik untuk mendukung pemantauan indikator pembangunan berbasis data.

#### Contoh keywords

> Keywords—ETL pipeline, Web API BPS, data sosial ekonomi, SQLite, dashboard analitik

---

### 4.2 Nomor Tabel Kacau

Di kajian literatur sudah ada:

```text
TABEL I. PENELITIAN TERDAHULU
```

Namun di metodologi, tabel endpoint API juga dirujuk sebagai Tabel I, dan tabel indikator sebagai Tabel II. Ini membuat nomor tabel dobel.

#### Solusi

Gunakan urutan:

| Nomor | Judul Tabel |
|---|---|
| Tabel I | Penelitian Terdahulu |
| Tabel II | Model Endpoint Web API BPS |
| Tabel III | Indikator Sosial Ekonomi yang Digunakan |
| Tabel IV | Hasil Validasi Pipeline |

---

### 4.3 Gambar Tidak Punya Caption yang Jelas

Di metodologi tertulis:

> Gambar arsitektur di atas

Padahal secara visual gambar ada di bawah. Selain itu, caption gambar tidak terlihat jelas.

#### Contoh perbaikan

Ubah kalimat menjadi:

> Arsitektur sistem ditunjukkan pada Gambar 1.

Caption:

> **Gambar 1. Arsitektur sistem ETL dan dashboard analitik berbasis Web API BPS.**

Untuk diagram tahapan penelitian:

> **Gambar 2. Tahapan penelitian dan pengembangan pipeline ETL.**

---

### 4.4 Highlight Kuning Harus Dihapus

Di PDF masih terlihat highlight kuning pada beberapa bagian:

- `B. Arsitektur Sistem`
- `Gambar arsitektur di atas`
- `dashboard-data.json yang di-export dari SQLite`
- `Tabel I`
- `kode 5xx`
- `Tabel II`
- `III. Metode Penelitian`

Ini membuat laporan terlihat belum final. Hapus semua highlight sebelum dikumpulkan.

---

### 4.5 Tabel Indikator Sulit Dibaca

Kolom `indicator_key` terlalu panjang dan pecah tidak rapi, misalnya:

```text
open_unemploy
ment_rate
```

Untuk laporan final, kolom ini sebaiknya dihilangkan atau diganti dengan nama pendek.

#### Contoh tabel indikator yang lebih rapi

| No | Indikator | Var ID | Tahun | Records |
|---:|---|---:|---|---:|
| 1 | Persentase Penduduk Miskin | 192 | 2021–2024 | 752 |
| 2 | Tingkat Pengangguran Terbuka | 543 | 2021–2024 | 288 |
| 3 | Rata-rata Lama Sekolah | 415 | 2021–2024 | 2.200 |
| 4 | Indeks Pembangunan Manusia | 494 | 2021–2024 | 152 |
| 5 | Gini Ratio | 98 | 2021–2024 | 752 |
| 6 | Pertumbuhan PDRB ADHK 2010 | 291 | 2021–2024 | 148 |
|  | **Total** |  |  | **4.292** |

---

## 5. Contoh Revisi Subbagian Metodologi yang Lebih Pas

Berikut contoh versi yang lebih kuat untuk beberapa bagian metodologi.

### 5.1 Contoh Revisi Arsitektur Sistem

> Arsitektur sistem yang dikembangkan dalam penelitian ini dirancang menggunakan pendekatan berlapis yang terdiri atas lima lapisan utama, yaitu lapisan sumber data, lapisan ETL pipeline, lapisan basis data analitik, lapisan jembatan data, dan lapisan presentasi. Lapisan sumber data berupa Web API BPS yang menyediakan data statistik dalam format JSON. Lapisan ETL pipeline diimplementasikan menggunakan Python untuk menjalankan proses extract, transform, dan load. Lapisan basis data analitik menggunakan SQLite dengan pendekatan star schema. Lapisan jembatan data berupa file `dashboard-data.json` yang dibangkitkan dari SQLite agar dashboard dapat berjalan secara statis. Lapisan presentasi berupa dashboard berbasis HTML, CSS, dan JavaScript yang memuat data dari file JSON dan menyajikannya dalam bentuk visualisasi, tabel, dan narasi analitik.

---

### 5.2 Contoh Revisi Pengumpulan Data

> Data penelitian diperoleh dari Web API BPS melalui endpoint `https://webapi.bps.go.id/v1/api/list`. Pengambilan data dilakukan pada domain BPS pusat (`0000`) untuk enam indikator sosial ekonomi periode 2021–2024. Proses pengambilan data tidak hanya menggunakan model `data`, tetapi juga beberapa model metadata, yaitu `th`, `vervar`, `turvar`, `turth`, dan `unit`. Model `th` digunakan untuk memperoleh `th_id` karena parameter `th` pada `model=data` merupakan ID internal BPS, bukan tahun kalender. Metadata lain digunakan untuk memetakan wilayah, klasifikasi turunan, periode turunan, dan satuan indikator.
>
> Total snapshot yang dihasilkan berjumlah 54 berkas JSON, terdiri dari 30 snapshot metadata dan 24 snapshot data dinamis. Snapshot metadata diperoleh dari 6 indikator × 5 model metadata, sedangkan snapshot data dinamis diperoleh dari 6 indikator × 4 tahun. Seluruh snapshot disimpan sebagai artifact mentah dengan checksum SHA-256 agar sumber data dapat ditelusuri kembali.

---

### 5.3 Contoh Revisi Transform

> Proses transform dilakukan dengan membaca snapshot JSON hasil ekstraksi, kemudian mendekode objek `datacontent` menggunakan aturan composite key BPS, yaitu `vervar.val + var.val + turvar.val + tahun.val + turtahun.val`. Setiap key dipetakan kembali ke metadata wilayah, indikator, waktu, klasifikasi turunan, dan periode turunan. Nilai statistik kemudian dinormalisasi menjadi format numerik agar dapat dimuat ke tabel fakta. Setelah proses decoding selesai, sistem menjalankan quality gate yang memeriksa kesesuaian jumlah data mentah dan data hasil decoding, unmatched key, nilai null, serta duplikasi fact grain.

---

### 5.4 Contoh Revisi Load

> Proses load memuat data hasil transformasi ke dalam SQLite menggunakan pendekatan star schema. Struktur basis data terdiri dari tabel fakta `fact_statistik` dan lima tabel dimensi, yaitu `dim_indikator`, `dim_wilayah`, `dim_waktu`, `dim_turvar`, dan `dim_turtahun`. Selain itu, sistem juga menyimpan metadata audit melalui tabel `raw_api_snapshot` dan `etl_run_log`. Pemuatan data menggunakan mekanisme upsert berbasis `ON CONFLICT DO UPDATE` agar pipeline dapat dijalankan ulang tanpa menghasilkan duplikasi pada fact grain yang sama.

---

### 5.5 Contoh Revisi Validasi dan Evaluasi

> Validasi dilakukan pada beberapa tahap. Pada tahap transform, quality gate memeriksa lima kriteria utama, yaitu jumlah data hasil decoding harus sama dengan jumlah raw `datacontent`, tidak ada unmatched key, tidak ada nilai null, tidak ada duplikasi fact grain, dan jumlah raw data harus lebih dari nol. Pada tahap load, sistem memverifikasi kesesuaian jumlah baris antara hasil transformasi dan tabel SQLite. Pada tahap dashboard, sistem memastikan `dashboard-data.json` valid, jumlah `table_rows` sesuai dengan jumlah fact row, chart series tersedia, dan flag `no_dummy_data` bernilai benar. Berdasarkan hasil eksekusi, pipeline menghasilkan 4.292 baris data fakta dari 54 snapshot JSON, dengan quality gate berstatus passed.

---

## 6. Checklist Revisi Final

Sebelum laporan dikumpulkan, minimal lakukan ini:

- [ ] Ganti abstract template.
- [ ] Ganti keywords template.
- [ ] Tambahkan subbagian Web API BPS dan Data Statistik Dinamis.
- [ ] Kurangi kalimat textbook pada ETL, database, dan dashboard.
- [ ] Tambahkan konteks `datacontent`, `th_id`, dan metadata BPS.
- [ ] Ganti “empat lapisan” menjadi “lima lapisan”.
- [ ] Ganti `fact_statistic` menjadi `fact_statistik`.
- [ ] Tambahkan endpoint `unit`.
- [ ] Perbaiki penjelasan 54 snapshot.
- [ ] Ganti “penanganan nilai hilang” menjadi “validasi nilai null”.
- [ ] Ganti klaim “akurasi” menjadi “kelengkapan, konsistensi, dan keterlacakan”.
- [ ] Ganti `INSERT OR REPLACE` menjadi `ON CONFLICT DO UPDATE`.
- [ ] Perjelas makna domain `0000`.
- [ ] Tambahkan validasi dashboard.
- [ ] Tambahkan command reproducibility.
- [ ] Rapikan nomor tabel.
- [ ] Tambahkan caption gambar dan tabel.
- [ ] Hapus highlight kuning.
- [ ] Buat tabel indikator lebih mudah dibaca.
- [ ] Hindari menyebut peta koropleth jika dashboard tidak memilikinya.

---

## 7. Prioritas Jika Waktu Mepet

Jika waktu revisi terbatas, urutan prioritasnya:

1. **Abstract dan keywords** — ini paling fatal karena masih template.
2. **Inkonsistensi teknis** — endpoint `unit`, 5 layer, `fact_statistik`, 54 snapshot.
3. **Nomor tabel dan caption** — supaya laporan terlihat final.
4. **Tambahkan contoh validasi/reproducibility** — supaya metodologi terlihat ilmiah dan dapat dijalankan ulang.
5. **Rapikan kajian literatur yang terlalu textbook** — supaya laporan tidak terasa generik.
6. **Bersihkan highlight dan layout tabel** — supaya siap dikumpulkan.

---

## 8. Kesimpulan Review

Kajian literatur dan metodologi **sudah berada di jalur yang benar**, tetapi belum cukup tajam dan belum sepenuhnya konsisten dengan implementasi proyek. Kajian literatur perlu dibuat lebih spesifik terhadap Web API BPS dan karakteristik `datacontent`. Metodologi perlu dibersihkan dari kesalahan teknis seperti jumlah lapisan arsitektur, endpoint yang belum lengkap, nama tabel yang salah, serta penjelasan snapshot yang ambigu.

Jika revisi pada checklist di atas dilakukan, bagian Kajian Literatur dan Metodologi bisa naik dari sekitar **78–82/100** menjadi **90+/100** karena proyek sebenarnya sudah memiliki artifact kuat: 54 snapshot JSON, 4.292 fact rows, SQLite star schema, quality gate passed, dashboard real-data-only, dan test suite yang berjalan.
