"""
Daily Scheduler
----------------
Runs finance_pipeline.py automatically every day at 6:00 PM.
Keep this window open in the background.

Run: python scheduler.py
"""

import schedule
import time
import logging
from datetime import datetime
from finance_pipeline import run_pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
log = logging.getLogger(__name__)


def job():
    log.info("Scheduled daily update starting...")
    run_pipeline()
    log.info("Scheduled daily update complete.")


# Schedule every day at 6:00 PM
schedule.every().day.at("18:00").do(job)

log.info("Scheduler started. Pipeline will run every day at 6:00 PM.")
log.info("Keep this window open. Press Ctrl+C to stop.")

# Run once immediately on startup
log.info("Running initial update now...")
job()

# Keep running
while True:
    schedule.run_pending()
    time.sleep(60)