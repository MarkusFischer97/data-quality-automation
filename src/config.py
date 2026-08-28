from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field


class NumericalMissingConfig(BaseModel):
    method: Literal["mean", "median", "mode"] = "median"


class CategoricalMissingConfig(BaseModel):
    method: Literal["mean", "median", "mode"] = "mode"


class MissingValuesConfig(BaseModel):
    enabled: bool = True
    numerical: NumericalMissingConfig = NumericalMissingConfig()
    categorical: CategoricalMissingConfig = CategoricalMissingConfig()


class ColumnMissingOverride(BaseModel):
    method: Literal["mean", "median", "mode"]

class DuplicatesConfig(BaseModel):
    enabled: bool = True


class EmptyDataConfig(BaseModel):
    enabled: bool = False


class OutliersConfig(BaseModel):
    enabled: bool = False
    method: Literal["winsorize"] = "winsorize"
    percentile: float = Field(default=0.99, gt=0, lt=1)


class CleaningConfig(BaseModel):
    duplicates: DuplicatesConfig = DuplicatesConfig()
    missing_values: MissingValuesConfig = MissingValuesConfig()
    empty_rows: EmptyDataConfig = EmptyDataConfig()
    empty_columns: EmptyDataConfig = EmptyDataConfig()
    outliers: OutliersConfig = OutliersConfig()


class AppConfig(BaseModel):
    cleaning: CleaningConfig = CleaningConfig()
    overrides: dict[str, ColumnMissingOverride] = {}


def load_config(config_path):
    """Load and validate a YAML configuration file."""

    path = Path(config_path)

    with open(path, "r", encoding="utf-8") as file:
        config_data = yaml.safe_load(file)

    return AppConfig.model_validate(config_data)


def get_missing_value_method(config, column, data_type):
    """Return the effective missing-value method for a column."""

    if column in config.overrides:
        return config.overrides[column].method

    if data_type == "numerical":
        return config.cleaning.missing_values.numerical.method

    if data_type == "categorical":
        return config.cleaning.missing_values.categorical.method

    return None