"""Command-line interface for the churn feature pipeline."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from churn_pipeline.config import PipelineConfig
from churn_pipeline.pipeline import run_pipeline
from churn_pipeline.validation import ValidationError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="churn-pipeline")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run the local churn feature pipeline.")
    run_parser.add_argument("--input", required=True, type=Path, help="Path to the raw customer CSV.")
    run_parser.add_argument("--output", required=True, type=Path, help="Path for the processed feature CSV.")
    run_parser.add_argument(
        "--reference-date",
        default=None,
        help="Optional YYYY-MM-DD snapshot date for recency features.",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "run":
        return _run_command(args)

    parser.error(f"Unknown command: {args.command}")
    return 2


def _run_command(args: argparse.Namespace) -> int:
    try:
        features = run_pipeline(
            args.input,
            args.output,
            PipelineConfig(reference_date=args.reference_date),
        )
    except (FileNotFoundError, ValidationError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Wrote {len(features)} rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
