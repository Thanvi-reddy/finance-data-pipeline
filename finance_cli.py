"""
Finance Data Pipeline — Control Panel
--------------------------------------
Interactive CLI for managing and exploring stock data.
Automation is handled separately by finance_pipeline.py.

Run: python finance_cli.py
"""

import pandas as pd
import os
import csv
from datetime import datetime
from finance_pipeline import (
    run_pipeline, load_tickers, download_ticker,
    get_filepath, DATA_DIR, LOG_FILE, TICKERS_FILE
)

EXPORT_DIR = "data/exports"


# ─────────────────────────────────────────────
# DISPLAY HELPERS
# ─────────────────────────────────────────────

def clear():
    os.system("cls" if os.name == "nt" else "clear")


def header():
    last_updated = "Never"
    log_path = LOG_FILE
    if os.path.exists(log_path):
        with open(log_path) as f:
            lines = f.readlines()
        for line in reversed(lines):
            if "Pipeline complete" in line:
                last_updated = line.split("|")[0].strip()
                break

    tickers = load_tickers()
    downloaded = sum(1 for t in tickers if os.path.exists(get_filepath(t)))

    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║         FINANCE DATA PIPELINE — Control Panel                   ║")
    print("║         Data powered by yfinance  |  No API key needed          ║")
    print("╠══════════════════════════════════════════════════════════════════╣")
    print(f"║  Tickers: {downloaded}/{len(tickers)} downloaded"
          f"   |   Last run: {last_updated:<30}║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print()


def divider():
    print("  " + "─" * 68)


def show_overview():
    """Show full portfolio overview table with sectors."""
    tickers_data = []
    with open(TICKERS_FILE) as f:
        reader = csv.DictReader(f)
        for row in reader:
            tickers_data.append(row)

    print(f"\n  {'PORTFOLIO OVERVIEW':^68}")
    divider()
    print(f"  {'Ticker':<10} {'Sector':<22} {'Earliest':<13} {'Latest':<13} {'Rows':<8} Status")
    divider()

    downloaded = 0
    for row in tickers_data:
        ticker = row.get("ticker", "").strip()
        sector = row.get("sector", "—").strip()
        filepath = get_filepath(ticker)
        if os.path.exists(filepath):
            df = pd.read_csv(filepath, index_col=0, parse_dates=True)
            earliest = str(df.index.min().date())
            latest = str(df.index.max().date())
            rows = len(df)
            print(f"  {ticker:<10} {sector:<22} {earliest:<13} {latest:<13} {rows:<8} ✓")
            downloaded += 1
        else:
            print(f"  {ticker:<10} {sector:<22} {'—':<13} {'—':<13} {'—':<8} ✗ Missing")

    divider()
    missing = len(tickers_data) - downloaded
    print(f"  Total: {len(tickers_data)} tickers  |  "
          f"Downloaded: {downloaded}  |  Missing: {missing}")
    print()


def show_menu():
    print(f"  {'ACTIONS':^30}")
    divider()
    print("  [1]  View price data for a ticker")
    print("  [2]  Search ticker stats")
    print("  [3]  Add ticker to watchlist")
    print("  [4]  Remove ticker from watchlist")
    print("  [5]  Export ticker data to Excel")
    print("  [6]  Run pipeline now (manual trigger)")
    print("  [7]  View pipeline logs")
    print("  [8]  Exit")
    divider()
    print()


# ─────────────────────────────────────────────
# ACTIONS
# ─────────────────────────────────────────────

def view_price_data():
    ticker = input("  Enter ticker symbol (e.g. AAPL): ").strip().upper()
    filepath = get_filepath(ticker)
    if not os.path.exists(filepath):
        print(f"\n  ✗ No data found for {ticker}. Run the pipeline first.\n")
        return

    df = pd.read_csv(filepath, index_col=0, parse_dates=True)
    df.index = pd.to_datetime(df.index, utc=True).date
    cols = ["Open", "High", "Low", "Close", "Volume"]
    available = [c for c in cols if c in df.columns]

    n = input("  How many recent rows? (press Enter for all): ").strip()

    print(f"\n  {'═'*68}")
    print(f"  {ticker} — Historical Price Data")
    print(f"  {'═'*68}")

    if n.isdigit():
        print(df[available].tail(int(n)).to_string())
    else:
        print(df[available].to_string())

    print(f"\n  Rows: {len(df)}  |  "
          f"Earliest: {df.index.min()}  |  Latest: {df.index.max()}")
    print(f"  {'═'*68}\n")


def search_ticker():
    ticker = input("  Enter ticker symbol: ").strip().upper()
    filepath = get_filepath(ticker)
    if not os.path.exists(filepath):
        print(f"\n  ✗ No data found for {ticker}.\n")
        return

    df = pd.read_csv(filepath, index_col=0, parse_dates=True)
    size_kb = os.path.getsize(filepath) // 1024

    print(f"\n  {'═'*50}")
    print(f"  Ticker        : {ticker}")
    print(f"  Earliest Date : {df.index.min().date()}")
    print(f"  Latest Date   : {df.index.max().date()}")
    print(f"  Total Rows    : {len(df):,}")
    print(f"  File Size     : {size_kb} KB")
    print(f"  File Path     : {filepath}")
    print(f"  Columns       : {', '.join(df.columns.tolist())}")
    print(f"  {'═'*50}\n")


def add_ticker():
    ticker = input("  Enter new ticker symbol (e.g. AMZN): ").strip().upper()
    sector = input("  Enter sector (e.g. Technology): ").strip()

    # Check if already exists
    with open(TICKERS_FILE) as f:
        existing = [row["ticker"].strip() for row in csv.DictReader(f)]

    if ticker in existing:
        print(f"\n  ✗ {ticker} already exists in watchlist.\n")
        return

    with open(TICKERS_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([ticker, sector])

    print(f"\n  ✓ {ticker} added to watchlist.")
    confirm = input(f"  Download data for {ticker} now? (yes/no): ").strip().lower()
    if confirm == "yes":
        result = download_ticker(ticker)
        if result["status"] == "downloaded":
            print(f"  ✓ Downloaded {result['rows']} rows | "
                  f"from {result['earliest_date']} to {result['latest_date']}")
        else:
            print(f"  ✗ Failed: {result.get('message', 'Unknown error')}")
    print()


def remove_ticker():
    ticker = input("  Enter ticker to remove: ").strip().upper()

    with open(TICKERS_FILE) as f:
        rows = list(csv.DictReader(f))

    matches = [r for r in rows if r["ticker"].strip() == ticker]
    if not matches:
        print(f"\n  ✗ {ticker} not found in watchlist.\n")
        return

    confirm = input(f"  Remove {ticker} from watchlist? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("  Cancelled.\n")
        return

    updated = [r for r in rows if r["ticker"].strip() != ticker]
    with open(TICKERS_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["ticker", "sector"])
        writer.writeheader()
        writer.writerows(updated)

    # Optionally delete the CSV file too
    filepath = get_filepath(ticker)
    if os.path.exists(filepath):
        del_data = input(f"  Also delete {ticker}'s downloaded data? (yes/no): ").strip().lower()
        if del_data == "yes":
            os.remove(filepath)
            print(f"  ✓ {ticker} removed from watchlist and data deleted.\n")
        else:
            print(f"  ✓ {ticker} removed from watchlist. Data file kept.\n")
    else:
        print(f"  ✓ {ticker} removed from watchlist.\n")


def export_to_excel():
    ticker = input("  Enter ticker to export (e.g. AAPL): ").strip().upper()
    filepath = get_filepath(ticker)
    if not os.path.exists(filepath):
        print(f"\n  ✗ No data found for {ticker}. Run the pipeline first.\n")
        return

    os.makedirs(EXPORT_DIR, exist_ok=True)
    df = pd.read_csv(filepath, index_col=0, parse_dates=True)

    export_path = os.path.join(EXPORT_DIR, f"{ticker}_data.xlsx")
    # Strip timezone info before exporting to Excel
    df.index = pd.to_datetime(df.index, utc=True).tz_localize(None)
    with pd.ExcelWriter(export_path, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name=ticker)
        workbook = writer.book
        worksheet = writer.sheets[ticker]
        for col in worksheet.columns:
            max_len = max(len(str(cell.value)) if cell.value else 0 for cell in col)
            worksheet.column_dimensions[col[0].column_letter].width = max_len + 4

    print(f"\n  ✓ Exported {ticker} data to {export_path}")
    print(f"  Rows: {len(df):,} | "
          f"From: {df.index.min().date()} | To: {df.index.max().date()}\n")


def run_pipeline_now():
    confirm = input("  Run full pipeline for all tickers now? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("  Cancelled.\n")
        return
    print()
    run_pipeline()
    print()


def view_logs():
    if not os.path.exists(LOG_FILE):
        print("\n  ✗ No log file found. Run the pipeline first.\n")
        return

    with open(LOG_FILE) as f:
        lines = f.readlines()

    last_lines = lines[-20:]
    print(f"\n  {'═'*68}")
    print(f"  Pipeline Logs — Last {len(last_lines)} entries")
    print(f"  {'═'*68}")
    for line in last_lines:
        print(f"  {line.rstrip()}")
    print(f"  {'═'*68}\n")


# ─────────────────────────────────────────────
# MAIN LOOP
# ─────────────────────────────────────────────

def main():
    actions = {
        "1": view_price_data,
        "2": search_ticker,
        "3": add_ticker,
        "4": remove_ticker,
        "5": export_to_excel,
        "6": run_pipeline_now,
        "7": view_logs,
    }

    while True:
        clear()
        header()
        show_overview()
        show_menu()

        choice = input("  Choose an option [1-8]: ").strip()

        if choice == "8":
            print("\n  Goodbye.\n")
            break
        elif choice in actions:
            print()
            actions[choice]()
            input("  Press Enter to return to menu...")
        else:
            print("\n  ✗ Invalid option. Please choose 1-8.\n")
            input("  Press Enter to continue...")


if __name__ == "__main__":
    main()