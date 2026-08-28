import pandas as pd
from src.config import get_missing_value_method


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


def impute_missing_values(df, config):
    """Impute missing values according to the configuration."""

    cleaned_df = df.copy()

    if not config.cleaning.missing_values.enabled:
        return cleaned_df

    for column in cleaned_df.columns:

        if not cleaned_df[column].isna().any():
            continue

        if pd.api.types.is_numeric_dtype(cleaned_df[column]):
            data_type = "numerical"
        elif pd.api.types.is_string_dtype(cleaned_df[column]):
            data_type = "categorical"
        else:
            continue

        method = get_missing_value_method(
            config,
            column,
            data_type,
        )

        if method == "mean":
            cleaned_df[column] = cleaned_df[column].fillna(
                cleaned_df[column].mean()
            )

        elif method == "median":
            cleaned_df[column] = cleaned_df[column].fillna(
                cleaned_df[column].median()
            )

        elif method == "mode":
            mode = cleaned_df[column].mode()

            if not mode.empty:
                cleaned_df[column] = cleaned_df[column].fillna(
                    mode.iloc[0]
                )

    return cleaned_df