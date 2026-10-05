# test_checks.py
import pandas as pd

from src.checks import (
    check_data_types,
    check_duplicates,
    check_missing_values,
    check_invalid_values,
    check_invalid_dates
)


def test_missing_values(sample_df):
    result = check_missing_values(sample_df)

    assert result.loc["revenue", "missing_count"] == 20


def test_duplicates(sample_df):
    result = check_duplicates(sample_df)

    assert result["duplicate_count"] == 10


def test_data_types(sample_df):
    result = check_data_types(sample_df)

    assert result.loc["customer_id", "data_type"] == "int64"
    assert result.loc["quantity", "data_type"] == "int64"
    assert result.loc["revenue", "data_type"] == "float64"


def test_invalid_values(sample_df, sample_config):
    result = check_invalid_values(sample_df, sample_config.validation_rules)

    assert result.loc[
        (result["column"] == "quantity") & (result["rule"] == "min"), "invalid_count"
    ].iloc[0] == 1

    assert result.loc[
        (result["column"] == "revenue") & (result["rule"] == "min"), "invalid_count"
    ].iloc[0] == 1

    assert result.loc[
        result["column"] == "region", "invalid_count"
    ].iloc[0] == 1


def test_invalid_dates(sample_df):
    result = check_invalid_dates(sample_df, ["date"])

    assert result.loc[
        result["column"] == "date", "invalid_count"
    ].iloc[0] == 1