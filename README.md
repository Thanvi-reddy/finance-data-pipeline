Finance Data Pipeline

Task: build a pipeline to download maximum-history stock data for 100+ tickers
via manual website download, the yfinance library, a custom agent, and an n8n workflow.

Status
- Manual Yahoo Finance download: blocked (CSV download is now a paid feature).
- yfinance, agent, and n8n: complete and working across all 100 tickers.

1. Manual Download
blocked

2. yfinance Library
- Script: `scripts/download_yfinance.py`
- Reads tickers from `tickers.csv`, downloads max-history data via
  `yf.Ticker(ticker).history(period="max")`, saves to `data/raw/<TICKER>_max_yf.csv`
- Run with: `python scripts/download_yfinance.py`

3. Comparison Notes
See `docs/COMPARISON.md` (in progress, pending manual data).

4. Workflow / Repo Agent
- Script: `agent/agent.py`
- Reusable function `download_ticker(ticker)` input: ticker string,
  output: status dict (success/failure, filepath, rows, earliest date)
- Includes retry logic (3 attempts) and handles invalid tickers gracefully
- Run with: `python agent/agent.py`

5. n8n Workflow
- Flow: Manual Trigger -> HTTP Request (Yahoo Finance API)
- Exported workflow: `n8n/workflow.json`
- Evaluation notes: `n8n/evaluation.md`

6. Demo Video
[Will be added here once recorded]

How to Run Everything
1. `pip install yfinance pandas`
2. `python scripts/download_yfinance.py`: runs yfinance download for all tickers in tickers.csv
3. `python agent/agent.py` :runs the agent version with error handling
4. n8n workflow: import `n8n/workflow.json` into n8n, run manually

Repo Structure

data/raw/       - downloaded CSVs (manual, yfinance, agent outputs)
data/screenshots/ - manual download process screenshots
scripts/        - yfinance download script
agent/          - reusable download agent
n8n/            - n8n workflow export + evaluation
docs/           - comparison notes
tickers.csv     - full list of 100+ tickers
