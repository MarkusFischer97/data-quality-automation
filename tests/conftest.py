from pathlib import Path

import pandas as pd
import pytest

from src.config import load_config

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def sample_df():
    return pd.read_csv(ROOT / "data/sample_data.csv")


@pytest.fixture
def sample_config():
    return load_config(ROOT / "config/default.yaml")
