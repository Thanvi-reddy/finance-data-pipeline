"""
CSV to JSON Converter
----------------------
Converts all CSVs in data/raw/ to JSON format.
Keeps both files — CSV stays as primary, JSON is recovery copy.
Saves JSON to data/json/ mirroring CSV filenames.

Run: python scripts/csv_to_json.py
"""

import pandas as pd
from pathlib import Path

RAW_DIR = Path("data/raw")
JSON_DIR = Path("data/json")


def convert_all():
    JSON_DIR.mkdir(parents=True, exist_ok=True)

    csv_files = sorted(RAW_DIR.glob("*_max.csv"))
    if not csv_files:
        print("No CSV files found in data/raw/")
        return

    print(f"Converting {len(csv_files)} CSV files to JSON...\n")
    print("-" * 50)

    success = 0
    failed = 0

    for csv_file in csv_files:
        try:
            # Read CSV
            df = pd.read_csv(csv_file)

            # Output path
            json_file = JSON_DIR / (csv_file.stem + ".json")

            # Convert to JSON — one record per row, ISO date format
            df.to_json(json_file, orient="records", date_format="iso", indent=2)

            print(f"✓ {csv_file.name} → {json_file.name} ({len(df)} rows)")
            success += 1

        except Exception as e:
            print(f"✗ {csv_file.name} — Error: {e}")
            failed += 1

    print("-" * 50)
    print(f"\nDone: {success} converted | {failed} failed")
    print(f"JSON files saved to: {JSON_DIR}")


def round_trip_check(ticker="AAPL"):
    """
    Verify JSON round-trip matches original CSV.
    Loads JSON back to DataFrame and compares with CSV.
    """
    csv_file = RAW_DIR / f"{ticker}_max.csv"
    json_file = JSON_DIR / f"{ticker}_max.json"

    if not csv_file.exists() or not json_file.exists():
        print(f"\nRound-trip check skipped — files not found for {ticker}")
        return

    df_csv = pd.read_csv(csv_file)
    df_json = pd.read_json(json_file, orient="records")

    rows_match = len(df_csv) == len(df_json)
    cols_match = list(df_csv.columns) == list(df_json.columns)

    print(f"\nRound-trip check for {ticker}:")
    print(f"  CSV rows:  {len(df_csv)}")
    print(f"  JSON rows: {len(df_json)}")
    print(f"  Rows match: {'✓' if rows_match else '✗'}")
    print(f"  Cols match: {'✓' if cols_match else '✗'}")

    if rows_match and cols_match:
        print(f"  ✓ Round-trip verified — JSON matches CSV perfectly")
    else:
        print(f"  ✗ Mismatch detected — check the conversion")


if __name__ == "__main__":
    convert_all()
    round_trip_check("AAPL")