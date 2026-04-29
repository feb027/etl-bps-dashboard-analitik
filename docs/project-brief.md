# Project Brief

## Judul

Perancangan ETL Pipeline dan Dashboard Analitik Data Sosial Ekonomi Berbasis Web API Badan Pusat Statistik (BPS)

## Latar Belakang Singkat

Data sosial-ekonomi dari BPS sering digunakan untuk membaca kondisi pembangunan, kemiskinan, pendidikan, ketenagakerjaan, dan kesejahteraan wilayah. Agar data tersebut dapat dianalisis secara konsisten, diperlukan pipeline rekayasa data yang mengambil data dari Web API BPS, membersihkan dan menormalisasi respons API, menyimpannya ke database, serta menyajikannya dalam dashboard analitik.

## Tujuan

1. Merancang pipeline ETL berbasis Python untuk Web API BPS.
2. Mengambil dan memvalidasi data sosial-ekonomi dari endpoint BPS.
3. Menyimpan data hasil transformasi ke SQLite dengan schema terstruktur.
4. Menyajikan data melalui dashboard statis berbasis artifact JSON.
5. Menyusun dokumentasi akademik yang evidence-first.

## Batasan Awal

- Sumber data utama: Web API BPS.
- Database: SQLite.
- Dashboard: static HTML/CSS/JS.
- Indikator awal dibatasi 3–5 indikator valid sampai Fase 1 selesai.
- Tidak memakai dummy data untuk hasil analitik.

## Success Criteria

- ETL quick mode berhasil menghasilkan data nyata.
- Database memiliki dimensi dan fact table yang konsisten.
- Dashboard menampilkan ringkasan dari data nyata.
- Laporan akhir memiliki bukti artifact untuk semua klaim.
