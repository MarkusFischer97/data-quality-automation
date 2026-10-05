from src.pipeline import run_pipeline


def test_run_pipeline(sample_df, sample_config):

    result = run_pipeline(sample_df, sample_config)

    assert "cleaned_data" in result
    assert "missing_values" in result
    assert "duplicates" in result
    assert "invalid_values" in result
    assert "dataset_profile" in result

    assert "cleaned_missing_values" in result
    assert "cleaned_data_types" in result
    assert "cleaned_invalid_values" in result
    assert "cleaned_invalid_dates" in result

    assert len(result["cleaned_data"]) == 1000

    assert result["duplicates"]["duplicate_count"] == 10
    assert result["cleaned_duplicates"]["duplicate_count"] == 0

