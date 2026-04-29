#!/usr/bin/env python3
"""ETL runner entry point scaffold."""

from __future__ import annotations

import argparse


def main() -> int:
    parser = argparse.ArgumentParser(description="Run BPS ETL pipeline")
    parser.add_argument("--mode", choices=["quick", "full"], default="quick")
    args = parser.parse_args()
    print(f"ETL runner scaffold. Mode={args.mode}. Implemented in later phases.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
