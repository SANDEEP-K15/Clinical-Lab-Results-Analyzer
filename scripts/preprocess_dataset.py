"""Preprocess Kaggle Laboratory Test Results – Anonymized Dataset.

Source: https://www.kaggle.com/datasets/pinuto/laboratory-test-results-anonymized-dataset
File: lab_test_results_public.csv
"""

import json
import re
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent
KAGGLE_DIR = PROJECT_ROOT / "data" / "kaggle"
RAW_FILE = KAGGLE_DIR / "lab_test_results_public.csv"
PROCESSED_FILE = KAGGLE_DIR / "processed_laboratory_results.csv"
SAMPLE_FILE = PROJECT_ROOT / "test_data" / "kaggle_sample.csv"
ALIAS_FILE = PROJECT_ROOT / "backend" / "data" / "test_name_aliases.json"
DATASET_URL = "https://www.kaggle.com/datasets/pinuto/laboratory-test-results-anonymized-dataset"

# Map Kaggle test names to application reference range keys
KAGGLE_TO_APP_ALIASES = {
    "hemoglobin": "hemoglobin",
    "lökosit": "wbc",
    "trombosit": "platelet count",
    "glukoz (strip)": None,
    "glikozile hemoglobin (hba1c)": None,
}

# Unit conversions: (from_unit_pattern, to_unit, multiplier)
UNIT_CONVERSIONS = {
    "wbc": [("10^3/ul", "cells/uL", 1000), ("10^3/µl", "cells/uL", 1000)],
    "platelet count": [("10^3/ul", "cells/uL", 1000), ("10^3/µl", "cells/uL", 1000)],
}


def normalize_test_name(name: str) -> str:
    if not isinstance(name, str):
        return ""
    normalized = name.strip().lower()
    return re.sub(r"\s+", " ", normalized)


def normalize_unit(unit: str) -> str:
    return unit.strip().lower().replace("µ", "u")


def preprocess(input_path: Path | None = None, output_path: Path | None = None) -> pd.DataFrame:
    input_file = input_path or RAW_FILE
    output_file = output_path or PROCESSED_FILE

    if not input_file.exists():
        print(f"Dataset not found at: {input_file}")
        print(f"\nDownload from: {DATASET_URL}")
        print("Run: python scripts/download_dataset.py")
        print("Or manually place lab_test_results_public.csv in data/kaggle/")
        sys.exit(1)

    print(f"Loading Kaggle dataset from {input_file}")
    df = pd.read_csv(input_file)
    print(f"Original shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")

    processed = pd.DataFrame()
    processed["date"] = df["Date"]
    processed["test_name"] = df["Test_Name"].apply(normalize_test_name)
    processed["original_test_name"] = df["Test_Name"]
    processed["value"] = pd.to_numeric(df["Result"], errors="coerce")
    processed["unit"] = df["Unit"].astype(str).str.strip()
    processed["reference_range"] = df["Reference_Range"]
    processed["status"] = df["Status"]
    processed["min_reference"] = pd.to_numeric(df["Min_Reference"], errors="coerce")
    processed["max_reference"] = pd.to_numeric(df["Max_Reference"], errors="coerce")
    processed["comment"] = df["Comment"]
    processed["recommended_followup"] = df["Recommended_Followup"]

    processed["app_test_key"] = processed["test_name"].map(
        lambda n: KAGGLE_TO_APP_ALIASES.get(n)
    )
    processed["is_numeric"] = processed["value"].notna()

    before = len(processed)
    processed = processed[processed["test_name"] != ""]
    after = len(processed)

    print(f"\nDataset inspection:")
    print(f"  Total rows: {after}")
    print(f"  Numeric results: {processed['is_numeric'].sum()}")
    print(f"  Unique tests: {processed['test_name'].nunique()}")
    print(f"  Mappable to app reference DB: {processed['app_test_key'].notna().sum()}")

    print(f"\nTop tests by frequency:")
    try:
        print(processed["test_name"].value_counts().head(10).to_string())
    except UnicodeEncodeError:
        print("(test names contain non-ASCII characters)")

    print(f"\nStatus distribution:")
    try:
        print(processed["status"].value_counts().to_string())
    except UnicodeEncodeError:
        print(processed["status"].value_counts().to_dict())

    output_file.parent.mkdir(parents=True, exist_ok=True)
    processed.to_csv(output_file, index=False)
    print(f"\nSaved processed dataset to {output_file}")

    _export_sample_csv(processed)
    _export_aliases(processed)

    summary = {
        "source_url": DATASET_URL,
        "source_file": str(input_file.name),
        "total_rows": int(after),
        "numeric_rows": int(processed["is_numeric"].sum()),
        "unique_tests": int(processed["test_name"].nunique()),
        "mappable_tests": int(processed["app_test_key"].notna().sum()),
        "status_counts": processed["status"].value_counts().to_dict(),
    }
    summary_path = KAGGLE_DIR / "dataset_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"Saved dataset summary to {summary_path}")

    return processed


def _export_sample_csv(processed: pd.DataFrame) -> None:
    """Export numeric Kaggle rows mappable to app reference tests."""
    mappable = processed[
        processed["app_test_key"].notna() & processed["is_numeric"]
    ].copy()

    sample_rows = []
    for _, row in mappable.iterrows():
        app_key = row["app_test_key"]
        value = row["value"]
        unit = row["unit"]

        unit_norm = normalize_unit(unit)
        converted_value = value
        converted_unit = unit

        for conv_unit, to_unit, mult in UNIT_CONVERSIONS.get(app_key, []):
            if unit_norm == conv_unit:
                converted_value = value * mult
                converted_unit = to_unit
                break

        display_name = {
            "hemoglobin": "Hemoglobin",
            "wbc": "WBC",
            "platelet count": "Platelet Count",
        }.get(app_key, row["original_test_name"])

        sample_rows.append({
            "test_name": display_name,
            "value": converted_value,
            "unit": converted_unit,
        })

    if sample_rows:
        sample_df = pd.DataFrame(sample_rows)
        SAMPLE_FILE.parent.mkdir(parents=True, exist_ok=True)
        sample_df.to_csv(SAMPLE_FILE, index=False)
        print(f"Exported {len(sample_rows)} mappable rows to {SAMPLE_FILE}")


def _export_aliases(processed: pd.DataFrame) -> None:
    """Build test name alias map from Kaggle dataset for reference lookup."""
    aliases = dict(KAGGLE_TO_APP_ALIASES)

    for name in processed["test_name"].unique():
        if name not in aliases:
            aliases[name] = None

    ALIAS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(ALIAS_FILE, "w", encoding="utf-8") as f:
        json.dump(aliases, f, indent=2, ensure_ascii=False)
    print(f"Saved test name aliases to {ALIAS_FILE}")


if __name__ == "__main__":
    preprocess()
