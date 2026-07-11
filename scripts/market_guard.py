"""
Market Hours Guard
-------------------
Called by GitHub Actions before running the download.
Exit code 0 = market open, run the job.
Exit code 78 = market closed, skip cleanly.

Run: python scripts/market_guard.py
"""

import sys
import pandas as pd
import pandas_market_calendars as mcal

nyse = mcal.get_calendar("NYSE")
now = pd.Timestamp.now(tz="America/New_York")
sched = nyse.schedule(start_date=now.date(), end_date=now.date())
is_open = (not sched.empty) and nyse.open_at_time(sched, now)

print(f"[{now:%Y-%m-%d %H:%M %Z}] market_open={is_open}")

sys.exit(0 if is_open else 78)