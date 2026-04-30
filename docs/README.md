# Dokumentasi Proyek

Dokumentasi repo ini dipisah berdasarkan fungsi agar lebih mudah dibaca dan dirawat.

## Navigasi Cepat

| Kategori | Isi | File Utama |
|---|---|---|
| `project/` | kontrol proyek, roadmap, workflow, phase gate, outline laporan | [`project/project-control.md`](project/project-control.md) |
| `architecture/` | arsitektur ETL, schema database, data dictionary, transform rules | [`architecture/etl-architecture.md`](architecture/etl-architecture.md) |
| `phases/` | dokumentasi teknis per fase implementasi | [`phases/extract-layer.md`](phases/extract-layer.md) |
| `reviews/` | review gate per fase | [`reviews/REVIEW_phase6_1_data_expansion.md`](reviews/REVIEW_phase6_1_data_expansion.md) |
| `assets/` | gambar/asset dokumentasi | [`assets/readme-hero.png`](assets/readme-hero.png) |

## Project Control

- [`project/project-brief.md`](project/project-brief.md) — ringkasan proyek dan scope akademik.
- [`project/project-control.md`](project/project-control.md) — status, artifact inventory, review status, dan next action.
- [`project/roadmap.md`](project/roadmap.md) — roadmap fase.
- [`project/workflow.md`](project/workflow.md) — workflow phase-gated.
- [`project/phase-gates.md`](project/phase-gates.md) — checklist selesai per fase.
- [`project/report-outline.md`](project/report-outline.md) — outline laporan final.
- [`project/reference-plan.md`](project/reference-plan.md) — rencana referensi.

## Architecture

- [`architecture/etl-architecture.md`](architecture/etl-architecture.md) — desain arsitektur ETL end-to-end.
- [`architecture/database-schema.md`](architecture/database-schema.md) — desain schema SQLite/star schema.
- [`architecture/data-dictionary.md`](architecture/data-dictionary.md) — kamus data tabel dan field.
- [`architecture/transform-rules.md`](architecture/transform-rules.md) — aturan decoding dan quality gate.

## Phase Docs

- [`phases/api-research-plan.md`](phases/api-research-plan.md) — rencana riset API BPS.
- [`phases/extract-layer.md`](phases/extract-layer.md) — dokumentasi extract layer.
- [`phases/transform-layer.md`](phases/transform-layer.md) — dokumentasi transform layer.
- [`phases/load-layer.md`](phases/load-layer.md) — dokumentasi load layer.
- [`phases/dashboard-spec.md`](phases/dashboard-spec.md) — spesifikasi dashboard.
- [`phases/dashboard-design-system.md`](phases/dashboard-design-system.md) — desain visual dashboard.

## Review Gates

- [`reviews/REVIEW_phase0b.md`](reviews/REVIEW_phase0b.md)
- [`reviews/REVIEW_phase1_api_research.md`](reviews/REVIEW_phase1_api_research.md)
- [`reviews/REVIEW_phase2_etl_design.md`](reviews/REVIEW_phase2_etl_design.md)
- [`reviews/REVIEW_phase3_extract_layer.md`](reviews/REVIEW_phase3_extract_layer.md)
- [`reviews/REVIEW_phase4_transform_layer.md`](reviews/REVIEW_phase4_transform_layer.md)
- [`reviews/REVIEW_phase5_load_layer.md`](reviews/REVIEW_phase5_load_layer.md)
- [`reviews/REVIEW_phase6_dashboard.md`](reviews/REVIEW_phase6_dashboard.md)
- [`reviews/REVIEW_phase6_1_data_expansion.md`](reviews/REVIEW_phase6_1_data_expansion.md)

## Reports

Progress dan laporan akhir tetap berada di folder [`../reports/`](../reports/) karena merupakan deliverable naratif, bukan dokumentasi teknis internal.
