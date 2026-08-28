import pytest
from pydantic import ValidationError

from src.config import (
    load_config,
    get_missing_value_method,
)

def test_load_default_config():

    config = load_config("config/default.yaml")

    assert config.cleaning.duplicates.enabled is True
    assert config.cleaning.missing_values.enabled is True
    assert config.cleaning.missing_values.numerical.method == "median"
    assert config.cleaning.missing_values.categorical.method == "mode"
    assert config.cleaning.outliers.enabled is False
    assert config.cleaning.outliers.percentile == 0.99


def test_invalid_imputation_method(tmp_path):

    config_file = tmp_path / "invalid.yaml"

    config_file.write_text(
        """
        cleaning:
        missing_values:
            numerical:
            method: banana
        """,
                encoding="utf-8",
            )

    with pytest.raises(ValidationError):
        load_config(config_file)


def test_column_override(tmp_path):

    config_file = tmp_path / "override.yaml"

    config_file.write_text(
        """
cleaning:
  missing_values:
    numerical:
      method: median

overrides:
  revenue:
    method: mean
""",
        encoding="utf-8",
    )

    config = load_config(config_file)

    assert config.cleaning.missing_values.numerical.method == "median"
    assert config.overrides["revenue"].method == "mean"


def test_get_missing_value_method(tmp_path):

    config_file = tmp_path / "override.yaml"

    config_file.write_text(
        """
cleaning:
  missing_values:
    numerical:
      method: median
    categorical:
      method: mode

overrides:
  revenue:
    method: mean
""",
        encoding="utf-8",
    )

    config = load_config(config_file)

    assert get_missing_value_method(
        config,
        "revenue",
        "numerical",
    ) == "mean"

    assert get_missing_value_method(
        config,
        "quantity",
        "numerical",
    ) == "median"

    assert get_missing_value_method(
        config,
        "region",
        "categorical",
    ) == "mode"