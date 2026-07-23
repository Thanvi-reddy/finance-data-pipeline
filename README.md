# Finance Data Pipeline

A fully automated stock data pipeline that downloads and maintains
maximum historical price data for 99 tickers across all major sectors.
Built to replace a paid stock data API - no API key needed.

---

## What This Does

- Downloads full historical data for 99 stock tickers using yfinance
- Auto-updates with only new rows (no re-downloading everything)
- Saves clean CSVs to data/raw/ and matching JSON to data/json/
- Runs automatically during NYSE trading hours via Supabase Cron + GitHub Actions
- Data persists between runs using Supabase Storage
- Logs every run with timestamps
- Provides an interactive CLI and a desktop GUI monitor

---

## How to Run

### 1. Install dependencies
pip install yfinance pandas schedule openpyxl pandas_market_calendars supabase

### 2. Run the automation pipeline (no user input needed)
python finance_pipeline.py

### 3. Run the interactive CLI (for humans)
python finance_cli.py

### 4. Run the Windows GUI monitor
py -3.11 gui_monitor.py

### 5. Run the daily local scheduler (optional, for local-only use)
python scheduler.py

---

## Automation Architecture

Data updates automatically during NYSE trading hours without any manual steps:

1. Supabase Cron (pg_cron + pg_net) fires on a schedule inside Supabase
2. It calls GitHub's API to trigger repository_dispatch on this repo
3. GitHub Actions runs: market-hours guard, download from Supabase Storage,
   run pipeline (update new rows), upload updated CSVs back to Supabase, commit logs

This design was chosen after GitHub Actions' own native schedule cron proved
unreliable on the free tier (runs were delayed by up to 1-2 hours during high load).
Supabase Cron was tested and confirmed to fire at exact intervals.

Cadence step-down (as required):
- 30 min - confirmed stable (13 consecutive runs, exact 30-min gaps, zero drift)
- 20 min - confirmed stable
- 10 min - active now (final target), Supabase Cron job trigger-finance-pipeline-10min

Persistent storage fix: GitHub Actions runs on a fresh server each time with no
local files. Fixed by integrating Supabase Storage - CSVs are downloaded at the
start of each run and uploaded back at the end. Confirmed: 99/99 tickers succeed
on every run.

---

## CLI Features (finance_cli.py)

| Option | What it does |
|--------|-------------|
| 1 | View price data for any ticker (choose how many rows) |
| 2 | Search ticker stats (rows, dates, file size) |
| 3 | Add a new ticker to the watchlist |
| 4 | Remove a ticker from the watchlist |
| 5 | Export any ticker's data to Excel |
| 6 | Manually trigger the pipeline |
| 7 | View last 20 pipeline log entries |
| 8 | Exit |

---

## GUI Monitor (gui_monitor.py)

Read-only Tkinter desktop app showing:
- Market status (OPEN/CLOSED) with live ET clock
- Last run result and status
- Countdown to next scheduled run
- Scrollable data summary (all 99 tickers, rows, latest date)
- Scrollable run log (color-coded RUN/SKIP)
- Auto-refreshes every 30 seconds

---

## NYSE Calendar

- calendar/nyse_2026.csv - 251 trading days for 2026
- calendar/build_calendar.py - builds and cross-verifies all 10 holidays
  against nyse.com
- Regular hours: 9:30 AM-4:00 PM ET; early closes on Nov 27 and Dec 24, 2026

---

## CSV to JSON

- scripts/csv_to_json.py - converts all CSVs in data/raw/ to data/json/
- CSV remains the primary format; JSON is kept as a recovery copy
- Round-trip verified: JSON matches CSV row-for-row

---

## Project Structure

finance-data-pipeline/
- finance_pipeline.py - Core automation engine
- finance_cli.py - Interactive CLI
- gui_monitor.py - Windows GUI monitor
- scheduler.py - Local daily scheduler (optional)
- tickers.csv - 99 tickers with sectors
- calendar/ - nyse_2026.csv, build_calendar.py
- scripts/ - download_yfinance.py, supabase_storage.py, csv_to_json.py, market_guard.py
- agent/ - agent.py (download agent with retry logic)
- n8n/ - workflow.json, evaluation.md
- docs/ - COMPARISON.md
- data/ - raw/, json/, earliest_dates_summary.csv, pipeline.log
- logs/ - run.log, pipeline_detail.log
- .github/workflows/ - scheduled_download.yml (triggered by Supabase Cron)

---

## Tickers Covered (99 total)

| Sector | Tickers |
|--------|---------|
| Technology | AAPL, MSFT, NVDA, GOOGL, META, AMZN, ORCL, ADBE, CRM, INTC, AMD, CSCO, IBM, TXN, QCOM, SHOP, SQ |
| Financials | JPM, BAC, WFC, GS, MS, C, BLK, AXP, SCHW, V, MA, BRK-B |
| Healthcare | JNJ, UNH, PFE, MRK, ABBV, LLY, TMO, ABT, BMY, AMGN, GILD, CVS |
| Consumer Staples | PG, KO, PEP, WMT, COST, MDLZ, CL, KMB |
| Consumer Discretionary | HD, MCD, NKE, SBUX, LOW, TGT, BKNG, TJX, DIS, F, UBER, ABNB |
| Energy | XOM, CVX, COP, SLB, EOG, PSX, OXY |
| Industrials | BA, CAT, GE, HON, UPS, RTX, LMT, DE, MMM, UNP |
| Communication | T, VZ, TMUS, CMCSA, NFLX, SNAP |
| Utilities/REIT | NEE, DUK, SO, AMT, PLD, O |
| ETF | SPY, QQQ, DIA, IWM, VTI |
| Edge Case (recent IPOs) | TSLA, PLTR, SNOW, COIN, RIVN |

---

## Known Notes

- yfinance is used instead of Yahoo Finance's manual CSV download, which is now
  behind a paywall - data is identical
- GitHub Actions' native scheduler was replaced with Supabase Cron due to
  free-tier queue delays
- BRK-B may occasionally need special handling due to the hyphen in the symbol

---

Built by Thanvi | Finance Data Pipeline Task | July 2026