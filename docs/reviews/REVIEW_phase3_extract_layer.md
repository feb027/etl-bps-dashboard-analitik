# Review Fase 3 - Extract Layer

## Verdict and Score

**APPROVED** dengan skor **91/100**.

Fase 3 layak dilanjutkan. Implementasi extract layer sudah memenuhi batas fase: client BPS dengan timeout/retry, target planner berbasis artifact Fase 1, snapshot raw yang disanitasi, manifest dengan checksum/fingerprint/row count, test mocked/fake response, dan dashboard tetap tidak menampilkan grafik statistik palsu. Tidak ada critical issue yang memblokir Fase 4.

## Evidence Reviewed

| Area | Evidence |
|---|---|
| BPS client | `src/bps_etl/extract/client.py` |
| Metadata target planning | `src/bps_etl/extract/metadata.py`, `results/api/selected_indicators.json` |
| Raw snapshot writer | `src/bps_etl/extract/snapshot.py` |
| Extract orchestration | `src/bps_etl/extract/pipeline.py` |
| CLI runner | `scripts/run_etl.py` |
| Tests | `tests/test_extract_layer.py`, related scaffold/dynamic/schema tests |
| Documentation | `docs/phases/extract-layer.md`, `reports/progress-3-extract-layer.md` |
| Manifest/artifacts | `results/api/extract/extract_manifest.json`, `results/api/extract/metadata/*.json`, `results/api/extract/data/*.json` |
| Dashboard truthfulness | `dashboard/data/dashboard-data.json`, `dashboard/index.html`, `dashboard/app.js`, `dashboard/styles.css` |
| Phase control | `docs/project/phase-gates.md`, `docs/project/project-control.md` |

## Validation Results

| Command/check | Result |
|---|---|
| `python3 -m py_compile scripts/*.py` | PASS |
| `python3 -m pytest -q` | PASS, 27 passed |
| `python3 -m json.tool dashboard/data/dashboard-data.json >/dev/null` | PASS |
| `python3 -m json.tool results/api/bps_api_probe_summary.json >/dev/null` | PASS |
| `python3 -m json.tool results/api/metadata_endpoint_evidence.json >/dev/null` | PASS |
| `python3 -m json.tool results/api/extract/extract_manifest.json >/dev/null` | PASS |
| `python3 scripts/run_etl.py --help` | PASS, CLI exposes extract-only phase, quick/full mode flag, selected indicators path, output dir, timeout, and retries |
| Manifest checksum spot/full verification | PASS, 32 manifest snapshots exist, SHA-256 values match files, request fingerprints match artifact payload metadata |
| Extract artifact size check | PASS, `results/api/extract/` is about 496K, reasonable for commit-safe evidence |
| Secret-pattern scan on extract artifacts | PASS, no `BPS_API_KEY=`, `key=`, `api_key=`, `token=`, or `secret=` pattern found in `results/api/extract/*.json` artifacts |

## Critical Issues

None.

## Important Improvements

1. **Retry policy should avoid retrying permanent HTTP client errors.**
   `BPSClient.request()` currently catches `HTTPError` together with transient errors and retries every HTTP status. This is acceptable for Fase 3 proof, but before larger runs it should retry only transient server/rate-limit cases such as 429/5xx and fail fast for 400/401/403/404. This prevents repeated invalid-key or invalid-parameter calls and makes failures easier to diagnose.

2. **Dashboard empty-state copy is slightly stale.**
   `dashboard/data/dashboard-data.json` and Fase 3 metrics are updated honestly, but `dashboard/index.html` still says Fase 2 just finished and that graphs appear after Fase 3-5. Since Fase 3 extract is now implemented, revise that copy to say raw extract evidence exists and statistical charts remain blocked until transform/load finish.

3. **Test placeholders still use secret-like strings in Fase 3 tests.**
   `tests/test_extract_layer.py` uses values such as `"secret"` and `"local-secret"` only as dummy input to prove sanitation. That is not a committed real credential, and the artifact sanitation works, but replacing these with explicit placeholders such as `"test-api-key-placeholder"` would reduce false positives in future secret scans and align better with the project's no-secrets rule.

4. **Add one negative test for missing `period_ids`.**
   The target planner correctly raises `ValueError` when a selected indicator lacks a `th_id` for a target year, but the current tests only cover the successful path. A small negative test would lock the most important Fase 1-to-Fase 3 contract: `model=data` must use persisted `th_id`, not literal years.

## Nice-to-Have

1. Add a test that verifies `BPSClient` stops after retry exhaustion and reports the attempt count clearly.
2. Include subdirectory context in manifest `artifact_path`, or add an explicit `artifact_group` field, so readers do not need to infer `metadata/` vs `data/` from `model`.
3. Add a documented non-network dry-run or planning command for `scripts/run_etl.py` so target generation can be reproduced without a live BPS API key.
4. After review fixes, update `docs/project/project-control.md` and `dashboard/data/dashboard-data.json` review metadata to point to this Fase 3 review.

## Final Decision

**APPROVED**.

Fase 3 satisfies the extract-layer review gate. It does not pretend transform/load/dashboard statistics are complete, it preserves evidence-first raw artifacts, and it keeps dashboard charts empty until later phases produce loaded analytical data.

## Post-Review Fixes Applied

Cheap fixes applied after review:

1. `BPSClient` now fails fast for permanent HTTP 4xx errors and retries only 429/5xx plus transient URL/timeout failures.
2. Dashboard empty-state copy now states that Fase 3 raw extract evidence exists and charts wait for transform/load.
3. Test placeholders were renamed to explicit dummy API-key placeholders.
4. Added missing-`period_ids` negative test for the Fase 1 → Fase 3 `th_id` contract.
5. Manifest snapshots now include `artifact_group` (`metadata` or `data`).
