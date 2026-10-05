"""Orchestrate checks, profiling, and the small set of configured transformations."""
import pandas as pd

from src.checks import (
    check_data_types, check_duplicates, check_invalid_dates,
    check_invalid_values, check_missing_values,
)
from src.cleaning import clean_dates, clean_text_columns, impute_missing_values, remove_duplicates
from src.config import AppConfig
from src.profiling import profile_categorical_columns, profile_dataset, profile_numeric_columns


def _assess(df, config):
    return {
        "missing_values": check_missing_values(df),
        "duplicates": check_duplicates(df),
        "data_types": check_data_types(df),
        "invalid_values": check_invalid_values(df, config.validation_rules),
        "invalid_dates": check_invalid_dates(df, config.cleaning.date_columns, config.cleaning.date_format),
        "dataset_profile": profile_dataset(df),
        "numeric_profile": profile_numeric_columns(df),
        "categorical_profile": profile_categorical_columns(df),
    }


def run_pipeline(df: pd.DataFrame, config: AppConfig) -> dict:
    """Assess both stages; never mutate input or automatically repair business values."""
    if not df.columns.is_unique or not all(isinstance(column, str) for column in df.columns):
        raise ValueError("Dataset columns must have unique string names")
    before = _assess(df, config)
    actions = []
    cleaned = remove_duplicates(df) if config.cleaning.duplicates.enabled else df.copy()
    actions.append({"action": "Duplicate rows removed", "column": "(whole row)",
                    "count": len(df) - len(cleaned),
                    "detail": "Exact input-row duplicates; first occurrence retained."})

    dates = check_invalid_dates(cleaned, config.cleaning.date_columns, config.cleaning.date_format)
    for record in dates.to_dict("records"):
        if record["status"] == "checked":
            actions.append({"action": "Dates coerced to missing", "column": record["column"],
                            "count": record["invalid_count"],
                            "detail": "Unparseable values become NaT; no date information is recovered."})
    cleaned = clean_dates(cleaned, config.cleaning.date_columns, config.cleaning.date_format)

    for column in dict.fromkeys(config.cleaning.text_columns):
        if column in cleaned.columns:
            text = cleaned[column].astype("string")
            changed = text.notna() & text.ne(text.str.strip())
            actions.append({"action": "Text values trimmed", "column": column,
                            "count": int(changed.sum()), "detail": "Surrounding whitespace only; case preserved."})
            blanks = text.notna() & text.str.strip().eq("")
            actions.append({"action": "Blank text made missing", "column": column,
                            "count": int(blanks.sum()), "detail": "Empty/whitespace-only text becomes missing."})
    cleaned = clean_text_columns(cleaned, config.cleaning.text_columns)
    missing_before_imputation = cleaned.isna().sum()
    cleaned = impute_missing_values(cleaned, config)
    filled = missing_before_imputation - cleaned.isna().sum()
    for column, count in filled.items():
        if count:
            actions.append({"action": "Missing values imputed", "column": column,
                            "count": int(count), "detail": "Configured method; observed nonmissing values are retained."})

    configured = []
    for use, columns in [
        ("validation", config.validation_rules),
        ("date parsing", config.cleaning.date_columns),
        ("text trimming", config.cleaning.text_columns),
        ("imputation override", config.overrides),
    ]:
        for column in dict.fromkeys(columns):
            configured.append({"column": column, "used_by": use,
                               "status": "present" if column in df.columns else "missing_column"})

    after = _assess(cleaned, config)
    return {
        **before,
        **{f"cleaned_{key}": value for key, value in after.items()},
        "cleaned_data": cleaned,
        "actions": pd.DataFrame(actions, columns=["action", "column", "count", "detail"]),
        "configured_columns": pd.DataFrame(configured, columns=["column", "used_by", "status"]),
        "config": config.model_dump(),
    }
