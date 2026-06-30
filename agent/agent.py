

import yfinance as yf
import os
import time

OUTPUT_DIR = "data/raw"
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 3


def download_ticker(ticker: str) -> dict:
    
    ticker = ticker.strip().upper()
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    attempt = 0
    last_error = None

    while attempt < MAX_RETRIES:
        attempt += 1
        try:
            data = yf.Ticker(ticker).history(period="max")

            # Case: invalid ticker or no data available
            if data.empty:
                return {
                    "ticker": ticker,
                    "status": "failed",
                    "message": "No data returned (invalid ticker or no history available)",
                    "filepath": None,
                    "rows": 0,
                    "earliest_date": None,
                }

            filepath = os.path.join(OUTPUT_DIR, f"{ticker}_max_agent.csv")
            data.to_csv(filepath)

            return {
                "ticker": ticker,
                "status": "success",
                "message": "Download successful",
                "filepath": filepath,
                "rows": len(data),
                "earliest_date": str(data.index[0]),
            }

        except Exception as e:
            last_error = str(e)
            print(f"  Attempt {attempt} failed for {ticker}: {last_error}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY_SECONDS)

    # All retries exhausted
    return {
        "ticker": ticker,
        "status": "failed",
        "message": f"Network/error after {MAX_RETRIES} attempts: {last_error}",
        "filepath": None,
        "rows": 0,
        "earliest_date": None,
    }


def run_agent(tickers: list) -> list:
    """
    Runs the agent across a list of tickers and prints a summary.
    """
    results = []
    for ticker in tickers:
        print(f"Processing {ticker}...")
        result = download_ticker(ticker)
        results.append(result)

        if result["status"] == "success":
            print(f"  SUCCESS | rows={result['rows']} | earliest={result['earliest_date']}")
        else:
            print(f"  FAILED  | {result['message']}")

    return results

import csv

if __name__ == "__main__":
    with open("tickers.csv") as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        all_tickers = [row[0] for row in reader]

    summary = run_agent(all_tickers)

    print("\n--- Summary ---")
    for r in summary:
        print(r)