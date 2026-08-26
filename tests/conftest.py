import pytest
import pandas as pd

@pytest.fixture
def sample_df():
    return pd.read_csv("data/sample_data.csv")