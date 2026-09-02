"""Kaggle dataset integration service.

Loads and inspects the Laboratory Test Results – Anonymized Dataset from:
https://www.kaggle.com/datasets/pinuto/laboratory-test-results-anonymized-dataset
"""

import json
import logging
from pathlib import Path

import pandas as pd

from utils.validators import normalize_test_name

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.parent
KAGGLE_DIR = PROJECT_ROOT / "data" / "kaggle"
PROCESSED_FILE = KAGGLE_DIR / "processed_laboratory_results.csv"
RAW_FILE = KAGGLE_DIR / "lab_test_results_public.csv"
ALIAS_FILE = Path(__file__).parent.parent / "data" / "test_name_aliases.json"
SUMMARY_FILE = KAGGLE_DIR / "dataset_summary.json"
DATASET_URL = "https://www.kaggle.com/datasets/pinuto/laboratory-test-results-anonymized-dataset"

UNIT_CONVERSIONS = {
    "wbc": {"10^3/ul": ("cells/uL", 1000), "10^3/µl": ("cells/uL", 1000)},
    "platelet count": {"10^3/ul": ("cells/uL", 1000), "10^3/µl": ("cells/uL", 1000)},
}


class DatasetService:
    def __init__(self):
        self._df: pd.DataFrame | None = None
        self._aliases: dict = {}
        self._load_aliases()

    def _load_aliases(self) -> None:
        if ALIAS_FILE.exists():
            with open(ALIAS_FILE, encoding="utf-8") as f:
                self._aliases = json.load(f)
            logger.info("Loaded %d test name aliases from Kaggle dataset", len(self._aliases))

    def _load_dataframe(self) -> pd.DataFrame:
        if self._df is not None:
            return self._df

        if PROCESSED_FILE.exists():
            self._df = pd.read_csv(PROCESSED_FILE)
        elif RAW_FILE.exists():
            logger.warning("Processed file missing; run: python scripts/preprocess_dataset.py")
            self._df = pd.read_csv(RAW_FILE)
            self._df["test_name"] = self._df["Test_Name"].str.strip().str.lower()
            self._df["is_numeric"] = pd.to_numeric(self._df["Result"], errors="coerce").notna()
        else:
            self._df = pd.DataFrame()

        return self._df

    def resolve_test_alias(self, test_name: str) -> str | None:
        """Resolve a test name to an application reference key using Kaggle-derived aliases."""
        normalized = normalize_test_name(test_name)
        if normalized in self._aliases and self._aliases[normalized]:
            return self._aliases[normalized]
        return normalized if normalized in self._aliases else None

    def convert_unit_if_needed(self, app_key: str, value: float, unit: str) -> tuple[float, str]:
        """Explicit unit conversion for Kaggle-compatible units."""
        unit_norm = unit.strip().lower().replace("µ", "u")
        conversions = UNIT_CONVERSIONS.get(app_key, {})
        if unit_norm in conversions:
            to_unit, multiplier = conversions[unit_norm]
            return value * multiplier, to_unit
        return value, unit

    def get_dataset_info(self) -> dict:
        """Return dataset metadata and inspection summary."""
        if SUMMARY_FILE.exists():
            with open(SUMMARY_FILE, encoding="utf-8") as f:
                summary = json.load(f)
            summary["available"] = True
            return summary

        df = self._load_dataframe()
        if df.empty:
            return {
                "available": False,
                "source_url": DATASET_URL,
                "message": "Kaggle dataset not found. Run: python scripts/download_dataset.py",
            }

        return {
            "available": True,
            "source_url": DATASET_URL,
            "source_file": "lab_test_results_public.csv",
            "total_rows": len(df),
            "unique_tests": int(df["test_name"].nunique()) if "test_name" in df.columns else 0,
            "numeric_rows": int(df["is_numeric"].sum()) if "is_numeric" in df.columns else 0,
        }

    def get_known_tests(self) -> list[dict]:
        """Return unique tests discovered in the Kaggle dataset."""
        df = self._load_dataframe()
        if df.empty:
            return []

        tests = []
        for name in df["test_name"].unique():
            subset = df[df["test_name"] == name]
            tests.append({
                "test_name": name,
                "count": len(subset),
                "app_reference_key": self._aliases.get(name),
                "has_numeric_values": bool(subset["is_numeric"].any()) if "is_numeric" in subset.columns else False,
            })
        return sorted(tests, key=lambda t: t["count"], reverse=True)

    def get_sample_labs(self) -> list[dict]:
        """Return mappable numeric lab results from the Kaggle dataset."""
        df = self._load_dataframe()
        if df.empty or "app_test_key" not in df.columns:
            return []

        mappable = df[df["app_test_key"].notna() & df["is_numeric"]]
        labs = []
        for _, row in mappable.iterrows():
            app_key = row["app_test_key"]
            value, unit = self.convert_unit_if_needed(app_key, row["value"], row["unit"])
            display_name = {
                "hemoglobin": "Hemoglobin",
                "wbc": "WBC",
                "platelet count": "Platelet Count",
            }.get(app_key, row.get("original_test_name", row["test_name"]))
            labs.append({"test_name": display_name, "value": value, "unit": unit})
        return labs


dataset_service = DatasetService()
