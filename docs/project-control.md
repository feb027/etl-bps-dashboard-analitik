# Project Control

## Current Status

- Current phase: **2 — ETL Architecture & Schema**
- Date initialized: 2026-04-29
- Repository: `feb027/etl-bps-dashboard-analitik`
- Dashboard URL target: `https://feb027.github.io/etl-bps-dashboard-analitik/`
- Latest verified commit: `22442189ff4e270befca8fcbdae3d7fb77ab9890`

## Decisions

| Decision | Status | Notes |
|---|---|---|
| Rebuild from scratch | Approved | Repo lama dipakai sebagai audit/anti-pattern |
| Static dashboard | Approved | GitHub Pages-friendly, real-data-only |
| SQLite database | Approved | Cukup untuk skala tugas Rekayasa Data |
| Phase-gated workflow | Approved | Sama pola UAS IoT |
| BPS API proof before ETL | Approved | Fase 1 wajib membuktikan endpoint/data |

## Artifact Inventory

| Path | Purpose | Status |
|---|---|---|
| `AGENTS.md` | Operating rules | Created |
| `docs/phase-gates.md` | Done criteria | Created |
| `docs/roadmap.md` | Phase roadmap | Created |
| `docs/api-research-plan.md` | Fase 1 plan | Created |
| `dashboard/data/dashboard-data.json` | Dashboard data scaffold | Created |
| `tests/test_scaffold.py` | Scaffold smoke test | Created |
| `results/api/bps_api_probe_summary.json` | Fase 1 API probe summary | Created |
| `results/api/metadata_endpoint_evidence.json` | Explicit metadata endpoint evidence | Created |
| `results/api/selected_indicators.json` | Valid selected BPS indicators | Created |
| `results/tables/bps_api_probe_results.csv` | Probe table per indicator/year | Created |
| `results/tables/normalized_sample.csv` | Decoded tabular sample | Created |
| `reports/progress-1-api-research.md` | Fase 1 progress report | Created |
| `docs/etl-architecture.md` | Fase 2 ETL architecture design | Created |
| `docs/database-schema.md` | Fase 2 SQLite schema explanation | Created |
| `docs/transform-rules.md` | Fase 2 transform rules | Created |
| `src/bps_etl/load/schema.sql` | SQLite DDL design | Created |
| `tests/test_schema.py` | Executable schema validation | Created |

## Review Status

| Phase | Reviewer | Score | Verdict | File |
|---|---|---:|---|---|
| 0A/0B | Codex lecturer/technical reviewer | 88 | APPROVED | `docs/REVIEW_phase0b.md` |
| 1 | Codex lecturer/technical reviewer | 90 | APPROVED | `docs/REVIEW_phase1_api_research.md` |
| 2 | Codex lecturer/technical reviewer | 88 | APPROVED | `docs/REVIEW_phase2_etl_design.md` |

## Remote & Pages Verification

| Check | Result |
|---|---|
| GitHub repo | `https://github.com/feb027/etl-bps-dashboard-analitik` |
| Remote main commit | `0dfa08bb1124dcdfaa422981dce6db81c20fe13b` |
| GitHub Pages URL | `https://feb027.github.io/etl-bps-dashboard-analitik/` |
| Page HTTP | 200 verified |
| Dashboard JSON HTTP | 200 verified |
| Dashboard JSON status | `Fase 0B scaffold; data statistik belum tersedia` |

## Blockers

- BPS API key must be provided locally in `.env` for Fase 1.
- Valid indicator IDs must be discovered from API, not guessed.

## Fase 1 Snapshot

| Metric | Value |
|---|---:|
| Valid indicators | 4 |
| Probe rows | 12 |
| Normalized sample records | 2490 |
| Unmatched datacontent keys | 0 |

Key finding: `model=data` requires `th_id` from `model=th`; BPS `datacontent` keys decode as `vervar.val + var.val + turvar.val + tahun.val + turtahun.val`.

## Fase 2 Snapshot

| Metric | Value |
|---|---:|
| Dimension tables | 5 |
| Fact tables | 1 |
| Audit tables | 2 |
| Schema validation tests | 10 |

Schema grain: `var_id + kode_wilayah + th_id + turvar_id + turth_id + source_domain`.

## Next Action

1. Push branch `phase-2-etl-architecture-schema`.
2. Open PR to `main`.
3. Start Fase 3 — Extract Layer after PR is reviewed/merged.
