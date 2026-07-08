

import yfinance as yf
import pandas as pd
import os
import time
import csv
from datetime import datetime, date

DATA_DIR = "data/raw"
TICKERS_FILE = "tickers.csv"
SUMMARY_FILE = "data/earliest_dates_summary.csv"
MAX_RETRIES = 3
RETRY_DELAY = 3

def get_filepath(ticker):
    return os.path.join(DATA_DIR, f"{ticker}_max.csv")

def load_existing(ticker):
    filepath = get_filepath(ticker)
    if os.path.exists(filepath):
        df = pd.read_csv(filepath, index_col=0, parse_dates=True)
        return df
    return None

def download_ticker(ticker):
    ticker = ticker.strip().upper()
    os.makedirs(DATA_DIR, exist_ok=True)
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
                if new_data.empty:
                    return {
                        "ticker": ticker,
                        "status": "up_to_date",
                        "message": "No new rows since last update",
                        "filepath": get_filepath(ticker),
                        "rows": len(existing),
                        "earliest_date": str(existing.index.min().date()),
                        "latest_date": str(existing.index.max().date()),
                        "new_rows": 0,
                    }
                new_data = new_data[new_data.index > last_date]
                if new_data.empty:
                    return {
                        "ticker": ticker,
                        "status": "up_to_date",
                        "message": "No new rows since last update",
                        "filepath": get_filepath(ticker),
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
                    "message": f"{len(new_data)} new rows added",
                    "filepath": get_filepath(ticker),
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
                        "message": "No data returned",
                        "filepath": None,
                        "rows": 0,
                        "earliest_date": None,
                        "latest_date": None,
                        "new_rows": 0,
                    }
                data.to_csv(get_filepath(ticker))
                return {
                    "ticker": ticker,
                    "status": "downloaded",
                    "message": "Full history downloaded",
                    "filepath": get_filepath(ticker),
                    "rows": len(data),
                    "earliest_date": str(data.index.min().date()),
                    "latest_date": str(data.index.max().date()),
                    "new_rows": len(data),
                }
        except Exception as e:
            last_error = str(e)
            print(f"  Attempt {attempt} failed for {ticker}: {last_error}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)

    return {
        "ticker": ticker,
        "status": "failed",
        "message": f"Failed after {MAX_RETRIES} attempts: {last_error}",
        "filepath": None,
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

def show_status():
    print("\n" + "="*70)
    print(f"{'Ticker':<10} {'Earliest':<14} {'Latest':<14} {'Rows':<8} {'Status'}")
    print("-"*70)
    tickers = load_tickers()
    total = len(tickers)
    downloaded = 0
    for ticker in tickers:
        filepath = get_filepath(ticker)
        if os.path.exists(filepath):
            df = pd.read_csv(filepath, index_col=0, parse_dates=True)
            earliest = str(df.index.min().date())
            latest = str(df.index.max().date())
            rows = len(df)
            print(f"{ticker:<10} {earliest:<14} {latest:<14} {rows:<8} Downloaded")
            downloaded += 1
        else:
            print(f"{ticker:<10} {'—':<14} {'—':<14} {'—':<8} Not downloaded")
    print("-"*70)
    print(f"Total: {total} | Downloaded: {downloaded} | Missing: {total - downloaded}")
    print("="*70 + "\n")

def save_summary(results):
    os.makedirs(DATA_DIR, exist_ok=True)
    summary_rows = [r for r in results if r["status"] != "failed"]
    if summary_rows:
        df = pd.DataFrame(summary_rows)[["ticker", "earliest_date", "latest_date", "rows", "status"]]
        df.to_csv(SUMMARY_FILE, index=False)
        print(f"Summary saved to {SUMMARY_FILE}")

def run_pipeline(tickers):
    results = []
    total = len(tickers)
    print(f"\nRunning pipeline for {total} ticker(s)...\n")
    print("-"*50)
    for i, ticker in enumerate(tickers, 1):
        print(f"[{i}/{total}] {ticker}...", end=" ")
        result = download_ticker(ticker)
        results.append(result)
        if result["status"] == "downloaded":
            print(f"Full download | {result['rows']} rows | from {result['earliest_date']}")
        elif result["status"] == "updated":
            print(f"Updated | +{result['new_rows']} new rows | latest: {result['latest_date']}")
        elif result["status"] == "up_to_date":
            print(f"Already up to date | {result['rows']} rows")
        else:
            print(f"Failed | {result['message']}")
        time.sleep(0.5)
    success = len([r for r in results if r["status"] != "failed"])
    failed = len([r for r in results if r["status"] == "failed"])
    print(f"\nDone: {success} success | {failed} failed")
    save_summary(results)
    return results

def main():
    print("\n" + "="*50)
    print("     Finance Data Pipeline")
    print("     Powered by yfinance — No API key needed")
    print("="*50)
    show_status()
    print("Options:")
    print("  1. Download/update a single ticker")
    print("  2. Download/update ALL tickers in tickers.csv")
    print("  3. Exit")
    choice = input("\nChoose an option (1/2/3): ").strip()
    if choice == "1":
        ticker = input("Enter ticker symbol (e.g. AAPL): ").strip().upper()
        run_pipeline([ticker])
    elif choice == "2":
        tickers = load_tickers()
        print(f"\nFound {len(tickers)} tickers in {TICKERS_FILE}")
        run_pipeline(tickers)
    elif choice == "3":
        print("Exiting.")
        return
    else:
        print("Invalid option. Run the script again.")
        return
    show_status()

if __name__ == "__main__":
    main()