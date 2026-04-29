# Project Control

## Current Status

- Current phase: **0B — Repository Infrastructure**
- Date initialized: 2026-04-29
- Repository: `feb027/etl-bps-dashboard-analitik`
- Dashboard URL target: `https://feb027.github.io/etl-bps-dashboard-analitik/`
- Latest verified commit: `0dfa08bb1124dcdfaa422981dce6db81c20fe13b`

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

## Review Status

| Phase | Reviewer | Score | Verdict | File |
|---|---|---:|---|---|
| 0A/0B | Codex lecturer/technical reviewer | 88 | APPROVED | `docs/REVIEW_phase0b.md` |

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

## Next Action

1. Start branch `phase-1-bps-api-research`.
2. Implement `scripts/verify_bps_api.py` to probe BPS `var`, `th`, `vervar`, `turvar`, `turth`, `unit`, and `data`.
3. Save API evidence under `results/api/` and normalized sample tables under `results/tables/`.
