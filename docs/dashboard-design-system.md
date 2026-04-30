# Dashboard Design System — Fase 6

## Direction

Fase 6 menggunakan arah **Editorial Data Atlas**: halaman analitik yang terasa seperti laporan data interaktif, bukan admin panel berbentuk kumpulan kartu. Fokus desainnya adalah narasi, ruang putih, tipografi, satu chart utama besar, ranking wilayah, tabel fakta, dan footer evidence.

## UI Skills yang Dipakai

| Skill | Peran |
|---|---|
| `frontend-design` | Menentukan arah visual yang distinctive dan menghindari generic dashboard. |
| `impeccable` | Gate anti-slop: no card-grid reflex, product UI harus melayani analisis. |
| `interface-design` | Struktur dashboard, kontrol filter, chart, ranking, dan tabel detail. |
| `emil-design-eng` | Motion pendek, feedback kontrol, dan polish interaksi. |
| `make-interfaces-feel-better` | Text wrapping, tabular numerals, focus/hit area, radius, dan surface detail. |
| `oklch-skill` | Token warna OKLCH yang tetap accessible dan tidak generik. |
| `fixing-accessibility` + `wcag-audit-patterns` | Landmark, label, focus state, keyboard controls, dan fallback chart. |
| `fixing-metadata` | Title, description, canonical, Open Graph, Twitter Card, dan theme color. |
| `fixing-motion-performance` | Animasi hanya transform/opacity/color, durasi <300ms, dan `prefers-reduced-motion`. |

## Design Tokens

Token utama berada di `dashboard/styles/tokens.css`. Sistem warna memakai OKLCH untuk background warm ivory, ink gelap bernuansa biru, dan aksen blue/amber yang digunakan terbatas untuk state data. Angka memakai `font-variant-numeric: tabular-nums` agar nilai dashboard stabil saat berubah.

## Layout

File modular:

```text
dashboard/styles/tokens.css
dashboard/styles/base.css
dashboard/styles/layout.css
dashboard/styles/components.css
dashboard/styles/visualizations.css
dashboard/scripts/*.js
```

Tidak ada build step. GitHub Pages memuat `dashboard/index.html`, ECharts CDN, CSS modular, dan JavaScript module dari `dashboard/scripts/main.js`.

## Accessibility & Performance

- `lang="id"`, skip link, semantic `header/main/footer`, heading hierarchy, table caption, labels untuk filter.
- Chart container memakai `role="img"` plus fallback text/table ketika ECharts gagal.
- Kontrol form tetap native (`select`, `input`, radio) agar keyboard-accessible.
- Motion ringkas, memakai properti transisi eksplisit, dan menghormati `prefers-reduced-motion`.

## Anti-Patterns yang Dihindari

- Tidak memakai bento/card grid sebagai struktur utama.
- Tidak memakai dummy/fake chart.
- Tidak memakai gradient text, glassmorphism dekoratif, atau template hero-metric generik.
- Tidak memakai backend atau React/Vite karena kebutuhan Fase 6 cukup static-first.
