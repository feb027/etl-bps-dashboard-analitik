# ETL BPS Dashboard Analitik

**Judul:** Perancangan ETL Pipeline dan Dashboard Analitik Data Sosial Ekonomi Berbasis Web API Badan Pusat Statistik (BPS)

Repo ini adalah proyek mata kuliah Rekayasa Data untuk membangun pipeline **Extract, Transform, Load (ETL)** dari Web API Badan Pusat Statistik (BPS), menyimpan data sosial-ekonomi ke database SQLite, lalu menyajikan ringkasan analitik melalui dashboard statis berbasis data nyata.

## Status

- Fase saat ini: **5 — Load Layer**
- Data statistik: 2.490 fact rows sudah dimuat ke SQLite lokal dari artifact BPS asli
- Dashboard: evidence ETL sudah diperbarui, grafik statistik menunggu Fase 6, **tanpa dummy/fake chart**
- Prinsip utama: evidence-first, real-data-only, no hardcoded API key

## Arsitektur Target

```text
Web API BPS
   ↓
Extract Layer
   ↓
Raw JSON Evidence
   ↓
Transform Layer
   ↓
Validated Tabular Data
   ↓
SQLite Database
   ↓
Dashboard Data Generator
   ↓
Static Web Dashboard
```

## Struktur Repo

```text
src/bps_etl/       Kode ETL modular
docs/              Dokumentasi proyek dan kontrol fase
prompts/           Prompt reviewer/writer
references/        Daftar referensi dan matriks literatur
scripts/           Entry point operasional ETL/dashboard
tests/             Smoke test dan unit test
dashboard/         Dashboard statis GitHub Pages
results/           Artifact kecil yang boleh di-commit
reports/           Progress report dan final report
```

## Setup Lokal

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# isi BPS_API_KEY di .env
```

## Validasi Proyek

```bash
python3 -m py_compile scripts/*.py
python3 -m pytest -q
python3 -m json.tool dashboard/data/dashboard-data.json >/dev/null
python3 -m json.tool results/database/load_metrics.json >/dev/null
```

## Jalankan Load Layer

```bash
python3 scripts/run_etl.py --phase load --mode quick \
  --database-path data/database/bps_etl.sqlite \
  --metrics-path results/database/load_metrics.json
```

## Jalankan Dashboard Lokal

Dashboard adalah static site. Untuk preview:

```bash
python3 -m http.server 8000
# buka http://localhost:8000/dashboard/
```

## Aturan Data

- `.env`, database, raw data, dan file besar tidak boleh di-commit.
- Dashboard tidak boleh menampilkan data dummy yang terlihat seperti hasil asli.
- Semua angka di README/laporan harus berasal dari artifact di `results/`, database, atau dashboard JSON.

## Roadmap Ringkas

| Fase | Nama | Output |
|---|---|---|
| 0A | Operating System | AGENTS, project-control, phase gates |
| 0B | Repository Infrastructure | Repo scaffold, tests, dashboard shell |
| 1 | BPS API Research | Bukti endpoint BPS dan sample data |
| 2 | ETL Design | Schema, data dictionary, architecture |
| 3 | Extract Layer | Client API + raw evidence |
| 4 | Transform Layer | Normalized tables + validation |
| 5 | Load Layer | SQLite + idempotent runner |
| 6 | Dashboard | Static analytics from real JSON |
| 7 | Report | Laporan akademik final |
| 8 | Final Audit | Release siap submit |
