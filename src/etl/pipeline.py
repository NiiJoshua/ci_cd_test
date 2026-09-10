"""Orchestrate extract -> validate -> transform -> load.

Run from the command line:
    python -m src.etl.pipeline --input data/raw/customers_raw.csv --output data/out/customers_clean.csv

Exit code is non-zero if any rows are rejected, so CI can *fail the build* on
bad data instead of silently shipping it.
"""
from __future__ import annotations
import argparse
import sys

from .extract import extract
from .validate import validate
from .transform import transform
from .load import load


def run(input_path: str, output_path: str, fail_on_reject: bool = False) -> dict:
    raw = extract(input_path)
    clean, rejects, report = validate(raw)
    tidy = transform(clean)
    final = load(tidy, output_path)
    report["rows_written"] = int(len(final))
    report["output_path"] = output_path
    report["fail_on_reject"] = fail_on_reject
    report["failed"] = bool(fail_on_reject and report["rows_rejected"] > 0)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Tiny ETL pipeline for the CI/CD demo.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument(
        "--fail-on-reject",
        action="store_true",
        help="Exit non-zero if any rows fail validation (use this in CI).",
    )
    args = parser.parse_args(argv)

    report = run(args.input, args.output, fail_on_reject=args.fail_on_reject)

    print("ETL run summary")
    for k, v in report.items():
        print(f"  {k}: {v}")

    if report["failed"]:
        print("::error::Validation found rejected rows and --fail-on-reject is set.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
