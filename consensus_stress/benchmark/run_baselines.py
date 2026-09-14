#!/usr/bin/env python3
"""Run pre-registered CST-Bench external baselines on the frozen VitaminC cohort."""
from __future__ import annotations

import argparse
from pathlib import Path

from cst_bench import run_model

HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE.parent / "round5"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=("qwen", "ling"), required=True)
    parser.add_argument("--workers", type=int, default=24)
    parser.add_argument("--limit-items", type=int, default=None,
                        help="debug-only limit; never used for headline results")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    summary = run_model(args.model, args.output_dir, workers=args.workers,
                        limit_items=args.limit_items)
    print(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
