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


def check_invalid_values(df, rules):
    """Check columns against configurable validation rules."""

    results = []

    for column, column_rules in rules.items():

        if column not in df.columns:
            continue

        for rule, value in column_rules.items():

            if rule == "min":
                invalid = df[column] < value

            elif rule == "max":
                invalid = df[column] > value

            elif rule == "allowed":
                invalid = ~df[column].isin(value)

            else:
                continue

            results.append(
                {
                    "column": column,
                    "rule": rule,
                    "invalid_count": int(invalid.sum()),
                }
            )

    return pd.DataFrame(results)


def check_invalid_dates(df, columns):
    """Check columns for invalid date values."""

    results = []

    for column in columns:

        if column not in df.columns:
            continue

        parsed_dates = pd.to_datetime(df[column], errors="coerce")

        invalid = parsed_dates.isna() & df[column].notna()

        results.append(
            {
                "column": column,
                "invalid_count": int(invalid.sum()),
            }
        )

    return pd.DataFrame(results)