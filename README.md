# Data Quality Automation

A small Python pipeline that turns recurring CSV data-quality review into a reproducible workflow: **profile, validate, clean deliberately, and explain the results**.

The bundled synthetic sales export contains missing revenue, duplicate records, negative business values, an unknown region, and an unusable date. The pipeline produces a cleaned CSV and an Excel report showing what changed and what still needs investigation.

## Example results

Using the bundled dataset and configuration:

| Measure | Before | After |
| --- | ---: | ---: |
| Rows | 1,010 | 1,000 |
| Missing cells | 20 | 1 |
| Extra duplicate rows | 10 | 0 |
| Business-rule violations | 3 | 3 |
| Nonmissing unparseable dates | 1 | 0 |

Twenty missing revenue values are filled with the deduplicated dataset's median, **504.00**. The unusable date becomes a missing timestamp. Negative quantity, negative revenue, and the unknown region remain flagged.

See [the example analysis](docs/example-results.md) for the interpretation and record-level examples.

## Workflow and architecture

```text
CSV + validated YAML
        |
Before checks and descriptive profiles
        |
Exact duplicate removal -> date parsing -> text trimming -> imputation
        |
After checks and descriptive profiles
        |
Excel report + cleaned CSV + console summary
```

The implementation uses pandas DataFrames and small functions:

- **Configuration:** Pydantic validates YAML settings and rejects unknown keys.
- **Checks:** missing cells, exact duplicates, observed dtypes, min/max/allowed rules, numeric type failures, and date parsing failures.
- **Cleaning:** configurable deduplication, declared date/text columns, mean/median/mode numeric imputation, categorical mode, and column-level overrides.
- **Profiling:** dataset dimensions and memory usage, numeric descriptive statistics, categorical counts/uniques/modes.
- **Reporting:** explicit before/after tables, cleaning actions, definitions, effective configuration, and readable Excel formatting.

There is no composite quality score or automatic business-value correction.

## Quickstart

**Supported and tested Python version: 3.13.** Run commands from the repository root.

```bash
git clone https://github.com/MarkusFischer97/data-quality-automation.git
cd data-quality-automation
python -m venv .venv
```

Activate the environment:

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

```bash
# macOS / Linux
source .venv/bin/activate
```

Install and run:

```bash
python -m pip install -r requirements.txt
python main.py
```

The committed sample is ready to use. Regenerate it deterministically if needed:

```bash
python generate_sample_data.py
```

Output directories are created automatically. Defaults write:

- `reports/data_quality_report.xlsx`
- `reports/cleaned_data.csv`

These generated files are ignored by Git. Existing output files are replaced on another run; input and configuration paths cannot be used as output paths.

## CLI

```bash
python main.py --input data/sample_data.csv --config config/example.yaml --report reports/data_quality_report.xlsx --cleaned-output reports/cleaned_data.csv
python main.py --help
```

Explicit relative paths use the current working directory. Default paths resolve relative to the repository, so invoking its `main.py` from another directory also works.

The command prints before/after counts, rows, coercions, imputed cells, warnings, and output paths. Invalid input/configuration or write failures return exit code 2 with a concise error. Remaining data-quality violations are reported without making the run fail.

## Configuration

Both [default.yaml](config/default.yaml) and [example.yaml](config/example.yaml) work with the sample. Copy and adapt the column names and rules for another CSV.

```yaml
cleaning:
  duplicates:
    enabled: true
  missing_values:
    enabled: true
    numerical:
      method: median          # mean, median, or mode
    categorical:
      method: mode            # categorical imputation supports mode only
  date_columns: [date]
  text_columns: [product, region]
  date_format: ISO8601         # or an explicit format such as "%d/%m/%Y"

overrides:
  customer_id:
    method: skip              # protect identifiers; mean/median/mode also supported

validation_rules:
  quantity:
    min: 1
  revenue:
    min: 0
  region:
    allowed: [North, South, East, West]
```

Rules also support `max`. Overrides select an imputation method, not a replacement constant; mean/median overrides require a numeric column. Set `missing_values.enabled: false` to disable imputation.

Omitted fields use generic model defaults: duplicate removal and imputation enabled, no date/text columns, no validation rules. An empty YAML file is rejected; `{}` is valid. Unknown keys, unsupported methods, conflicting date/text columns, and inverted numeric bounds are rejected.

For programmatic use, pass configuration explicitly:

```python
import pandas as pd
from src.config import load_config
from src.pipeline import run_pipeline

results = run_pipeline(pd.read_csv("data/sample_data.csv"),
                       load_config("config/example.yaml"))
cleaned = results["cleaned_data"]
```

## Analytical decisions and metric definitions

- **Business values remain observed values.** Range/category failures are flagged, never replaced with invented quantities, revenues, or regions.
- **Date coercion is information loss, not recovery.** Nonmissing values that fail the declared format become `NaT`. Date checks and cleaning use the same parser. ISO 8601 is the default; mixed-format inference is unsupported. Parsed dates are UTC, naive dates are assumed UTC, and numeric epoch inputs are unsupported.
- **Imputation is a choice.** It uses finite observed numeric or nonmissing categorical donors after deduplication and normalization. Flagged finite business values remain in the donor population. Review validity before using cleaned output for analysis: imputation can change distributions and introduce bias.
- **Identifiers need protection.** The sample explicitly skips customer IDs. Datetimes, booleans, and columns with no eligible donors remain unimputed. Fractional fills promote nullable integers to nullable floats. Mode ties use pandas' first mode.
- **Text normalization is narrow.** Only configured columns are trimmed; case and business categories are preserved. Blank/whitespace-only text becomes missing before imputation.
- **Duplicate count means extra exact rows.** The first occurrence is retained. Removal happens before normalization/imputation; transformations can create new duplicates, which remain visible in the after check.
- **Missingness is separate from validity.** Nulls count as missing cells, not rule/date violations. Missing percentages use the stage's row count.
- **Rule violations are not distinct bad records.** A row can fail several rules. Numeric strings are compared numerically without changing their source values. Non-numeric/infinite values receive one `numeric_type` violation per range-checked column and are excluded from min/max denominators. Each rule lists its evaluated-value count.
- **Absent columns are unchecked.** Missing configured columns appear in the workbook and console warnings; zero violations do not imply a passed check. Empty datasets are reportable with a warning. Zero-denominator percentages are represented as zero alongside counts and assessment status.
- **Dtypes are descriptive.** They show pandas' observed types, not validation against an expected schema.

## Outputs

The report opens with the summary and dataset overview. It includes cleaning actions, configured-column status, and before/after missing values, duplicates, invalid values, invalid dates, and dtypes. Numeric and categorical profiles cover both stages.

Notes define the measures. Effective configuration and CLI source paths make the run understandable. Headers, filters, frozen rows, widths, and numerical formats keep detail tables readable. Percentage fields contain values on a 0?100 scale.

The cleaned CSV preserves all columns and remaining business violations. Timestamps serialize with UTC offsets; missing values serialize as empty fields. CSV does not preserve pandas dtype metadata?consult the workbook for the in-memory types.

## Project structure

```text
config/                  Default and example YAML
data/sample_data.csv     Committed synthetic input
docs/example-results.md  Worked example and interpretation
src/
  config.py              Validated settings
  checks.py              Quality measures and shared date parser
  cleaning.py            Conservative transformations
  profiling.py           Descriptive profiles
  pipeline.py            Workflow orchestration
  reporting.py           Excel tables and formatting
tests/                   Unit, regression, CLI, and end-to-end tests
.github/workflows/       Single-version test CI
generate_sample_data.py  Deterministic sample generator
main.py                  argparse entry point
requirements.txt         Pinned direct runtime dependencies
requirements-dev.txt     Runtime plus pytest
pyproject.toml           pytest configuration (not package metadata)
```

## Tests and CI

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Tests check actual counts and values, configuration switches/overrides, untouched source data, empty and single-type datasets, missing columns, numeric/date parsing, nullable integer fills, literal Excel text, workbook formatting, and generator reproducibility.

The end-to-end test runs the CLI with the sample config and reads both outputs. A fresh-checkout test runs without an existing report directory. GitHub Actions installs dependencies and runs the suite on Python 3.13 for pushes and pull requests.

## Scope and limitations

Portfolio Ready v1 is a local, in-memory CSV workflow. It uses pandas' default CSV parsing and missing-value recognition. Excel input, large-file streaming, cross-field constraints, expected-schema enforcement, and record-level issue exports are outside this release.

The bundled sales data is synthetic, not a financial research dataset. Profiles include numeric identifiers and invalid observed values; interpreting those statistics requires domain judgment. Cleaned output is a review artifact and preparation step, not a guarantee that data is suitable for modeling.
