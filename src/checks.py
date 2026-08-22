# checks.py
import pandas as pd


def check_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Check for missing values in each column."""

    result = pd.DataFrame({
        "missing_count": df.isna().sum(),
        "missing_percentage": df.isna().mean() * 100,
    })

    return result.sort_values("missing_count", ascending=False)


def check_duplicates(df: pd.DataFrame) -> dict:
    """Check for duplicate rows."""

    duplicate_count = df.duplicated().sum()

    return {
        "duplicate_count": int(duplicate_count),
        "duplicate_percentage": float(
            duplicate_count / len(df) * 100
        ),
    }


def check_data_types(df: pd.DataFrame) -> pd.DataFrame:
    """Return detected data types for each column."""

    return pd.DataFrame({
        "data_type": df.dtypes.astype(str)
    })