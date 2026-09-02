# Kaggle Dataset: Laboratory Test Results – Anonymized Dataset

**Source:** https://www.kaggle.com/datasets/pinuto/laboratory-test-results-anonymized-dataset

**Author:** pinuto  
**License:** CC-BY-SA-4.0  
**File:** `lab_test_results_public.csv`

## Dataset Columns

| Column | Description |
|--------|-------------|
| Date | Test date (YYYY-MM-DD) |
| Test_Name | Laboratory test name |
| Result | Measured value (numeric or qualitative) |
| Unit | Measurement unit |
| Reference_Range | Official normal range |
| Status | Normal / High / Low indicator |
| Comment | Short medical interpretation |
| Min_Reference | Lower bound of reference range |
| Max_Reference | Upper bound of reference range |
| Unit_Description | Expanded unit description |
| Recommended_Followup | Suggested monitoring or action |

## Download

### Option 1: Automated script
```bash
cd backend
venv\Scripts\activate
pip install kaggle
python ../scripts/download_dataset.py
```

Requires [Kaggle API credentials](https://www.kaggle.com/docs/api) in `~/.kaggle/kaggle.json`.

### Option 2: Manual download
1. Visit the [dataset page](https://www.kaggle.com/datasets/pinuto/laboratory-test-results-anonymized-dataset)
2. Click **Download**
3. Extract `lab_test_results_public.csv` to this folder

## Preprocess

```bash
python scripts/preprocess_dataset.py
```

This produces:
- `processed_laboratory_results.csv` — cleaned, normalized data
- `dataset_summary.json` — inspection statistics
- `backend/data/test_name_aliases.json` — test name mappings for the app
- `test_data/kaggle_sample.csv` — mappable rows for demo/analysis

## Integration in This Project

The Kaggle dataset is used for:
- **Data inspection** — column analysis and status distribution
- **Test name normalization** — aliases (e.g., `Lökosit` → WBC, `Trombosit` → Platelet Count)
- **Unit conversion** — Kaggle `10^3/uL` → app `cells/uL` for WBC and platelets
- **Demo sample** — `test_data/kaggle_sample.csv` extracted from real dataset rows

Reference ranges for classification remain controlled by `backend/data/reference_ranges.json` (not the Kaggle dataset ranges).

## API Endpoints

- `GET /dataset/info` — dataset metadata and summary
- `GET /dataset/tests` — unique tests from Kaggle data
- `GET /dataset/sample` — mappable lab results from Kaggle
