"""Preprocess Kaggle Laboratory Test Results dataset."""

import json
import re
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent
KAGGLE_DIR = PROJECT_ROOT / "data" / "kaggle"
RAW_FILE = KAGGLE_DIR / "laboratory_test_results.csv"
PROCESSED_FILE = KAGGLE_DIR / "processed_laboratory_results.csv"


def normalize_test_name(name: str) -> str:
    if not isinstance(name, str):
        return ""
    normalized = name.strip().lower()
    return re.sub(r"\s+", " ", normalized)


def preprocess(input_path: Path | None = None, output_path: Path | None = None) -> pd.DataFrame:
    input_file = input_path or RAW_FILE
    output_file = output_path or PROCESSED_FILE

    if not input_file.exists():
        print(f"Dataset not found at: {input_file}")
        print("\nTo download the Kaggle dataset:")
        print("1. Go to https://www.kaggle.com/datasets")
        print("2. Search for 'Laboratory Test Results – Anonymized Dataset'")
        print("3. Download and place as: data/kaggle/laboratory_test_results.csv")
        sys.exit(1)

    print(f"Loading dataset from {input_file}")
    df = pd.read_csv(input_file)
    print(f"Original shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")

    name_col = next((c for c in df.columns if "test" in c.lower() and "name" in c.lower()), None)
    value_col = next((c for c in df.columns if c.lower() in ("value", "result", "test_value")), None)
    unit_col = next((c for c in df.columns if "unit" in c.lower()), None)

    if not all([name_col, value_col]):
        print("Could not identify required columns. Available:", list(df.columns))
        print("Expected columns similar to: test_name, value, unit")
        sys.exit(1)

    processed = pd.DataFrame()
    processed["test_name"] = df[name_col].apply(normalize_test_name)
    processed["value"] = pd.to_numeric(df[value_col], errors="coerce")
    processed["unit"] = df[unit_col].astype(str).str.strip() if unit_col else ""

    before = len(processed)
    processed = processed.dropna(subset=["test_name", "value"])
    processed = processed[processed["test_name"] != ""]
    after = len(processed)

    print(f"Removed {before - after} invalid rows")
    print(f"Processed shape: {processed.shape}")
    print(f"Unique tests: {processed['test_name'].nunique()}")
    print(processed["test_name"].value_counts().head(10))

    output_file.parent.mkdir(parents=True, exist_ok=True)
    processed.to_csv(output_file, index=False)
    print(f"Saved processed dataset to {output_file}")
    return processed


if __name__ == "__main__":
    preprocess()
