import pandas as pd

from src.cleaning import (
    remove_duplicates,
    clean_dates,
    clean_text_columns,
    impute_missing_values,
)
from src.config import load_config


def test_remove_duplicates(sample_df):

    cleaned_df = remove_duplicates(sample_df)

    assert len(cleaned_df) == 1000
    assert cleaned_df.duplicated().sum() == 0


def test_clean_dates(sample_df):

    cleaned_df = clean_dates(sample_df, ["date"])

    assert pd.api.types.is_datetime64_any_dtype(cleaned_df["date"])
    assert cleaned_df["date"].isna().sum() == 1


def test_clean_text_columns(sample_df):

    test_df = sample_df.copy()
    test_df.loc[0, "region"] = "  North  "

    cleaned_df = clean_text_columns(test_df, ["region"])

    assert cleaned_df.loc[0, "region"] == "North"


def test_impute_missing_values(sample_df):

    config = load_config("config/default.yaml")

    cleaned_df = impute_missing_values(
        sample_df,
        config,
    )

    assert cleaned_df["revenue"].isna().sum() == 0



def test_imputation_override(sample_df, tmp_path):

    config_file = tmp_path / "override.yaml"

    config_file.write_text(
        """
cleaning:
  missing_values:
    enabled: true
    numerical:
      method: median
    categorical:
      method: mode

overrides:
  revenue:
    method: mean
""",
        encoding="utf-8",
    )

    config = load_config(config_file)

    expected_mean = sample_df["revenue"].mean()

    cleaned_df = impute_missing_values(
        sample_df,
        config,
    )

    missing_index = sample_df["revenue"].isna().idxmax()

    assert cleaned_df.loc[missing_index, "revenue"] == expected_mean


def test_imputation_disabled(sample_df, tmp_path):

    config_file = tmp_path / "disabled.yaml"

    config_file.write_text(
        """
cleaning:
  missing_values:
    enabled: false
    numerical:
      method: median
    categorical:
      method: mode
""",
        encoding="utf-8",
    )

    config = load_config(config_file)

    cleaned_df = impute_missing_values(
        sample_df,
        config,
    )

    assert cleaned_df["revenue"].isna().sum() == 20

    pd.testing.assert_frame_equal(cleaned_df, sample_df)