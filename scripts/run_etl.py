#!/usr/bin/env python3
"""ETL runner entry point.

Fase 3 implements the extract phase only. Transform/load/dashboard generation stay
phase-gated for later phases.
"""

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
    parser.add_argument("--phase", choices=["extract"], default="extract", help="Pipeline phase to run. Fase 3 supports extract only.")
    parser.add_argument("--mode", choices=["quick", "full"], default="quick", help="quick uses selected Fase 1 targets; full is reserved for later expansion.")
    parser.add_argument("--selected-indicators", type=Path, default=ROOT / "results" / "api" / "selected_indicators.json")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_EXTRACT_OUTPUT_DIR)
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--retries", type=int, default=2)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.mode == "full":
        parser.error("--mode full is reserved for later phases; use --mode quick in Fase 3")

    targets = load_extract_targets(args.selected_indicators)
    client = BPSClient(
        api_key=require_api_key(),
        base_url=os.getenv("BPS_BASE_URL", BPS_BASE_URL),
        timeout=args.timeout,
        retries=args.retries,
    )
    summary = run_extract(client=client, targets=targets, output_dir=args.output_dir, metadata_models=TARGET_MODELS)
    print(json.dumps({k: v for k, v in summary.items() if k != "snapshots"}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
