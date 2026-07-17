
import os
import csv

os.environ["SUPABASE_URL"] = "https://uyfaoiudszznnnihedgc.supabase.co"
os.environ["SUPABASE_KEY"] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV5ZmFvaXVkc3p6bm5uaWhlZGdjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODQzMTAxMDEsImV4cCI6MjA5OTg4NjEwMX0.kXJ56lrsJaNhTw7_J7lgk7Q3eWk-58ejJxflVk6zycE"

from scripts.supabase_storage import download_all, upload_all
from finance_pipeline import run_pipeline

with open("tickers.csv") as f:
    tickers = [row["ticker"].strip() for row in csv.DictReader(f)]

print("Step 1 - Download from Supabase:")
download_all(tickers)

print("\nStep 2 - Run pipeline:")
run_pipeline()

print("\nStep 3 - Upload back to Supabase:")
upload_all(tickers)