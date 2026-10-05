"""Generate the deterministic bundled dataset without affecting global RNG state."""
from pathlib import Path

import numpy as np
import pandas as pd


def generate_sample_data(output_path=Path(__file__).resolve().parent / "data/sample_data.csv"):
    # Reproducibility
    rng = np.random.RandomState(42)

    # Output path
    output_path = Path(output_path)

    # Number of observations
    n = 1_000

    # Create base dataset
    df = pd.DataFrame(
        {
            "customer_id": np.arange(10001, 10001 + n),
            "date": pd.date_range("2025-01-01", periods=n, freq="D"),
            "product": rng.choice(
                ["Product A", "Product B", "Product C", "Product D"],
                size=n,
            ),
            "quantity": rng.randint(1, 11, size=n),
            "revenue": np.round(rng.uniform(20, 1_000, size=n), 2),
            "region": rng.choice(
                ["North", "South", "East", "West"],
                size=n,
            ),
        }
    )


    # ---------------------------------------------------------
    # Introduce data quality issues intentionally
    # ---------------------------------------------------------

    # Missing values
    df.loc[rng.choice(df.index, 20, replace=False), "revenue"] = np.nan

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
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    print(f"Created sample dataset: {output_path}")
    print(f"Shape: {df.shape}")
    return df


if __name__ == "__main__":
    generate_sample_data()
