# Phase Gates

## Global Done Rule

A phase is not complete until:
1. expected artifacts exist,
2. tests/validations pass,
3. docs match artifacts,
4. no dummy/fake data is presented as real,
5. review gate is approved or explicitly deferred by user.

## Fase 0A Done Criteria

- [x] `AGENTS.md` exists
- [x] project-control exists
- [x] workflow doc exists
- [x] phase gates exist
- [x] reviewer prompts exist
- [x] user approved operating model

## Fase 0B Done Criteria

- [x] GitHub repo created and pushed
- [x] README exists
- [x] `.gitignore` protects secrets/data/db
- [x] `.env.example` exists
- [x] package scaffold exists
- [x] static dashboard shell exists
- [x] smoke test exists
- [x] `python3 -m py_compile scripts/*.py` passes
- [x] `python3 -m pytest -q` passes
- [x] `dashboard/data/dashboard-data.json` is valid JSON
- [x] GitHub Pages enabled and HTTP 200 verified
- [x] Fase 0B review file exists

## Fase 1 Done Criteria — BPS API Research

- [x] API key loaded only from `.env`
- [x] BPS docs/source logged in references
- [x] `model=var` verified
- [x] `model=th` verified and `th_id` usage documented
- [x] `model=vervar`, `turvar`, `turth` checked for target indicators
- [x] `model=data` produces real `datacontent`
- [x] at least 3 valid indicators selected
- [x] normalized sample table exists
- [x] progress report exists
- [x] lecturer/technical review approves

## Fase 2 Done Criteria — ETL Design

- [x] data dictionary exists
- [x] database schema exists
- [x] ETL architecture diagram/doc exists
- [x] transform rules documented
- [x] primary/unique keys defined
- [x] review approves

## Fase 3 Done Criteria — Extract Layer

- [x] BPS client implemented
- [x] retry and timeout implemented
- [x] raw evidence saving implemented
- [x] no hardcoded key
- [x] unit tests with mocked response pass
- [x] review approves

## Fase 4 Done Criteria — Transform Layer

- [ ] `datacontent` decoder implemented
- [ ] normalized fact preview exists
- [ ] data quality metrics exist
- [ ] duplicate/missing checks implemented
- [ ] tests pass
- [ ] review approves

## Fase 5 Done Criteria — Load Layer

- [ ] SQLite schema implemented
- [ ] quick ETL run fills dimensions and facts
- [ ] rerun is idempotent
- [ ] ETL run log works
- [ ] tests pass
- [ ] review approves

## Fase 6 Done Criteria — Dashboard

- [ ] dashboard JSON generated from real database/artifacts
- [ ] no fake chart/table
- [ ] static dashboard renders locally
- [ ] GitHub Pages works
- [ ] screenshots saved
- [ ] review approves

## Fase 7 Done Criteria — Report

- [ ] final report complete
- [ ] all claims backed by artifacts
- [ ] references valid
- [ ] figures/tables linked
- [ ] lecturer review approves

## Fase 8 Done Criteria — Final Audit

- [ ] repo clean
- [ ] no secrets/data/db tracked
- [ ] tests pass
- [ ] dashboard link works
- [ ] final review approves
- [ ] release/tag optional
