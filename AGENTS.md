# AGENTS.md — Project Operating Rules

## Project Identity

Judul: **Perancangan ETL Pipeline dan Dashboard Analitik Data Sosial Ekonomi Berbasis Web API Badan Pusat Statistik (BPS)**

Mata kuliah: Rekayasa Data
Fokus: ETL pipeline, Web API, database, dashboard analitik, dokumentasi akademik.

## Non-Negotiable Rules

1. **Evidence-first.** Semua angka, grafik, tabel, dan klaim harus berasal dari artifact nyata.
2. **No fake dashboard.** Dashboard boleh empty state, tetapi tidak boleh menampilkan dummy chart/table yang seolah-olah data asli.
3. **No secrets.** API key hanya dari `.env`; jangan hardcode token/API key di source, docs, atau tests.
4. **No raw large data in git.** Raw API/data besar harus di-ignore. Commit hanya ringkasan kecil di `results/` dan `dashboard/data/`.
5. **BPS API correctness first.** Jangan asumsi parameter API. Verifikasi `var`, `th`, `vervar`, `turvar`, `turth`, dan `datacontent` sebelum implementasi ETL besar.
6. **Phase-gated workflow.** Setiap fase: plan → execute → artifact → docs → review → fix → commit.
7. **Academic honesty.** Jika artifact belum ada, tulis belum tersedia. Jangan mengarang hasil.

## Development Commands

```bash
python3 -m py_compile scripts/*.py
python3 -m pytest -q
python3 -m json.tool dashboard/data/dashboard-data.json >/dev/null
```

## Review Gates

- APPROVED jika skor minimal 85 dan tidak ada critical issue.
- Target kuat: skor minimal 90.
- Reviewer harus menulis ke file review di `docs/reviews/` dan tidak mengubah source kecuali diminta.

## Git Rules

- Gunakan branch per fase setelah scaffold awal.
- Commit artifact dan docs bersamaan jika saling bergantung.
- Jangan commit `.env`, `.db`, raw data, cache, virtualenv, log besar.

## Dashboard Rules

- Data dashboard bersumber dari `dashboard/data/dashboard-data.json`.
- JSON dibuat oleh `scripts/generate_dashboard_data.py` dari database/artifact nyata.
- Jika belum ada data, tampilkan empty state yang jujur.
