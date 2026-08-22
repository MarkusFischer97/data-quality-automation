# test_checks.py
import pandas as pd
import pytest

from src.checks import (
    check_data_types,
    check_duplicates,
    check_missing_values,
)


@pytest.fixture
def sample_df():
    return pd.read_csv("data/sample_data.csv")


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