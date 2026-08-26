import pandas as pd


def remove_duplicates(df):
    """Return a copy of the dataframe without duplicate rows."""

    return df.drop_duplicates().copy()


def clean_dates(df, columns):
    """Convert specified columns to datetime."""

    cleaned_df = df.copy()

    for column in columns:
        if column not in cleaned_df.columns:
            continue

        cleaned_df[column] = pd.to_datetime(
            cleaned_df[column],
            errors="coerce"
        )

    return cleaned_df


def clean_text_columns(df, columns):
    """Standardize text values in specified columns."""

    cleaned_df = df.copy()

    for column in columns:
        if column not in cleaned_df.columns:
            continue

        cleaned_df[column] = (
            cleaned_df[column]
            .astype("string")
            .str.strip()
        )

    return cleaned_df