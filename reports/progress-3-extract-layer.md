# Progress 3 — Extract Layer

## Status

Fase 3 mengimplementasikan extract layer production untuk mengambil metadata dan raw dynamic data BPS secara terstruktur. Output Fase 3 masih raw/sanitized API evidence; transform normalized fact rows dilakukan pada Fase 4.

## Input

- Selected indicators: `results/api/selected_indicators.json`
- BPS API key: local `.env` / environment, tidak dikomit
- Source design: `docs/etl-architecture.md`, `docs/transform-rules.md`, `docs/database-schema.md`

## Implementasi

| Artifact | Fungsi |
|---|---|
| `src/bps_etl/extract/client.py` | BPS API client dengan timeout + retry. |
| `src/bps_etl/extract/metadata.py` | Extract target planner dari selected indicators. |
| `src/bps_etl/extract/snapshot.py` | Commit-safe raw snapshot writer + SHA-256 manifest metadata. |
| `src/bps_etl/extract/pipeline.py` | Metadata/dynamic data extraction pipeline. |
| `scripts/run_etl.py` | CLI Fase 3: `--phase extract --mode quick`. |
| `tests/test_extract_layer.py` | Unit tests dengan mocked/fake responses. |
| `results/api/extract/` | Raw extract snapshots dan manifest. |
| `docs/extract-layer.md` | Dokumentasi teknis extract layer. |

## Run Evidence

Command:

```bash
python3 scripts/run_etl.py --phase extract --mode quick --timeout 30 --retries 2
```

Result:

| Metric | Value |
|---|---:|
| Status | success |
| Target dynamic data | 12 |
| Metadata snapshots | 20 |
| Dynamic snapshots | 12 |
| Total snapshots | 32 |
| Total raw rows/keys | 3642 |
| Captured at | `2026-04-29T16:35:03Z` |

## Security Evidence

- `results/api/extract/extract_manifest.json` tidak menyimpan API key.
- Snapshot `request.params` disanitasi: `key`, `api_key`, `token`, `password`, `secret` dihapus.
- `request_fingerprint` stabil walaupun input berisi key berbeda.

## Validation Commands

```bash
python3 -m py_compile scripts/*.py
python3 -m pytest -q
python3 -m json.tool dashboard/data/dashboard-data.json >/dev/null
python3 -m json.tool results/api/bps_api_probe_summary.json >/dev/null
python3 -m json.tool results/api/metadata_endpoint_evidence.json >/dev/null
python3 -m json.tool results/api/extract/extract_manifest.json >/dev/null
```

## Batas Fase 3

Belum melakukan:

1. decode raw `datacontent` menjadi normalized fact rows production,
2. load ke SQLite,
3. generate grafik statistik final.

Tahap berikutnya: Fase 4 — Transform Layer.

## Review Result

Codex lecturer/technical review: **91/100 — APPROVED**.

Post-review fixes applied:

1. HTTP retry now avoids permanent 4xx client errors and only retries 429/5xx plus transient URL/timeouts.
2. Dashboard empty-state copy updated for Fase 3.
3. Test placeholder secrets replaced with explicit dummy placeholders.
4. Added negative test for missing `period_ids`.
5. Manifest snapshots now include `artifact_group` (`metadata` or `data`).
