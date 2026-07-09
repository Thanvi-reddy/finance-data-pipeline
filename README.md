markdown# Finance Data Pipeline

An automated pipeline that downloads and maintains historical stock price data
for 100 tickers across all major sectors — combining a manual Yahoo Finance
workflow, a Python (yfinance) library approach, a repo agent, and an n8n
workflow experiment, per the assigned task.

---

## Overview

This project explores two parallel paths for acquiring historical stock data:

1. **Manual download** from the Yahoo Finance website (primary objective)
2. **Programmatic download** using the `yfinance` Python library (secondary,
   to understand how the data is exposed under the hood)

Both feed into an **automated agent pipeline** that can fetch, validate, and
save data for any ticker with minimal manual effort, plus a daily scheduler
and an n8n workflow experiment for comparison.

---

## Project Structure
finance-data-pipeline/
├── finance_pipeline.py          # Core automation — downloads & updates all tickers
├── finance_cli.py               # Interactive CLI — view, manage, export data
├── scheduler.py                 # Daily auto-scheduler (runs pipeline at 6 PM)
├── tickers.csv                  # Full list of 100 tickers with sectors
│
├── data/
│   ├── raw/                     # Downloaded CSVs, one per ticker (e.g. AAPL_max.csv)
│   ├── earliest_dates_summary.csv  # Summary of earliest date / row count per ticker
│   └── pipeline.log              # Run logs with timestamps
│
├── scripts/
│   └── download_yfinance.py     # yfinance-based download script (library route)
│
├── agent/
│   └── agent.py                 # Repo agent: fetch → validate → save, with retry & error handling
│
├── n8n/
│   ├── workflow.json            # Exported n8n workflow
│   └── evaluation.md            # n8n vs code-based approach comparison
│
└── docs/
└── COMPARISON.md            # Manual download vs yfinance: dates, row counts, notes

---

## How to Run

### 1. Install dependencies
pip install yfinance pandas schedule openpyxl

### 2. Run the automation pipeline (no input needed)
python finance_pipeline.py

### 3. Run the interactive CLI
python finance_cli.py

### 4. Run the daily auto-scheduler (updates data every day at 6 PM)
python scheduler.py

### 5. Run the yfinance-only download script
python scripts/download_yfinance.py

### 6. Run the repo agent for a single ticker
python agent/agent.py <TICKER>

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

## Manual vs yfinance

Full comparison — earliest dates, row counts, and any gaps/splits observed —
is documented in `docs/COMPARISON.md`.

---

## Repo Agent

`agent/agent.py` wraps the download in a single reusable function:
- **Input:** a ticker symbol
- **Output:** a saved CSV in `data/raw/`, plus a success/fail status
- **Handles:** invalid tickers, empty responses, and network errors with retry

Adding a new ticker only requires adding it to `tickers.csv` — no code changes.

---

## n8n Workflow

An equivalent download flow was built in n8n and exported to
`n8n/workflow.json`. The setup, reliability, and maintainability comparison
against the Python agent is written up in `n8n/evaluation.md`.

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

## Notes

- Yahoo Finance's direct CSV export was used for the manual download route;
  `yfinance` was used to replicate the same data programmatically for comparison.
- Manual download blocker was raised and yfinance confirmed as an approved
  supplementary approach.
- n8n local install hit a Node version mismatch (v25.6.1); the cloud version
  was used instead.

---



*Built by Thanvi | Finance Data Pipeline Task | July 2026*