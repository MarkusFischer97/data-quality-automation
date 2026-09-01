# Data Quality Automation

A Python-based data quality pipeline for automatically profiling, validating, cleaning, and reporting on CSV and Excel datasets.

The project demonstrates how recurring data-quality checks can be turned into a structured and repeatable workflow instead of being performed manually for every new dataset.

---

## Why this project?

Data quality issues are common in recurring datasets such as operational exports, financial reports, and business data.

Typical problems include:

- missing values
- duplicate records
- invalid values
- inconsistent text data
- invalid dates
- unexpected data types

Manually identifying and documenting these issues is repetitive and can lead to inconsistent results.

This project automates these steps and produces a structured data-quality report.

---

## Workflow

```text
Input Dataset
      │
      ▼
Data Profiling
      │
      ▼
Quality Checks
      │
      ▼
Data Cleaning
      │
      ▼
Quality Checks
      │
      ▼
Before / After Comparison
      │
      ▼
Excel Quality Report
```

The pipeline separates **data inspection**, **validation**, **cleaning**, and **reporting** so that each step can be extended independently.

---

## Features

### Data Profiling

The pipeline provides basic dataset profiling, including:

- row and column counts
- duplicate records
- memory usage
- numerical column statistics
- missing values
- unique values
- common categorical values

### Data Quality Checks

The current implementation checks for:

- missing values
- duplicate rows
- detected data types
- invalid values based on configurable rules
- invalid date values

Validation rules can define constraints such as minimum and maximum values or allowed categorical values.

### Data Cleaning

The cleaning pipeline currently supports:

- duplicate removal
- date conversion
- text standardization
- missing-value imputation
- configurable mean, median, and mode imputation

Cleaning behaviour can be controlled through the project configuration.

### Reporting

The pipeline generates a structured Excel report containing the results of the quality checks.

The report includes sections for:

- summary
- missing values
- duplicates
- invalid values
- invalid dates
- data types
- before/after results

This makes the output easier to review than raw console output alone.

---

## Example Use Case

The repository contains a synthetic dataset with deliberately introduced data-quality issues.

The example workflow is:

```text
Synthetic / External Dataset
          │
          ▼
      Profiling
          │
          ▼
   Quality Assessment
          │
          ▼
       Cleaning
          │
          ▼
   Quality Assessment
          │
          ▼
     Quality Report
```

The synthetic data generator makes the example reproducible and allows the pipeline to be tested against known quality problems.

---

## Configuration

The pipeline uses YAML configuration files to define processing behaviour and validation rules.

For example, validation rules can define constraints such as:

```yaml
quantity:
  min: 1

revenue:
  min: 0

region:
  allowed:
    - North
    - South
    - East
    - West
```

This makes the validation logic configurable instead of requiring changes to the Python code for every dataset.

---

## Project Structure

```text
data-quality-automation/
│
├── config/
│   ├── default.yaml
│   └── example.yaml
│
├── data/
│   └── sample_data.csv
│
├── src/
│   ├── checks.py
│   ├── cleaning.py
│   ├── config.py
│   ├── pipeline.py
│   ├── profiling.py
│   ├── reporting.py
│   └── rules.py
│
├── tests/
│
├── generate_sample_data.py
├── main.py
├── pyproject.toml
└── requirements.txt
```

---

## Installation

Clone the repository and install the required dependencies:

```bash
git clone https://github.com/MarkusFischer97/data-quality-automation.git
cd data-quality-automation

pip install -r requirements.txt
```

For development, the project can also be installed using the configuration provided in `pyproject.toml`.

---

## Usage

Generate the synthetic sample dataset:

```bash
python generate_sample_data.py
```

Run the data-quality pipeline:

```bash
python main.py
```

The pipeline processes the configured dataset, performs the quality checks and cleaning steps, and generates the corresponding report.

---

## Technologies

- Python
- pandas
- PyYAML
- openpyxl
- pytest
- YAML-based configuration

---

## Future Improvements

The current project provides the foundation for a more comprehensive data-quality framework.

Potential future improvements include:

- additional data-quality dimensions
- configurable quality scoring
- improved validation and consistency checks
- stronger test coverage
- support for additional input formats
- statistical outlier and anomaly detection
- automated execution and monitoring
- richer reporting and visualisation

These improvements are intentionally kept separate from the current core pipeline.

---

## Project Status

The current version is a functional portfolio project demonstrating automated data profiling, rule-based validation, data cleaning, and quality reporting.

The project is designed to be extended as additional data-quality and automation requirements are explored.