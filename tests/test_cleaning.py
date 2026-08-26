import pandas as pd

from src.cleaning import (
    remove_duplicates,
    clean_dates,
    clean_text_columns
)

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
