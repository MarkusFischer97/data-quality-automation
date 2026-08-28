import pandas as pd


def generate_excel_report(results, output_path):
    """Generate an Excel report from pipeline results."""

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:

        summary = create_summary(results)

        summary.to_excel(
            writer,
            sheet_name="Summary",
            index=True,
        )

        results["missing_values"].to_excel(
            writer,
            sheet_name="Missing Values",
            index=True,
        )

        pd.DataFrame([results["duplicates"]]).to_excel(
            writer,
            sheet_name="Duplicates",
            index=False,
        )

        results["invalid_values"].to_excel(
            writer,
            sheet_name="Invalid Values",
            index=False,
        )

        results["invalid_dates"].to_excel(
            writer,
            sheet_name="Invalid Dates",
            index=False,
        )

        results["data_types"].to_excel(
            writer,
            sheet_name="Data Types",
            index=True,
        )


def create_summary(results):
    """Create a before/after summary of data quality issues."""

    summary = {
        "Missing Values": {
            "Before": results["missing_values"]["missing_count"].sum(),
            "After": results["cleaned_missing_values"]["missing_count"].sum(),
        },
        "Duplicate Rows": {
            "Before": results["duplicates"]["duplicate_count"],
            "After": results["cleaned_duplicates"]["duplicate_count"],
        },
        "Invalid Values": {
            "Before": results["invalid_values"]["invalid_count"].sum(),
            "After": results["cleaned_invalid_values"]["invalid_count"].sum(),
        },
        "Invalid Dates": {
            "Before": results["invalid_dates"]["invalid_count"].sum(),
            "After": results["cleaned_invalid_dates"]["invalid_count"].sum(),
        },
    }

    return pd.DataFrame.from_dict(summary, orient="index")