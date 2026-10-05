"""Exercise the public commands, generated values, and fresh-checkout behavior."""
from pathlib import Path
import shutil
import subprocess
import sys

from openpyxl import load_workbook
import pandas as pd
import pytest

from generate_sample_data import generate_sample_data
from main import main

ROOT = Path(__file__).resolve().parents[1]


def test_end_to_end_cli_from_another_directory(tmp_path):
    report = tmp_path / "new/reports/quality.xlsx"
    cleaned = tmp_path / "new/data/cleaned.csv"
    command = [
        sys.executable, str(ROOT / "main.py"),
        "--input", str(ROOT / "data/sample_data.csv"),
        "--config", str(ROOT / "config/example.yaml"),
        "--report", str(report), "--cleaned-output", str(cleaned),
    ]
    run = subprocess.run(command, cwd=tmp_path, capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
    assert "Rows: 1,010 -> 1,000" in run.stdout
    assert "missing cells imputed: 20" in run.stdout
    frame = pd.read_csv(cleaned)
    assert frame.shape == (1000, 6)
    assert frame["revenue"].isna().sum() == 0
    assert frame["date"].isna().sum() == 1
    with_report = load_workbook(report)
    assert list(with_report["Summary"].values)[1:] == [
        ("Missing Values", 20, 1, "missing cells", "checked"),
        ("Duplicate Rows", 10, 0, "extra exact duplicate rows", "checked"),
        ("Invalid Values", 3, 3, "rule violations, not distinct rows", "checked"),
        ("Invalid Dates", 1, 0, "nonmissing unparseable date cells", "checked"),
    ]
    assert "BEFORE" in {row[0] for row in list(with_report["Missing Values"].values)[1:]}
    assert "AFTER" in {row[0] for row in list(with_report["Missing Values"].values)[1:]}
    with_report.close()


def test_fresh_checkout_defaults(tmp_path):
    clone = tmp_path / "checkout"
    clone.mkdir()
    for name in ["main.py", "generate_sample_data.py"]:
        shutil.copy2(ROOT / name, clone / name)
    for name in ["src", "config", "data"]:
        shutil.copytree(ROOT / name, clone / name, ignore=shutil.ignore_patterns("__pycache__"))
    assert not (clone / "reports").exists()
    run = subprocess.run([sys.executable, str(clone / "main.py")], cwd=tmp_path, capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
    assert (clone / "reports/data_quality_report.xlsx").exists()
    assert pd.read_csv(clone / "reports/cleaned_data.csv").shape == (1000, 6)


def test_generator_reproduces_committed_sample(sample_df, tmp_path):
    path = tmp_path / "data/sample.csv"
    generate_sample_data(path)
    pd.testing.assert_frame_equal(pd.read_csv(path), sample_df)


def test_help(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0
    assert "--cleaned-output" in capsys.readouterr().out


def test_missing_input_has_useful_error(tmp_path, capsys):
    assert main(["--input", str(tmp_path / "missing.csv")]) == 2
    output = capsys.readouterr()
    assert "Error:" in output.err and "missing.csv" in output.err
    assert "Traceback" not in output.err


def test_source_overwrite_is_rejected(tmp_path, capsys):
    path = tmp_path / "input.csv"
    path.write_text("x\n1\n", encoding="utf-8")
    assert main(["--input", str(path), "--cleaned-output", str(path)]) == 2
    assert "never overwritten" in capsys.readouterr().err
    assert path.read_text() == "x\n1\n"


def test_empty_csv_error(tmp_path, capsys):
    path = tmp_path / "empty.csv"
    path.write_text("", encoding="utf-8")
    assert main(["--input", str(path)]) == 2
    assert "No columns to parse" in capsys.readouterr().err


def test_header_only_csv_reports_warnings(tmp_path, capsys):
    path = tmp_path / "empty.csv"
    path.write_text("other\n", encoding="utf-8")
    assert main(["--input", str(path), "--report", str(tmp_path / "report.xlsx"),
                 "--cleaned-output", str(tmp_path / "cleaned.csv")]) == 0
    output = capsys.readouterr()
    assert "zero rows" in output.err
    assert "configured columns absent and unchecked" in output.err
    assert pd.read_csv(tmp_path / "cleaned.csv").empty


def test_imports_do_not_generate_files(tmp_path):
    code = f"import sys; sys.path.insert(0, {str(ROOT)!r}); import main; import generate_sample_data"
    run = subprocess.run([sys.executable, "-c", code], cwd=tmp_path, capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
    assert not run.stdout
    assert list(tmp_path.iterdir()) == []
