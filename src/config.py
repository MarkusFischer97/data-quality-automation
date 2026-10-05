"""Validated settings for the implemented pipeline operations."""
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator


class Settings(BaseModel):
    model_config = ConfigDict(extra="forbid")


class NumericalMissingConfig(Settings):
    method: Literal["mean", "median", "mode"] = "median"


class CategoricalMissingConfig(Settings):
    method: Literal["mode"] = "mode"


class MissingValuesConfig(Settings):
    enabled: bool = True
    numerical: NumericalMissingConfig = Field(default_factory=NumericalMissingConfig)
    categorical: CategoricalMissingConfig = Field(default_factory=CategoricalMissingConfig)


class ColumnMissingOverride(Settings):
    method: Literal["mean", "median", "mode", "skip"]


class DuplicatesConfig(Settings):
    enabled: bool = True


class CleaningConfig(Settings):
    duplicates: DuplicatesConfig = Field(default_factory=DuplicatesConfig)
    missing_values: MissingValuesConfig = Field(default_factory=MissingValuesConfig)
    date_columns: list[str] = Field(default_factory=list)
    text_columns: list[str] = Field(default_factory=list)
    date_format: str = "ISO8601"

    @model_validator(mode="after")
    def validate_dates(self):
        if not self.date_format or self.date_format == "mixed":
            raise ValueError("Use ISO8601 or an explicit strftime date format; mixed inference is unsupported")
        if set(self.date_columns) & set(self.text_columns):
            raise ValueError("A column cannot be configured as both date and text")
        return self


class ValidationRule(Settings):
    min: float | None = Field(default=None, allow_inf_nan=False)
    max: float | None = Field(default=None, allow_inf_nan=False)
    allowed: list[str | int | float | bool] | None = None

    @model_validator(mode="after")
    def validate_bounds(self):
        if self.min is None and self.max is None and self.allowed is None:
            raise ValueError("Specify min, max, or allowed")
        if self.min is not None and self.max is not None and self.min > self.max:
            raise ValueError("min must not exceed max")
        return self


class AppConfig(Settings):
    cleaning: CleaningConfig = Field(default_factory=CleaningConfig)
    overrides: dict[str, ColumnMissingOverride] = Field(default_factory=dict)
    validation_rules: dict[str, ValidationRule] = Field(default_factory=dict)


def load_config(config_path: str | Path) -> AppConfig:
    """Load YAML; an empty file is an error, while {} uses generic defaults."""
    with Path(config_path).open(encoding="utf-8") as file:
        return AppConfig.model_validate(yaml.safe_load(file))


def get_missing_value_method(config, column, data_type):
    if column in config.overrides:
        return config.overrides[column].method
    if data_type == "numerical":
        return config.cleaning.missing_values.numerical.method
    if data_type == "categorical":
        return config.cleaning.missing_values.categorical.method
    return "skip"
