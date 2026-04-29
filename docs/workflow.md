# Workflow

## Phase Pattern

```text
plan → execute → artifact → docs → review → fix → commit → next phase
```

## Branch Pattern

- `main`: stable, reviewed artifacts
- `phase-1-bps-api-research`
- `phase-2-etl-design`
- `phase-3-extract-layer`
- `phase-4-transform-layer`
- `phase-5-load-pipeline`
- `phase-6-dashboard`
- `phase-7-report`

## Commit Pattern

```text
docs: initialize project operating system
chore: scaffold repository infrastructure
feat: verify bps api metadata access
feat: implement bps extract client
feat: add transform validation
feat: implement sqlite load layer
feat: generate dashboard data
```

## Validation Commands

```bash
python3 -m py_compile scripts/*.py
python3 -m pytest -q
python3 -m json.tool dashboard/data/dashboard-data.json >/dev/null
```

## Review Loop

1. Write review prompt output to `docs/REVIEW_phaseX.md`.
2. Fix critical and important issues.
3. Run validation commands again.
4. If needed, write final verification review to `docs/REVIEW_phaseX_final.md`.
5. Update `docs/project-control.md`.
