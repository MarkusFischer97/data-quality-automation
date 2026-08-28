from src.checks import (
    check_missing_values,
    check_duplicates,
    check_data_types,
    check_invalid_values,
    check_invalid_dates,
)

from src.profiling import (
    profile_dataset,
    profile_numeric_columns,
    profile_categorical_columns,
)

from src.cleaning import (
    remove_duplicates,
    clean_dates,
    clean_text_columns,
)

from src.rules import VALIDATION_RULES


def run_pipeline(df):
    """Run the complete data quality pipeline."""

    # Quality checks before cleaning
    missing_values = check_missing_values(df)
    duplicates = check_duplicates(df)
    data_types = check_data_types(df)
    invalid_values = check_invalid_values(df, VALIDATION_RULES)
    invalid_dates = check_invalid_dates(df, ["date"])

    # Profiling
    dataset_profile = profile_dataset(df)
    numeric_profile = profile_numeric_columns(df)
    categorical_profile = profile_categorical_columns(df)

    # Cleaning
    cleaned_df = remove_duplicates(df)
    cleaned_df = clean_dates(cleaned_df, ["date"])
    cleaned_df = clean_text_columns(
        cleaned_df,
        ["product", "region"]
    )

    # Quality checks after cleaning
    cleaned_missing_values = check_missing_values(cleaned_df)
    cleaned_duplicates = check_duplicates(cleaned_df)
    cleaned_data_types = check_data_types(cleaned_df)
    cleaned_invalid_values = check_invalid_values(
        cleaned_df,
        VALIDATION_RULES
    )
    cleaned_invalid_dates = check_invalid_dates(
        cleaned_df,
        ["date"]
    )



    return {
        "cleaned_data": cleaned_df,
        "missing_values": missing_values,
        "duplicates": duplicates,
        "data_types": data_types,
        "invalid_values": invalid_values,
        "invalid_dates": invalid_dates,
        "dataset_profile": dataset_profile,
        "numeric_profile": numeric_profile,
        "categorical_profile": categorical_profile,
        "cleaned_duplicates": cleaned_duplicates,
        "cleaned_missing_values": cleaned_missing_values,
        "cleaned_duplicates": cleaned_duplicates,
        "cleaned_data_types": cleaned_data_types,
        "cleaned_invalid_values": cleaned_invalid_values,
        "cleaned_invalid_dates": cleaned_invalid_dates,
    }