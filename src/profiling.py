import pandas as pd


def profile_dataset(df):
    """Return basic information about the dataset."""

    profile = {
        "rows": len(df),
        "columns": len(df.columns),
        "duplicate_count": df.duplicated().sum(),
        "memory_usage": df.memory_usage(deep=True).sum(),
    }

    return profile


def profile_numeric_columns(df):
    """Return descriptive statistics for numeric columns."""

    numeric_df = df.select_dtypes(include="number")

    profile = numeric_df.describe().T

    profile["missing"] = numeric_df.isna().sum()
    profile["unique"] = numeric_df.nunique()

    return profile


def profile_categorical_columns(df):
    """Return descriptive statistics for categorical columns."""

    categorical_df = df.select_dtypes(include=["object", "string"])

    profile = pd.DataFrame(index=categorical_df.columns)

    profile["count"] = categorical_df.count()
    profile["missing"] = categorical_df.isna().sum()
    profile["unique"] = categorical_df.nunique()
    profile["most_common"] = categorical_df.mode().iloc[0]

    return profile