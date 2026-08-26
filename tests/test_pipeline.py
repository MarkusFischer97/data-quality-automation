from src.pipeline import run_pipeline


def test_run_pipeline(sample_df):

    result = run_pipeline(sample_df)

    assert "cleaned_data" in result
    assert "missing_values" in result
    assert "duplicates" in result
    assert "invalid_values" in result
    assert "dataset_profile" in result

    assert len(result["cleaned_data"]) == 1000
    assert result["cleaned_duplicates"]["duplicate_count"] == 0