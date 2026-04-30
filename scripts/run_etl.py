#!/usr/bin/env python3
"""ETL runner entry point for phase-gated BPS ETL runs."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
from typing import Sequence

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bps_etl.config import BPS_BASE_URL
from bps_etl.extract.client import BPSClient
from bps_etl.extract.metadata import TARGET_MODELS, load_extract_targets
from bps_etl.extract.pipeline import DEFAULT_EXTRACT_OUTPUT_DIR, run_extract
from bps_etl.load.database import DEFAULT_DATABASE_PATH, DEFAULT_LOAD_METRICS_PATH, DEFAULT_TRANSFORM_DIR, run_load
from bps_etl.transform.pipeline import DEFAULT_TRANSFORM_OUTPUT_DIR, run_transform


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"\''))


def require_api_key() -> str:
    load_env_file(ROOT / ".env")
    api_key = os.getenv("BPS_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("BPS_API_KEY is missing. Copy .env.example to .env and fill the key.")
    return api_key


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run BPS ETL pipeline")
    parser.add_argument("--phase", choices=["extract", "transform", "load"], default="extract", help="Pipeline phase to run. Fase 5 supports loading transform artifacts into SQLite.")
    parser.add_argument("--mode", choices=["quick", "full"], default="quick", help="quick uses selected committed artifacts; full is reserved for later expansion.")
    parser.add_argument("--selected-indicators", type=Path, default=ROOT / "results" / "api" / "selected_indicators.json")
    parser.add_argument("--extract-manifest", type=Path, default=ROOT / "results" / "api" / "extract" / "extract_manifest.json")
    parser.add_argument("--transform-dir", type=Path, default=DEFAULT_TRANSFORM_DIR)
    parser.add_argument("--database-path", type=Path, default=DEFAULT_DATABASE_PATH)
    parser.add_argument("--metrics-path", type=Path, default=DEFAULT_LOAD_METRICS_PATH)
    parser.add_argument("--source-git-commit", default=None)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--retries", type=int, default=2)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.mode == "full":
        parser.error("--mode full is reserved for later expansion; use --mode quick")

    if args.phase == "transform":
        summary = run_transform(
            extract_manifest_path=args.extract_manifest,
            selected_indicators_path=args.selected_indicators,
            output_dir=args.output_dir or DEFAULT_TRANSFORM_OUTPUT_DIR,
        )
        print(json.dumps({k: v for k, v in summary.items() if k != "snapshots"}, ensure_ascii=False, indent=2))
        return 0

    if args.phase == "load":
        summary = run_load(
            database_path=args.database_path,
            transform_dir=args.transform_dir,
            extract_manifest_path=args.extract_manifest,
            metrics_path=args.metrics_path,
            source_git_commit=args.source_git_commit,
        )
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0

    targets = load_extract_targets(args.selected_indicators)
    client = BPSClient(
        api_key=require_api_key(),
        base_url=os.getenv("BPS_BASE_URL", BPS_BASE_URL),
        timeout=args.timeout,
        retries=args.retries,
    )
    summary = run_extract(client=client, targets=targets, output_dir=args.output_dir or DEFAULT_EXTRACT_OUTPUT_DIR, metadata_models=TARGET_MODELS)
    print(json.dumps({k: v for k, v in summary.items() if k != "snapshots"}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
