import os
import csv
from scripts.supabase_storage import upload_all

with open("tickers.csv") as f:
    reader = csv.DictReader(f)
    tickers = [row["ticker"].strip() for row in reader]

upload_all(tickers)