from src.profiling import (
    profile_dataset,
    profile_numeric_columns,
    profile_categorical_columns,
)

def test_profile_dataset(sample_df):

    result = profile_dataset(sample_df)

    assert result["rows"] == 1010
    assert result["columns"] == 6
    assert result["duplicate_count"] == 10


def test_profile_numeric_columns(sample_df):

    result = profile_numeric_columns(sample_df)

    assert "quantity" in result.index
    assert "revenue" in result.index

    assert result.loc["quantity", "missing"] == 0
    assert result.loc["revenue", "missing"] == 20


def test_profile_categorical_columns(sample_df):

    result = profile_categorical_columns(sample_df)

    assert "product" in result.index
    assert "region" in result.index

    assert result.loc["region", "missing"] == 0
    assert result.loc["region", "unique"] == 5