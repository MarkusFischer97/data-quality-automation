"""Conservative transformations; business-rule violations are not corrected."""
import numpy as np
import pandas as pd

from src.checks import parse_dates
from src.config import get_missing_value_method


def remove_duplicates(df):
    return df.drop_duplicates().copy()


def clean_dates(df, columns, date_format="ISO8601"):
    cleaned = df.copy()
    for column in dict.fromkeys(columns):
        if column in cleaned.columns:
            cleaned[column] = parse_dates(cleaned[column], date_format)
    return cleaned


def clean_text_columns(df, columns):
    """Trim surrounding whitespace; blank text becomes missing. Preserve case."""
    cleaned = df.copy()
    for column in dict.fromkeys(columns):
        if column in cleaned.columns:
            text = cleaned[column].astype("string").str.strip()
            cleaned[column] = text.mask(text.eq(""), pd.NA)
    return cleaned


def impute_missing_values(df, config):
    cleaned = df.copy()
    if not config.cleaning.missing_values.enabled:
        return cleaned
    for column in cleaned.columns:
        source = cleaned[column]
        if not source.isna().any():
            continue
        if pd.api.types.is_numeric_dtype(source) and not pd.api.types.is_bool_dtype(source):
            data_type = "numerical"
        elif (pd.api.types.is_string_dtype(source) or source.dtype == object
              or isinstance(source.dtype, pd.CategoricalDtype)):
            data_type = "categorical"
        else:
            continue
        method = get_missing_value_method(config, column, data_type)
        if method == "skip":
            continue
        if data_type == "categorical" and method != "mode":
            raise ValueError(f"Column '{column}' is categorical; use mode or skip, not {method}")
        donors = source.dropna()
        if data_type == "numerical":
            donors = donors[np.isfinite(donors)]
        if donors.empty:
            continue
        if method == "mode":
            modes = donors.mode()
            if modes.empty:
                continue
            fill_value = modes.iloc[0]
        else:
            fill_value = donors.mean() if method == "mean" else donors.median()
        if pd.isna(fill_value) or (data_type == "numerical" and not np.isfinite(fill_value)):
            continue
        if pd.api.types.is_integer_dtype(source) and float(fill_value) % 1:
            source = source.astype("Float64")
        cleaned[column] = source.fillna(fill_value)
    return cleaned
