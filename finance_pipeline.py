"""
Finance Data Pipeline
-----------------------------------------
Runs automatically with zero user input.
Can be called by scheduler, agent, or n8n.

Run: python scripts/market_guard.py && python finance_pipeline.py
"""

import yfinance as yf
import pandas as pd
import os
import time
import csv
import json
import logging
from datetime import date, datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

DATA_DIR = "data/raw"
TICKERS_FILE = "tickers.csv"
LATEST_SUMMARY_FILE = "data/latest.json"
RECENT_FILE = "data/recent.json"
RECENT_DAYS = 120  # covers the 10D/30D/90D chart views without needing
                    # the full multi-year CSV (which is what was making
                    # ticker switches slow — 300-400+ KB per switch)
SUMMARY_FILE = "data/earliest_dates_summary.csv"
LOG_FILE = "data/pipeline.log"
MAX_RETRIES = 3
RETRY_DELAY = 3

# Keep this modest — yfinance can start throttling/rate-limiting if hit
# with too many simultaneous requests. 8 is a safe starting point;
# lower it if you start seeing more "failed" tickers than before.
MAX_WORKERS = 8

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
        df = pd.read_csv(filepath, index_col=0)
        df.index = pd.to_datetime(df.index, utc=True).tz_convert(None)
        # Older files won't have download_ts yet — add it as missing so
        # dedupe/merge logic below doesn't break on legacy rows.
        if "download_ts" not in df.columns:
            df["download_ts"] = pd.NA
        return df
    return None


def dedupe(df):
    """Drop duplicate rows on the (date-index) key, keeping the latest
    download_ts for each. Returns (deduped_df, num_duplicates_removed)."""
    before = len(df)
    # Index (data timestamp) is the dedupe key per the checklist.
    # Sort so the most recent download_ts wins when duplicates exist.
    df = df.sort_values("download_ts")
    df = df[~df.index.duplicated(keep="last")]
    df = df.sort_index()
    removed = before - len(df)
    return df, removed


def snapshot(df):
    """Grab just the handful of fields the dashboard sidebar needs from a
    ticker's dataframe, so we don't have to ship the whole multi-MB CSV
    just to show a price and a % change badge."""
    if df is None or len(df) == 0:
        return None
    last = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else last
    dl_ts = last.get("download_ts")
    return {
        "close": round(float(last["Close"]), 2),
        "prev_close": round(float(prev["Close"]), 2),
        "high": round(float(last["High"]), 2),
        "low": round(float(last["Low"]), 2),
        "volume": int(last["Volume"]) if pd.notna(last["Volume"]) else 0,
        "date": str(df.index[-1].date()),
        "download_ts": None if pd.isna(dl_ts) else str(dl_ts),
        "rows": len(df),
    }


def recent_rows(df, n=RECENT_DAYS):
    """Return the last N days as a compact list of [date, O, H, L, C, V]
    arrays (not objects with repeated key names) to keep the file small —
    this is what the dashboard loads by default so it doesn't have to
    download the entire multi-year CSV just to draw a 10D/30D/90D chart."""
    if df is None or len(df) == 0:
        return []
    tail = df.tail(n)
    out = []
    for idx, row in tail.iterrows():
        out.append([
            str(idx.date()),
            round(float(row["Open"]), 2),
            round(float(row["High"]), 2),
            round(float(row["Low"]), 2),
            round(float(row["Close"]), 2),
            int(row["Volume"]) if pd.notna(row["Volume"]) else 0,
        ])
    return out


def download_ticker(ticker):
    ticker = ticker.strip().upper()
    existing = load_existing(ticker)
    attempt = 0
    last_error = None
    dupes_removed = 0

    while attempt < MAX_RETRIES:
        attempt += 1
        try:
            download_time = datetime.now(timezone.utc).isoformat()

            if existing is not None:
                last_date = existing.index.max()
                new_data = yf.Ticker(ticker).history(
                    start=last_date.date(),
                    end=date.today()
                )
                if not new_data.empty:
                    new_data.index = pd.to_datetime(new_data.index, utc=True)
                last_date_naive = last_date.tz_localize(None) if last_date.tzinfo else last_date
                new_data.index = pd.to_datetime(new_data.index).tz_localize(None)
                new_data = new_data[new_data.index > last_date_naive]

                if new_data.empty:
                    return {
                        "ticker": ticker,
                        "status": "up_to_date",
                        "rows": len(existing),
                        "earliest_date": str(existing.index.min().date()),
                        "latest_date": str(existing.index.max().date()),
                        "new_rows": 0,
                        "duplicates_removed": 0,
                        "snapshot": snapshot(existing),
                        "recent": recent_rows(existing),
                    }

                new_data["download_ts"] = download_time
                combined = pd.concat([existing, new_data])
                combined, dupes_removed = dedupe(combined)
                combined.to_csv(get_filepath(ticker))

                return {
                    "ticker": ticker,
                    "status": "updated",
                    "rows": len(combined),
                    "earliest_date": str(combined.index.min().date()),
                    "latest_date": str(combined.index.max().date()),
                    "new_rows": len(new_data),
                    "duplicates_removed": dupes_removed,
                    "snapshot": snapshot(combined),
                    "recent": recent_rows(combined),
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
                        "duplicates_removed": 0,
                    }
                data["download_ts"] = download_time
                data, dupes_removed = dedupe(data)
                data.to_csv(get_filepath(ticker))
                return {
                    "ticker": ticker,
                    "status": "downloaded",
                    "rows": len(data),
                    "earliest_date": str(data.index.min().date()),
                    "latest_date": str(data.index.max().date()),
                    "new_rows": len(data),
                    "duplicates_removed": dupes_removed,
                    "snapshot": snapshot(data),
                    "recent": recent_rows(data),
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
        "duplicates_removed": 0,
    }


def load_tickers():
    with open(TICKERS_FILE) as f:
        reader = csv.reader(f)
        next(reader)
        return [row[0].strip() for row in reader if row]


def save_summary(results):
    rows = [r for r in results if r["status"] != "failed"]
    if rows:
        df = pd.DataFrame(rows)[["ticker", "earliest_date", "latest_date", "rows", "status", "duplicates_removed"]]
        df.to_csv(SUMMARY_FILE, index=False)
        log.info(f"Summary saved to {SUMMARY_FILE}")


def save_latest_summary(results):
    """Write one small JSON file with each ticker's latest snapshot.
    The dashboard reads this single file for the sidebar instead of
    fetching all 99 full-history CSVs — the thing that was making the
    live page load slowly."""
    out = {}
    for r in results:
        if r.get("snapshot"):
            out[r["ticker"]] = r["snapshot"]
    with open(LATEST_SUMMARY_FILE, "w") as f:
        json.dump(out, f)
    log.info(f"Latest snapshot summary saved to {LATEST_SUMMARY_FILE} ({len(out)} tickers)")


def save_recent_summary(results):
    """Write one compact JSON file with the last RECENT_DAYS of OHLCV
    for every ticker. The dashboard loads this by default (small, fast)
    for the 10D/30D/90D chart views, instead of downloading each
    ticker's full multi-year CSV (300-400+ KB) just to switch tickers.
    The full CSV is only fetched lazily if someone clicks 'All'."""
    out = {}
    for r in results:
        if r.get("recent"):
            out[r["ticker"]] = r["recent"]
    with open(RECENT_FILE, "w") as f:
        json.dump(out, f)
    log.info(f"Recent-days summary saved to {RECENT_FILE} ({len(out)} tickers)")


def run_pipeline(tickers=None):
    if tickers is None:
        tickers = load_tickers()

    log.info(f"Pipeline started — {len(tickers)} tickers (parallel, {MAX_WORKERS} workers)")
    results = []
    completed = 0
    total_dupes = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(download_ticker, t): t for t in tickers}
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            completed += 1
            total_dupes += result.get("duplicates_removed", 0)

            if result["status"] == "downloaded":
                log.info(f"[{completed}/{len(tickers)}] {result['ticker']}: Full download | {result['rows']} rows | from {result['earliest_date']}")
            elif result["status"] == "updated":
                dupe_note = f" | {result['duplicates_removed']} dupes removed" if result['duplicates_removed'] else ""
                log.info(f"[{completed}/{len(tickers)}] {result['ticker']}: Updated | +{result['new_rows']} new rows{dupe_note}")
            elif result["status"] == "up_to_date":
                log.info(f"[{completed}/{len(tickers)}] {result['ticker']}: Already up to date")
            else:
                log.error(f"[{completed}/{len(tickers)}] {result['ticker']}: Failed")

    success = len([r for r in results if r["status"] != "failed"])
    failed = len([r for r in results if r["status"] == "failed"])
    log.info(f"Pipeline complete — {success} success | {failed} failed | {total_dupes} total duplicates removed")

    save_summary(results)
    save_latest_summary(results)
    save_recent_summary(results)
    return results


if __name__ == "__main__":
    run_pipeline()
