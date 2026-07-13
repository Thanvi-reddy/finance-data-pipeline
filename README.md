# Finance Data Pipeline

A fully automated stock data pipeline that downloads and maintains 
maximum historical price data for 100 tickers across all major sectors.
Built to replace a paid stock data API - no API key needed.

---

## What This Does

- Downloads full historical data for 100 stock tickers using yfinance
- Auto-updates daily with only new rows (no re-downloading everything)
- Saves clean CSVs to `data/raw/` for direct use by a website or API
- Logs every run with timestamps
- Provides an interactive CLI for managing and exploring data

---

## How to Run

### 1. Install dependencies
pip install yfinance pandas schedule openpyxl

### 2. Run the automation pipeline (no user input needed)
python finance_pipeline.py

### 3. Run the interactive CLI (for humans)
python finance_cli.py

### 4. Run the daily auto-scheduler (keeps data updated every day at 6 PM)
python scheduler.py


---

## CLI Features

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

## Tickers Covered (100 total)

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
| Edge Case | TSLA, PLTR, SNOW, COIN, RIVN |

---
---

Scheduler, GUI Monitor & JSON

### Step 1 — NYSE Calendar
- Built 2026 NYSE trading calendar using `pandas_market_calendars`
- 251 trading days, all 10 holidays verified against nyse.com
- Saved to `calendar/nyse_2026.csv`
- Run: `python calendar/build_calendar.py`

### Step 2 — GitHub Actions Scheduler
- Workflow: `.github/workflows/scheduled_download.yml`
- Runs every 30 min during 13:00-21:00 UTC Mon-Fri
- Market guard (`scripts/market_guard.py`) checks NYSE hours before every run
- Logs RUN or SKIP with UTC timestamp to `logs/run.log`
- Commits logs back to repo automatically
- Cadence: 30 min (stable) → 20 min → 10 min (progressive)

### Step 3 — Windows GUI Monitor
- File: `gui_monitor.py`
- Run: `py -3.11 gui_monitor.py`
- Shows: market status (OPEN/CLOSED), last run, next run countdown,
  scrollable data summary (all tickers), scrollable run log
- Auto-refreshes every 30 seconds, read-only

### Step 4 — CSV to JSON
- Script: `scripts/csv_to_json.py`
- Run: `python scripts/csv_to_json.py`
- Converts all CSVs in `data/raw/` to JSON in `data/json/`
- Keeps both files — CSV is primary, JSON is recovery copy
- Round-trip verified: JSON matches CSV perfectly

*Built by Thanvi | Finance Data Pipeline  | July 2026*