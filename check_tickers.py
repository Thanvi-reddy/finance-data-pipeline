import csv
with open('tickers.csv') as f:
    tickers = [r['ticker'] for r in csv.DictReader(f)]
print(f'Count: {len(tickers)}')
for t in tickers:
    print(t)