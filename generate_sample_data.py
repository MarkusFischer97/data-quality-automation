# generate_sample_data.py
from pathlib import Path

import numpy as np
import pandas as pd


# Reproducibility
np.random.seed(42)

# Output path
OUTPUT_PATH = Path("data/sample_data.csv")

# Number of observations
N = 1_000

# Create base dataset
df = pd.DataFrame(
    {
        "customer_id": np.arange(10001, 10001 + N),
        "date": pd.date_range("2025-01-01", periods=N, freq="D"),
        "product": np.random.choice(
            ["Product A", "Product B", "Product C", "Product D"],
            size=N,
        ),
        "quantity": np.random.randint(1, 11, size=N),
        "revenue": np.round(np.random.uniform(20, 1_000, size=N), 2),
        "region": np.random.choice(
            ["North", "South", "East", "West"],
            size=N,
        ),
    }
)


# ---------------------------------------------------------
# Introduce data quality issues intentionally
# ---------------------------------------------------------

# Missing values
df.loc[np.random.choice(df.index, 20, replace=False), "revenue"] = np.nan

# Duplicate rows
duplicates = df.sample(10, random_state=42)
df = pd.concat([df, duplicates], ignore_index=True)

# Invalid values
df.loc[5, "quantity"] = -3
df.loc[15, "revenue"] = -500

# Invalid category
df.loc[25, "region"] = "Unknown Region"

# Invalid date
df["date"] = df["date"].astype(object)
df.loc[35, "date"] = "not_a_date"

# Save dataset
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUTPUT_PATH, index=False)

print(f"Created sample dataset: {OUTPUT_PATH}")
print(f"Shape: {df.shape}")