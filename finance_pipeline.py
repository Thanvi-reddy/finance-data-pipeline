"""
Finance Data Pipeline — Automation Core
-----------------------------------------
Runs automatically with zero user input.
Can be called by scheduler, agent, or n8n.

Run: python finance_pipeline.py
"""

import yfinance as yf
import pandas as pd
import os
import time
import csv
import logging
from datetime import date

DATA_DIR = "data/raw"
TICKERS_FILE = "tickers.csv"
SUMMARY_FILE = "data/earliest_dates_summary.csv"
LOG_FILE = "data/pipeline.log"
MAX_RETRIES = 3
RETRY_DELAY = 3

# Setup logging
os.makedirs(DATA_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)


def get_filepath(ticker):
    return os.path.join(DATA_DIR, f"{ticker}_max.csv")


def load_existing(ticker):
    filepath = get_filepath(ticker)
    if os.path.exists(filepath):
        return pd.read_csv(filepath, index_col=0, parse_dates=True)
    return None


def download_ticker(ticker):
    ticker = ticker.strip().upper()
    existing = load_existing(ticker)
    attempt = 0
    last_error = None

    while attempt < MAX_RETRIES:
        attempt += 1
        try:
            if existing is not None:
                last_date = existing.index.max()
                new_data = yf.Ticker(ticker).history(
                    start=last_date.date(),
                    end=date.today()
                )
                new_data = new_data[new_data.index > last_date]
                if new_data.empty:
                    return {
                        "ticker": ticker,
                        "status": "up_to_date",
                        "rows": len(existing),
                        "earliest_date": str(existing.index.min().date()),
                        "latest_date": str(existing.index.max().date()),
                        "new_rows": 0,
                    }
                combined = pd.concat([existing, new_data])
                combined.to_csv(get_filepath(ticker))
                return {
                    "ticker": ticker,
                    "status": "updated",
                    "rows": len(combined),
                    "earliest_date": str(combined.index.min().date()),
                    "latest_date": str(combined.index.max().date()),
                    "new_rows": len(new_data),
                }
            else:
                data = yf.Ticker(ticker).history(period="max")
                if data.empty:
                    return {
                        "ticker": ticker,
                        "status": "failed",
                        "rows": 0,
                        "earliest_date": None,
                        "latest_date": None,
                        "new_rows": 0,
                    }
                data.to_csv(get_filepath(ticker))
                return {
                    "ticker": ticker,
                    "status": "downloaded",
                    "rows": len(data),
                    "earliest_date": str(data.index.min().date()),
                    "latest_date": str(data.index.max().date()),
                    "new_rows": len(data),
                }
        except Exception as e:
            last_error = str(e)
            log.warning(f"Attempt {attempt} failed for {ticker}: {last_error}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)

    return {
        "ticker": ticker,
        "status": "failed",
        "rows": 0,
        "earliest_date": None,
        "latest_date": None,
        "new_rows": 0,
    }


def load_tickers():
    with open(TICKERS_FILE) as f:
        reader = csv.reader(f)
        next(reader)
        return [row[0].strip() for row in reader if row]


def save_summary(results):
    rows = [r for r in results if r["status"] != "failed"]
    if rows:
        df = pd.DataFrame(rows)[["ticker", "earliest_date", "latest_date", "rows", "status"]]
        df.to_csv(SUMMARY_FILE, index=False)
        log.info(f"Summary saved to {SUMMARY_FILE}")


def run_pipeline(tickers=None):
    if tickers is None:
        tickers = load_tickers()

    log.info(f"Pipeline started — {len(tickers)} tickers")
    results = []

    for i, ticker in enumerate(tickers, 1):
        result = download_ticker(ticker)
        results.append(result)

        if result["status"] == "downloaded":
            log.info(f"[{i}/{len(tickers)}] {ticker}: Full download | {result['rows']} rows | from {result['earliest_date']}")
        elif result["status"] == "updated":
            log.info(f"[{i}/{len(tickers)}] {ticker}: Updated | +{result['new_rows']} new rows")
        elif result["status"] == "up_to_date":
            log.info(f"[{i}/{len(tickers)}] {ticker}: Already up to date")
        else:
            log.error(f"[{i}/{len(tickers)}] {ticker}: Failed")

        time.sleep(0.5)

    success = len([r for r in results if r["status"] != "failed"])
    failed = len([r for r in results if r["status"] == "failed"])
    log.info(f"Pipeline complete — {success} success | {failed} failed")

    save_summary(results)
    return results


if __name__ == "__main__":
    run_pipeline()