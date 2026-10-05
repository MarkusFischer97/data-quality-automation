"""Command-line entry point for the CSV data-quality example."""
import argparse
import sys
from pathlib import Path

import pandas as pd
import yaml

from src.config import load_config
from src.pipeline import run_pipeline
from src.reporting import create_summary, generate_excel_report

ROOT = Path(__file__).resolve().parent


def build_parser():
    parser = argparse.ArgumentParser(
        description="Profile and check a CSV, apply configured cleaning, and save an Excel report and cleaned CSV.",
        epilog="Relative paths are resolved from your working directory. Defaults use the bundled repository paths.",
    )
    parser.add_argument(
        "--input", type=Path, default=ROOT / "data/sample_data.csv",
        help="Input CSV (default: bundled sample)",
    )
    parser.add_argument(
        "--config", type=Path, default=ROOT / "config/default.yaml",
        help="Validated YAML settings (default: config/default.yaml)",
    )
    parser.add_argument(
        "--report", type=Path, default=ROOT / "reports/data_quality_report.xlsx",
        help="Excel report (.xlsx); parent directories are created",
    )
    parser.add_argument(
        "--cleaned-output", type=Path, default=ROOT / "reports/cleaned_data.csv",
        help="Cleaned CSV; parent directories are created",
    )
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        paths = [args.input.resolve(), args.config.resolve(), args.report.resolve(), args.cleaned_output.resolve()]
        if len(set(paths)) != len(paths):
            raise ValueError("Input, config, report, and cleaned-output paths must be different; source files are never overwritten")
        if args.input.suffix.lower() != ".csv" or args.cleaned_output.suffix.lower() != ".csv":
            raise ValueError("Input and cleaned-output must use the .csv extension")
        if args.report.suffix.lower() != ".xlsx":
            raise ValueError("Report must use the .xlsx extension")
        config = load_config(args.config)
        df = pd.read_csv(args.input)
        results = run_pipeline(df, config)
        generate_excel_report(results, args.report, context={
            "input": str(args.input.resolve()), "config_file": str(args.config.resolve()),
            "cleaned_output": str(args.cleaned_output.resolve()),
        })
        args.cleaned_output.parent.mkdir(parents=True, exist_ok=True)
        results["cleaned_data"].to_csv(args.cleaned_output, index=False)
    except (OSError, ValueError, TypeError, yaml.YAMLError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    print(f"Rows: {len(df):,} -> {len(results['cleaned_data']):,}; columns: {len(df.columns)}")
    print(create_summary(results).to_string())
    coerced = results["actions"].loc[results["actions"]["action"].eq("Dates coerced to missing"), "count"].sum()
    imputed = results["actions"].loc[results["actions"]["action"].eq("Missing values imputed"), "count"].sum()
    print(f"Dates coerced to missing: {coerced}; missing cells imputed: {imputed}.")
    print("Remaining violations are flagged for review; no business values are automatically corrected.")
    absent = results["configured_columns"].loc[
        results["configured_columns"]["status"].eq("missing_column"), "column"
    ].unique()
    if len(absent):
        print(f"Warning: configured columns absent and unchecked: {', '.join(absent)}", file=sys.stderr)
    if df.empty:
        print("Warning: input has zero rows; zero percentages do not imply validated data.", file=sys.stderr)
    print(f"Report: {args.report.resolve()}")
    print(f"Cleaned CSV: {args.cleaned_output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
