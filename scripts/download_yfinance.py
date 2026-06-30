import yfinance as yf
import pandas as pd
import os

import csv

with open("tickers.csv") as f:
    reader = csv.reader(f)
    next(reader)  # skip header
    tickers = [row[0] for row in reader]

output_dir = "data/raw"
os.makedirs(output_dir, exist_ok=True)

for ticker in tickers:
    print(f"Downloading {ticker}...")
    data = yf.Ticker(ticker).history(period="max")

    if data.empty:
        print(f"  No data returned for {ticker}")
        continue

    filepath = os.path.join(output_dir, f"{ticker}_max_yf.csv")
    data.to_csv(filepath)

    earliest_date = data.index[0]
    row_count = len(data)
    print(f"  Saved {filepath} | Earliest date: {earliest_date} | Rows: {row_count}")