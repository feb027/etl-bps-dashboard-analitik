# Project Control

## Current Status

- Current phase: **4 — Transform Layer**
- Date initialized: 2026-04-29
- Repository: `feb027/etl-bps-dashboard-analitik`
- Dashboard URL target: `https://feb027.github.io/etl-bps-dashboard-analitik/`
- Latest verified commit: `fe55aafdbb47cae6d72c821b49cf96579e3e831f`

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
| `docs/extract-layer.md` | Fase 3 extract layer technical documentation | Created |
| `src/bps_etl/extract/pipeline.py` | Fase 3 extract orchestration | Created |
| `src/bps_etl/extract/snapshot.py` | Commit-safe raw snapshot writer | Created |
| `results/api/extract/extract_manifest.json` | Fase 3 extract run manifest | Created |
| `reports/progress-3-extract-layer.md` | Fase 3 progress report | Created |
| `docs/transform-layer.md` | Fase 4 transform technical documentation | Created |
| `src/bps_etl/transform/pipeline.py` | Fase 4 transform orchestration | Created |
| `results/tables/transform/transform_manifest.json` | Fase 4 transform run manifest | Created |
| `results/tables/transform/fact_statistik_preview.csv` | Fase 4 normalized fact preview | Created |
| `reports/progress-4-transform-layer.md` | Fase 4 progress report | Created |

## Review Status

| Phase | Reviewer | Score | Verdict | File |
|---|---|---:|---|---|
| 0A/0B | Codex lecturer/technical reviewer | 88 | APPROVED | `docs/REVIEW_phase0b.md` |
| 1 | Codex lecturer/technical reviewer | 90 | APPROVED | `docs/REVIEW_phase1_api_research.md` |
| 2 | Codex lecturer/technical reviewer | 88 | APPROVED | `docs/REVIEW_phase2_etl_design.md` |
| 3 | Codex lecturer/technical reviewer | 91 | APPROVED | `docs/REVIEW_phase3_extract_layer.md` |
| 4 | Codex lecturer/technical reviewer | 93 | APPROVED | `docs/REVIEW_phase4_transform_layer.md` |

## Remote & Pages Verification

| Check | Result |
|---|---|
| GitHub repo | `https://github.com/feb027/etl-bps-dashboard-analitik` |
| Remote main commit | `e7534586daa015f2522fd00aeec66fdb6a11cc6c` |
| GitHub Pages URL | `https://feb027.github.io/etl-bps-dashboard-analitik/` |
| Page HTTP | 200 verified |
| Dashboard JSON HTTP | 200 verified |
| Dashboard JSON status | `Fase 3 complete` on live main; Fase 4 dashboard update pending PR merge |

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

## Fase 3 Snapshot

| Metric | Value |
|---|---:|
| Extract targets | 12 |
| Metadata snapshots | 20 |
| Dynamic snapshots | 12 |
| Total snapshots | 32 |
| Total raw rows/keys | 3642 |
| Extract tests | 8 |

Extract manifest: `results/api/extract/extract_manifest.json`.

## Fase 4 Snapshot

| Metric | Value |
|---|---:|
| Dynamic snapshots transformed | 12 |
| Fact preview rows | 2490 |
| Dimension indikator rows | 4 |
| Dimension wilayah rows | 553 |
| Dimension waktu rows | 3 |
| Unmatched keys | 0 |
| Duplicate fact grains | 0 |
| Null/non-numeric values | 0 |
| Quality gate | `passed` |
| Transform tests | 5 |

Transform manifest: `results/tables/transform/transform_manifest.json`.

## Next Action

1. Push branch `phase-4-transform-layer`.
2. Open PR to `main`.
3. Start Fase 5 — Load Layer after PR is reviewed/merged.
