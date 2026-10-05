"""Basic descriptive profiles, including well-defined empty results."""
import pandas as pd


def profile_dataset(df):
    return {"rows": len(df), "columns": len(df.columns),
            "duplicate_count": int(df.duplicated().sum()),
            "memory_usage_bytes": int(df.memory_usage(deep=True).sum())}


def profile_numeric_columns(df):
    numeric = df.select_dtypes(include="number")
    if numeric.shape[1]:
        profile = numeric.describe().T
    else:
        profile = pd.DataFrame(columns=["count", "mean", "std", "min", "25%", "50%", "75%", "max"])
    profile["missing"] = numeric.isna().sum()
    profile["unique"] = numeric.nunique()
    return profile.rename_axis("column")


def profile_categorical_columns(df):
    categorical = df.select_dtypes(include=["object", "string", "category"])
    profile = pd.DataFrame(index=categorical.columns)
    profile["count"] = categorical.count()
    profile["missing"] = categorical.isna().sum()
    profile["unique"] = categorical.nunique()
    modes = categorical.mode()
    profile["most_common"] = modes.iloc[0] if len(modes) else pd.Series(index=categorical.columns, dtype="object")
    return profile.rename_axis("column")
