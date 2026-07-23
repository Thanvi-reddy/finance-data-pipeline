"""
Supabase Storage Integration
-----------------------------
Uploads and downloads stock CSVs to/from Supabase Storage Bucket.
Used by GitHub Actions to persist data between runs.

Uses direct REST calls via `requests` instead of the storage3 client,
since storage3's error-handling path throws 'dict' object has no
attribute 'text' whenever the server returns a non-2xx response.

Run: python scripts/supabase_storage.py
"""
from dotenv import load_dotenv
load_dotenv()

import os
import requests
from pathlib import Path

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
BUCKET_NAME = "stock-data"
DATA_DIR = Path("data/raw")


def _check_config():
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set as environment variables")


def _headers(content_type: str = None):
    headers = {
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "apikey": SUPABASE_KEY,
    }
    if content_type:
        headers["Content-Type"] = content_type
    return headers


def upload_csv(ticker: str) -> bool:
    """Upload a single ticker CSV to Supabase Storage (create or overwrite)."""
    _check_config()
    filepath = DATA_DIR / f"{ticker}_max.csv"
    if not filepath.exists():
        print(f"  ✗ {ticker}: file not found locally")
        return False

    with open(filepath, "rb") as f:
        data = f.read()

    url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET_NAME}/{ticker}_max.csv"
    headers = _headers("text/csv")
    headers["x-upsert"] = "true"  # overwrite if it already exists

    try:
        resp = requests.post(url, headers=headers, data=data, timeout=30)
        if resp.status_code in (200, 201):
            print(f"  ✓ {ticker}: uploaded")
            return True
        else:
            print(f"  ✗ {ticker}: upload failed — HTTP {resp.status_code}: {resp.text[:200]}")
            return False
    except Exception as e:
        print(f"  ✗ {ticker}: upload failed — {e}")
        return False


def download_csv(ticker: str) -> bool:
    """Download a single ticker CSV from Supabase Storage."""
    _check_config()
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET_NAME}/{ticker}_max.csv"
    try:
        resp = requests.get(url, headers=_headers(), timeout=30)
        if resp.status_code == 200:
            filepath = DATA_DIR / f"{ticker}_max.csv"
            with open(filepath, "wb") as f:
                f.write(resp.content)
            print(f"  ✓ {ticker}: downloaded")
            return True
        else:
            print(f"  ✗ {ticker}: not in Supabase yet — HTTP {resp.status_code}")
            return False
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

    print("Testing upload with AAPL...")
    upload_csv("AAPL")

    print("\nTesting download with AAPL...")
    test_path = DATA_DIR / "AAPL_max.csv"
    backup_path = DATA_DIR / "AAPL_max_backup.csv"
    test_path.rename(backup_path)

    result = download_csv("AAPL")
    if result:
        print("✓ Round-trip test passed — upload and download working")
        test_path.unlink()
        backup_path.rename(test_path)
    else:
        print("✗ Download failed")
        backup_path.rename(test_path)