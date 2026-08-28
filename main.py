import pandas as pd

from src.pipeline import run_pipeline
from src.reporting import generate_excel_report


df = pd.read_csv("data/sample_data.csv")

results = run_pipeline(df)

generate_excel_report(
    results,
    "reports/data_quality_report.xlsx"
)

print("Data quality report generated successfully.")