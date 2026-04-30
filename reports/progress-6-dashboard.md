# Progress Fase 6 — Dashboard

## Status

Fase 6 dashboard **implemented and approved**. Dashboard sekarang memakai data nyata dari SQLite Fase 5 yang digenerate ke `dashboard/data/dashboard-data.json`.

## Scope

- Generate JSON dashboard dari `data/database/bps_etl.sqlite`.
- Modularisasi static dashboard GitHub Pages dengan vanilla HTML/CSS/JS.
- Render chart interaktif menggunakan ECharts CDN.
- Tambah filter indikator/tahun/search wilayah/mode ranking.
- Tambah narasi otomatis dari extrema dan perubahan data nyata.
- Tambah tabel detail dari `fact_statistik`.
- Tambah evidence footer dan metadata sosial.

## Data Evidence

| Metric | Value |
|---|---:|
| Indicators | 4 |
| Regions | 553 |
| Years | 3 |
| Fact rows | 2490 |
| Raw snapshot audit rows | 32 |

## Artifact Baru/Utama

- `dashboard/index.html`
- `dashboard/styles/*.css`
- `dashboard/scripts/*.js`
- `dashboard/data/dashboard-data.json`
- `dashboard/og-dashboard.png`
- `results/figures/dashboard-phase6-full.png`
- `docs/dashboard-design-system.md`
- `tests/test_dashboard_generator.py`

## Validation

```bash
python3 scripts/run_etl.py --phase load --mode quick
python3 scripts/generate_dashboard_data.py
python3 -m py_compile scripts/*.py
python3 -m pytest -q
python3 -m json.tool dashboard/data/dashboard-data.json >/dev/null
git diff --check
```

## Review Gate

Approved: `docs/REVIEW_phase6_dashboard.md`, skor 91/100.
