# Bundled example: what cleaning changes

Run from the repository root:

```bash
python main.py --input data/sample_data.csv --config config/example.yaml --report reports/data_quality_report.xlsx --cleaned-output reports/cleaned_data.csv
```

The input is a deterministic synthetic sales export with 1,010 rows and six columns. Ten rows are exact duplicates; 20 revenue cells are missing. The generator also introduces three business-rule violations and one unparseable date.

| Measure | Before | After | Meaning |
| --- | ---: | ---: | --- |
| Rows | 1,010 | 1,000 | Ten extra exact rows removed |
| Missing cells | 20 | 1 | Twenty revenues filled; one unusable date becomes missing |
| Extra duplicate rows | 10 | 0 | Whole-row equality, retaining the first occurrence |
| Rule violations | 3 | 3 | Observed invalid business values retained |
| Nonmissing unparseable dates | 1 | 0 | Coercion to missing, not date recovery |

## Follow specific records

The exported CSV has no pandas index; use customer IDs to locate these records.

| Customer ID | Issue | After cleaning |
| --- | --- | --- |
| 10006 | Quantity is -3; minimum is 1 | -3 remains and is flagged |
| 10016 | Revenue is -500; minimum is 0 | -500 remains and is flagged |
| 10026 | Region is Unknown Region | Category remains and is flagged |
| 10036 | Date is not_a_date | Date becomes missing |

The 20 missing revenues are filled with **504.00**, the median of the deduplicated, nonmissing revenue values. No text values require trimming in this particular sample; regression tests separately demonstrate trimming and blank categorical handling.

## Interpret the improvement carefully

The invalid-date count reaches zero because its value is now missing. The workbook's Cleaning Actions sheet records one date coercion, while the AFTER Missing Values table records one missing date among 1,000 rows (**0.10%**).

Revenue missingness falls from 20 / 1,010 (**1.98%**) to zero. That means the chosen imputation was applied; it does not establish that the filled revenues equal the unknown true values. The negative observed revenue is still included among finite imputation donors. A real analytical workflow should investigate it and assess imputation bias before modeling.

Rule totals count violations, not distinct rows. This sample happens to have three failures in separate records. Other datasets may have overlapping failures, additional numeric type failures, or absent configured columns.

## Review the deliverables

- **Summary / Dataset Overview:** before/after counts, units, assessment status, row counts, and memory in bytes.
- **Cleaning Actions:** duplicate removal, date coercion, trimming/blank conversion, and imputed-cell counts.
- **Detail and profile sheets:** both stages, per-rule denominators, observed types, descriptive statistics, and categorical modes.
- **Configured Columns / Notes / Run Configuration / Run Context:** which checks were possible, metric definitions, effective settings, and CLI source paths.
- **Cleaned CSV:** 1,000 rows, no missing revenue, one missing date, and the three unresolved business-rule violations.

No composite score is calculated. The results show which transformations happened and which issues require judgment.
