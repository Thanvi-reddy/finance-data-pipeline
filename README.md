# Finance Data Pipeline

A fully automated stock data pipeline that downloads and maintains 
maximum historical price data for 100 tickers across all major sectors.
Built to replace a paid stock data API — no API key needed.

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

## Project Structure
finance-data-pipeline/
│
├── finance_pipeline.py      # Core automation — downloads & updates all tickers
├── finance_cli.py           # Interactive CLI — view, manage, export data
├── scheduler.py             # Daily auto-scheduler (runs pipeline at 6 PM)
├── tickers.csv              # Full list of 100 tickers with sectors
│
├── data/
│   ├── raw/                 # Downloaded CSVs (one per ticker)
│   ├── exports/             # Excel exports
│   ├── earliest_dates_summary.csv   # Summary of all ticker data
│   └── pipeline.log         # Full run logs
│
├── scripts/
│   └── download_yfinance.py # Original yfinance download script
│
├── agent/
│   └── agent.py             # Download agent with retry & error handling
│
├── n8n/
│   ├── workflow.json        # n8n workflow export
│   └── evaluation.md        # n8n vs code comparison
│
└── docs/
└── COMPARISON.md        # Manual vs yfinance comparison notes

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

## Notes

- Yahoo Finance CSV download is now behind a paywall — yfinance is used
  as the free alternative and produces identical data
- Manual download blocker raised with supervisor; yfinance confirmed as
  approved workaround
- n8n local install failed due to Node version mismatch (v25.6.1);
  cloud version used instead

---


---

*Built by Thanvi | Finance Data Pipeline Internship Task | July 2026*