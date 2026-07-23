"""
Supabase Storage Integration
-----------------------------
Uploads and downloads stock CSVs to/from Supabase Storage Bucket.
Used by GitHub Actions to persist data between runs.

Run: python scripts/supabase_storage.py
"""
from dotenv import load_dotenv
load_dotenv()

import os
import pandas as pd
from pathlib import Path
from supabase import create_client

# ─── Config ───────────────────────────────────────────────────────
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
BUCKET_NAME = "stock-data"
DATA_DIR = Path("data/raw")


def get_client():
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set as environment variables")
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def upload_csv(ticker: str):
    """Upload a single ticker CSV to Supabase Storage."""
    filepath = DATA_DIR / f"{ticker}_max.csv"
    if not filepath.exists():
        print(f"  ✗ {ticker}: file not found locally")
        return False

    client = get_client()
    with open(filepath, "rb") as f:
        data = f.read()

    try:
        # Try upload first, if exists then update
        try:
            client.storage.from_(BUCKET_NAME).upload(
                f"{ticker}_max.csv", data,
                {"content-type": "text/csv", "upsert": "true"}
            )
        except Exception:
            client.storage.from_(BUCKET_NAME).update(
                f"{ticker}_max.csv", data,
                {"content-type": "text/csv"}
            )
        print(f"  ✓ {ticker}: uploaded")
        return True
    except Exception as e:
        print(f"  ✗ {ticker}: upload failed — {e}")
        return False


def download_csv(ticker: str) -> bool:
    """Download a single ticker CSV from Supabase Storage."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    client = get_client()

    try:
        data = client.storage.from_(BUCKET_NAME).download(f"{ticker}_max.csv")
        filepath = DATA_DIR / f"{ticker}_max.csv"
        with open(filepath, "wb") as f:
            f.write(data)
        print(f"  ✓ {ticker}: downloaded")
        return True
    except Exception as e:
        print(f"  ✗ {ticker}: not in Supabase yet — {e}")
        return False


def upload_all(tickers: list):
    """Upload all ticker CSVs to Supabase."""
    print(f"Uploading {len(tickers)} tickers to Supabase...")
    success = sum(upload_csv(t) for t in tickers)
    print(f"Done: {success}/{len(tickers)} uploaded")


def download_all(tickers: list):
    """Download all ticker CSVs from Supabase."""
    print(f"Downloading {len(tickers)} tickers from Supabase...")
    success = sum(download_csv(t) for t in tickers)
    print(f"Done: {success}/{len(tickers)} downloaded")


if __name__ == "__main__":
    import csv

    with open("tickers.csv") as f:
        reader = csv.DictReader(f)
        tickers = [row["ticker"].strip() for row in reader]

    print("Testing Supabase connection...")
    print(f"URL: {SUPABASE_URL}")
    print(f"Bucket: {BUCKET_NAME}")
    print()

    # Test with just AAPL first
    print("Testing upload with AAPL...")
    upload_csv("AAPL")

    print("\nTesting download with AAPL...")
    # Rename local file temporarily to test download
    test_path = DATA_DIR / "AAPL_max.csv"
    backup_path = DATA_DIR / "AAPL_max_backup.csv"
    test_path.rename(backup_path)

    result = download_csv("AAPL")
    if result:
        print("✓ Round-trip test passed — upload and download working")
        # Restore backup
        test_path.unlink()
        backup_path.rename(test_path)
    else:
        print("✗ Download failed")
        backup_path.rename(test_path)