"""Download Kaggle Laboratory Test Results dataset."""

import subprocess
import sys
from pathlib import Path

DATASET_SLUG = "pinuto/laboratory-test-results-anonymized-dataset"
PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "data" / "kaggle"


def download():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Downloading dataset: {DATASET_SLUG}")
    print(f"URL: https://www.kaggle.com/datasets/{DATASET_SLUG}")
    print(f"Output: {OUTPUT_DIR}")

    result = subprocess.run(
        [
            sys.executable, "-m", "kaggle", "datasets", "download",
            "-d", DATASET_SLUG,
            "-p", str(OUTPUT_DIR),
            "--unzip",
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print("Download failed. Ensure Kaggle API credentials are configured.")
        print("See: https://www.kaggle.com/docs/api")
        print(result.stderr)
        sys.exit(1)

    print(result.stdout)
    csv_file = OUTPUT_DIR / "lab_test_results_public.csv"
    if csv_file.exists():
        print(f"Dataset ready: {csv_file}")
    else:
        print("Warning: expected file lab_test_results_public.csv not found after download.")


if __name__ == "__main__":
    download()
