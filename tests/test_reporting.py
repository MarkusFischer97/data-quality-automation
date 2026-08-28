from openpyxl import load_workbook

from src.pipeline import run_pipeline
from src.reporting import (
    generate_excel_report,
    create_summary,
)


def test_generate_excel_report(sample_df, tmp_path):

    results = run_pipeline(sample_df)

    output_path = tmp_path / "data_quality_report.xlsx"

    generate_excel_report(results, output_path)

    assert output_path.exists()


    workbook = load_workbook(output_path)

    assert "Summary" in workbook.sheetnames
    assert "Missing Values" in workbook.sheetnames
    assert "Duplicates" in workbook.sheetnames
    assert "Invalid Values" in workbook.sheetnames
    assert "Invalid Dates" in workbook.sheetnames
    assert "Data Types" in workbook.sheetnames


def test_create_summary(sample_df):

    results = run_pipeline(sample_df)

    summary = create_summary(results)

    assert summary.loc["Missing Values", "Before"] == 20
    assert summary.loc["Duplicate Rows", "Before"] == 10
    assert summary.loc["Duplicate Rows", "After"] == 0
    assert summary.loc["Invalid Dates", "Before"] == 1