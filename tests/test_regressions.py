"""Regression tests for the audit's concrete failures and measurement definitions."""
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from pydantic import ValidationError

from src.checks import check_duplicates, check_invalid_dates, check_invalid_values
from src.cleaning import clean_dates, impute_missing_values
from src.config import AppConfig, load_config
from src.pipeline import run_pipeline
from src.profiling import profile_categorical_columns, profile_numeric_columns
from src.reporting import create_summary, generate_excel_report


@pytest.mark.parametrize("frame", [
    pd.DataFrame(),
    pd.DataFrame({"x": pd.Series(dtype="float64")}),
    pd.DataFrame({"x": [1, 2]}),
    pd.DataFrame({"label": ["a", "b"]}),
    pd.DataFrame({"label": pd.Series([None, None], dtype="string")}),
])
def test_schema_variants_complete_and_report(frame, tmp_path):
    original = frame.copy(deep=True)
    results = run_pipeline(frame, AppConfig())
    assert results["cleaned_dataset_profile"]["rows"] == len(frame.drop_duplicates())
    assert create_summary(results).loc["Invalid Values", "After"] == 0
    assert list(results["invalid_values"].columns) == [
        "column", "rule", "invalid_count", "evaluated_count", "invalid_percentage", "status"
    ]
    generate_excel_report(results, tmp_path / "nested/report.xlsx")
    pd.testing.assert_frame_equal(frame, original)


def test_zero_row_percentages_and_profiles():
    frame = pd.DataFrame({"x": pd.Series(dtype="float64"), "text": pd.Series(dtype="string")})
    results = run_pipeline(frame, AppConfig())
    assert check_duplicates(frame)["duplicate_percentage"] == 0
    assert results["missing_values"]["missing_percentage"].eq(0).all()
    assert profile_numeric_columns(frame).loc["x", "count"] == 0
    assert pd.isna(profile_categorical_columns(frame).loc["text", "most_common"])


def test_missing_configured_columns_are_unchecked(tmp_path):
    config = AppConfig.model_validate({
        "cleaning": {"date_columns": ["date"], "text_columns": ["region"]},
        "validation_rules": {"quantity": {"min": 1}},
        "overrides": {"id": {"method": "skip"}},
    })
    results = run_pipeline(pd.DataFrame({"other": [1]}), config)
    assert results["configured_columns"]["status"].eq("missing_column").all()
    assert results["invalid_values"]["status"].eq("missing_column").all()
    assert results["invalid_values"]["evaluated_count"].sum() == 0
    assert results["invalid_dates"]["status"].eq("missing_column").all()
    assert create_summary(results).loc["Invalid Values", "Assessment"] == "unchecked: missing configured columns"
    generate_excel_report(results, tmp_path / "report.xlsx")


def test_numeric_strings_and_bad_types_have_separate_denominators():
    frame = pd.DataFrame({"x": ["2", "-1", "bad", None, "inf", "4"]})
    original = frame.copy()
    checks = check_invalid_values(frame, {"x": {"min": 0, "max": 3}}).set_index("rule")
    assert checks.loc["numeric_type", "invalid_count"] == 2
    assert checks.loc["numeric_type", "evaluated_count"] == 5
    assert checks.loc["min", "invalid_count"] == 1
    assert checks.loc["min", "evaluated_count"] == 3
    assert checks.loc["max", "invalid_count"] == 1
    pd.testing.assert_frame_equal(frame, original)


def test_null_is_missing_not_allowed_violation():
    checks = check_invalid_values(pd.DataFrame({"region": ["North", None, "bad"]}),
                                  {"region": {"allowed": ["North"]}})
    assert checks.iloc[0]["invalid_count"] == 1
    assert checks.iloc[0]["evaluated_count"] == 2
    assert checks.iloc[0]["invalid_percentage"] == 50


def test_date_format_and_utc_are_consistent():
    frame = pd.DataFrame({"date": ["2025-01-01", "02/01/2025", None, "not_a_date",
                                  "2025-01-01T01:00:00+01:00"]})
    result = check_invalid_dates(frame, ["date"])
    assert result.iloc[0]["invalid_count"] == 2
    assert result.iloc[0]["evaluated_count"] == 4
    cleaned = clean_dates(frame, ["date"])
    assert cleaned["date"].isna().sum() == 3
    assert cleaned.loc[0, "date"] == cleaned.loc[4, "date"]
    assert check_invalid_dates(cleaned, ["date"]).iloc[0]["invalid_count"] == 0
    custom = clean_dates(pd.DataFrame({"date": ["02/01/2025"]}), ["date"], "%d/%m/%Y")
    assert custom.loc[0, "date"] == pd.Timestamp("2025-01-02", tz="UTC")


@pytest.mark.parametrize("value", [1735689600, 20250101])
def test_numeric_dates_are_not_epochs(value):
    result = clean_dates(pd.DataFrame({"date": [value]}), ["date"])
    assert result["date"].isna().all()


@pytest.mark.parametrize("method, expected", [("median", 2), ("mean", 3), ("mode", 1)])
def test_imputation_methods_and_identifier_skip(method, expected):
    config = AppConfig.model_validate({
        "cleaning": {"missing_values": {"numerical": {"method": method}}},
        "overrides": {"id": {"method": "skip"}},
    })
    frame = pd.DataFrame({"x": [1., 2., 6., np.nan], "id": [1., 2., 3., np.nan]})
    cleaned = impute_missing_values(frame, config)
    assert cleaned.loc[3, "x"] == expected
    assert pd.isna(cleaned.loc[3, "id"])


def test_nullable_integer_fractional_fill_promotes_dtype():
    frame = pd.DataFrame({"x": pd.Series([1, 2, None], dtype="Int64")})
    cleaned = impute_missing_values(frame, AppConfig())
    assert cleaned["x"].tolist() == [1, 2, 1.5]
    assert str(cleaned["x"].dtype) == "Float64"
    assert str(frame["x"].dtype) == "Int64"


def test_all_null_datetime_boolean_and_nonfinite_donors():
    frame = pd.DataFrame({
        "number": [np.nan, np.nan],
        "text": pd.Series([None, None], dtype="string"),
        "date": pd.to_datetime([None, None]),
        "flag": pd.Series([True, None], dtype="boolean"),
        "bad_number": [np.inf, np.nan],
    })
    cleaned = impute_missing_values(frame, AppConfig())
    pd.testing.assert_frame_equal(frame, cleaned)


def test_invalid_categorical_override_is_actionable():
    config = AppConfig.model_validate({"overrides": {"label": {"method": "mean"}}})
    with pytest.raises(ValueError, match="label.*categorical.*mode or skip"):
        impute_missing_values(pd.DataFrame({"label": pd.Series(["a", None], dtype="string")}), config)


def test_pipeline_honors_config_and_override():
    config = AppConfig.model_validate({
        "cleaning": {"duplicates": {"enabled": False}, "text_columns": ["label"]},
        "overrides": {"x": {"method": "mean"}},
        "validation_rules": {"x": {"max": 2}},
    })
    frame = pd.DataFrame({"x": [1., 5., np.nan, 1.], "label": [" a ", "b", " ", " a "]})
    results = run_pipeline(frame, config)
    assert len(results["cleaned_data"]) == 4
    assert results["cleaned_data"].loc[2, "x"] == pytest.approx(7 / 3)
    assert results["cleaned_data"].loc[2, "label"] == "a"
    assert results["cleaned_duplicates"]["duplicate_count"] == 1
    summary = create_summary(results)
    assert summary.loc["Invalid Values", "Before"] == 1
    assert summary.loc["Invalid Values", "After"] == 2
    assert results["actions"].loc[results["actions"]["action"].eq("Blank text made missing"), "count"].sum() == 1


def test_pipeline_can_disable_imputation():
    config = AppConfig.model_validate({"cleaning": {"missing_values": {"enabled": False}}})
    frame = pd.DataFrame({"x": [1., np.nan]})
    results = run_pipeline(frame, config)
    pd.testing.assert_frame_equal(results["cleaned_data"], frame)


def test_pipeline_uses_declared_date_columns_and_format():
    config = AppConfig.model_validate({
        "cleaning": {"date_columns": ["sale_day"], "date_format": "%d/%m/%Y"},
    })
    frame = pd.DataFrame({"sale_day": ["02/01/2025", "bad"], "date": ["unchanged", "unchanged"]})
    results = run_pipeline(frame, config)
    assert results["cleaned_data"].loc[0, "sale_day"] == pd.Timestamp("2025-01-02", tz="UTC")
    assert pd.isna(results["cleaned_data"].loc[1, "sale_day"])
    assert results["cleaned_data"]["date"].tolist() == frame["date"].tolist()
    assert create_summary(results).loc["Invalid Dates", "Before"] == 1


def test_categorical_mode_fill_preserves_categories():
    frame = pd.DataFrame({"label": pd.Categorical(["a", "a", None])})
    cleaned = impute_missing_values(frame, AppConfig())
    assert cleaned["label"].tolist() == ["a", "a", "a"]
    assert isinstance(cleaned["label"].dtype, pd.CategoricalDtype)


def test_sample_outcomes_and_unresolved_business_values(sample_df, sample_config):
    results = run_pipeline(sample_df, sample_config)
    summary = create_summary(results)
    assert summary["Before"].tolist() == [20, 10, 3, 1]
    assert summary["After"].tolist() == [1, 0, 3, 0]
    cleaned = results["cleaned_data"]
    assert len(cleaned) == 1000
    assert cleaned.loc[5, "quantity"] == -3
    assert cleaned.loc[15, "revenue"] == -500
    assert cleaned.loc[25, "region"] == "Unknown Region"
    assert pd.isna(cleaned.loc[35, "date"])
    assert cleaned["revenue"].isna().sum() == 0
    median = sample_df.drop_duplicates()["revenue"].median()
    assert cleaned.loc[sample_df.iloc[:1000]["revenue"].isna(), "revenue"].eq(median).all()
    assert results["actions"].loc[results["actions"]["action"].eq("Missing values imputed"), "count"].sum() == 20


@pytest.mark.parametrize("content", [
    {"unknown": True},
    {"cleaning": {"duplicates": {"enabld": False}}},
    {"cleaning": {"outliers": {"enabled": True}}},
    {"cleaning": {"missing_values": {"categorical": {"method": "median"}}}},
    {"validation_rules": {"x": {"minimum": 0}}},
    {"validation_rules": {"x": {"min": 10, "max": 1}}},
    {"validation_rules": {"x": {}}},
    {"cleaning": {"date_columns": ["x"], "text_columns": ["x"]}},
    {"cleaning": {"date_format": "mixed"}},
])
def test_invalid_config_rejected(content):
    with pytest.raises(ValidationError):
        AppConfig.model_validate(content)


def test_empty_yaml_is_error_and_example_is_valid(tmp_path):
    path = tmp_path / "empty.yaml"
    path.write_text("", encoding="utf-8")
    with pytest.raises(ValidationError):
        load_config(path)
    root = Path(__file__).resolve().parents[1]
    assert load_config(root / "config/example.yaml") == load_config(root / "config/default.yaml")


def test_duplicate_columns_rejected():
    with pytest.raises(ValueError, match="unique string names"):
        run_pipeline(pd.DataFrame([[1, 2]], columns=["x", "x"]), AppConfig())
