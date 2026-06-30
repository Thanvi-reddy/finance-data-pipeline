Manual vs yfinance Comparison

Status
Manual download blocked: Yahoo Finance CSV download is now behind a premium paywall.

yfinance Library Results

| Ticker | Earliest Date | Row Count | Source |
|--------|---------------|-----------|--------|
| AAPL   | 1980-12-12    | 11,478    | yfinance (period="max") |
| MSFT   | 1986-03-13    | 10,152    | yfinance (period="max") |
| SPY    | 1993-01-29    | 8,411     | yfinance (period="max") |

Cross-check: AAPL Manual (Yahoo website, no CSV) vs yfinance
- Yahoo Finance website (Max range, visual check only): earliest date shown was Dec 12, 1980
- yfinance: earliest date 1980-12-12
- Match confirmed on earliest date (row-by-row comparison pending CSV access)

Cross-check: MSFT via GOOGLEFINANCE (Sheets) vs yfinance
- GOOGLEFINANCE: earliest date 13/03/1986, 10,151 rows
- yfinance: earliest date 1986-03-13, 10,152 rows
- Difference: 1 row — likely a header/edge row difference, needs further check

Notes
- AAPL date confirmed visually on Yahoo Finance (Max range) but full CSV not yet
  downloaded due to paywall.
- Will update this table once manual CSV access is resolved.