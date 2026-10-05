"""Counts use nonmissing values for rule/date denominators, and all rows otherwise."""
import numpy as np
import pandas as pd


def check_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    result = pd.DataFrame({
        "missing_count": df.isna().sum(),
        "row_count": len(df),
        "missing_percentage": df.isna().mean().fillna(0) * 100,
    })
    return result.rename_axis("column").sort_values("missing_count", ascending=False)


def check_duplicates(df: pd.DataFrame) -> dict:
    count = int(df.duplicated().sum())
    return {
        "duplicate_count": count,
        "row_count": len(df),
        "duplicate_percentage": count / len(df) * 100 if len(df) else 0.0,
    }


def check_data_types(df: pd.DataFrame) -> pd.DataFrame:
    """Observed pandas dtypes, not an expected-schema validation."""
    return pd.DataFrame({"data_type": df.dtypes.astype(str)}).rename_axis("column")


def check_invalid_values(df, rules):
    """Count violations per rule; nulls are assessed only by missing-value checks.

    Numeric strings can satisfy range rules. Non-numeric and infinite values
    receive one numeric_type violation and are excluded from range denominators.
    Original values are never changed by validation.
    """
    results = []
    for column, settings in rules.items():
        column_rules = settings.model_dump(exclude_none=True) if hasattr(settings, "model_dump") else settings
        if column not in df.columns:
            for rule in column_rules:
                results.append({"column": column, "rule": rule, "invalid_count": 0,
                                "evaluated_count": 0, "invalid_percentage": 0.0,
                                "status": "missing_column"})
            continue
        source = df[column]
        present = source.notna()
        if "min" in column_rules or "max" in column_rules:
            numeric = pd.to_numeric(source, errors="coerce")
            finite = numeric.notna() & np.isfinite(numeric)
            bad_type = present & ~finite
            count, total = int(bad_type.sum()), int(present.sum())
            results.append({"column": column, "rule": "numeric_type", "invalid_count": count,
                            "evaluated_count": total, "invalid_percentage": count / total * 100 if total else 0.0,
                            "status": "checked"})
        for rule, value in column_rules.items():
            if rule == "allowed":
                evaluated = present
                invalid = present & ~source.isin(value)
            elif rule in {"min", "max"}:
                evaluated = present & finite
                invalid = evaluated & ((numeric < value) if rule == "min" else (numeric > value))
            else:
                raise ValueError(f"Unsupported rule: {rule}")
            count, total = int(invalid.sum()), int(evaluated.sum())
            results.append({"column": column, "rule": rule, "invalid_count": count,
                            "evaluated_count": total, "invalid_percentage": count / total * 100 if total else 0.0,
                            "status": "checked"})
    return pd.DataFrame(results, columns=["column", "rule", "invalid_count", "evaluated_count",
                                          "invalid_percentage", "status"])


def parse_dates(series, date_format="ISO8601"):
    """Parse a declared format; normalize offsets to UTC and reject numeric epochs."""
    if pd.api.types.is_datetime64_any_dtype(series):
        return pd.to_datetime(series, errors="coerce", utc=True)
    text = series.astype("string")
    numeric_input = series.map(lambda value: isinstance(value, (int, float, np.number)))
    text = text.mask(numeric_input, pd.NA)
    return pd.to_datetime(text, format=date_format, errors="coerce", utc=True)


def check_invalid_dates(df, columns, date_format="ISO8601"):
    results = []
    for column in dict.fromkeys(columns):
        if column not in df.columns:
            results.append({"column": column, "invalid_count": 0, "evaluated_count": 0,
                            "invalid_percentage": 0.0, "status": "missing_column"})
            continue
        parsed = parse_dates(df[column], date_format)
        count = int((parsed.isna() & df[column].notna()).sum())
        total = int(df[column].notna().sum())
        results.append({"column": column, "invalid_count": count, "evaluated_count": total,
                        "invalid_percentage": count / total * 100 if total else 0.0,
                        "status": "checked"})
    return pd.DataFrame(results, columns=["column", "invalid_count", "evaluated_count",
                                          "invalid_percentage", "status"])
