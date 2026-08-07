"""
Run pipeline + sync to Supabase (changed tickers only)
--------------------------------------------------------
Runs finance_pipeline.py, then uploads ONLY the tickers whose data
actually changed (status 'updated' or 'downloaded') to Supabase —
skipping tickers that were already up to date. This avoids wasting
requests re-uploading files that haven't changed.

Run: python scripts/run_and_sync.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from finance_pipeline import run_pipeline
from scripts.supabase_storage import upload_all


def main():
    results = run_pipeline()

    changed = [r["ticker"] for r in results if r["status"] in ("updated", "downloaded")]
    unchanged = len(results) - len(changed)

    print(f"\n{len(changed)} tickers changed, {unchanged} already up to date (skipping upload for those)")

    if changed:
        upload_all(changed)
    else:
        print("Nothing changed — skipping Supabase upload entirely")


if __name__ == "__main__":
    main()