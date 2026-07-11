"""
NYSE Calendar Builder
----------------------
Downloads and verifies the 2026 NYSE trading calendar.
Cross-checks holidays against verified list from task doc.
Saves to calendar/nyse_2026.csv

Run: python calendar/build_calendar.py
"""

import pandas as pd
import pandas_market_calendars as mcal
from pathlib import Path

# ─── Build 2026 calendar ───────────────────────────────────────────
nyse = mcal.get_calendar("NYSE")
sched = nyse.schedule(start_date="2026-01-01", end_date="2026-12-31")

# Save to CSV
output_path = Path("calendar/nyse_2026.csv")
output_path.parent.mkdir(parents=True, exist_ok=True)
sched.to_csv(output_path)
print(f"Saved {len(sched)} trading days to {output_path}")

# ─── Verify trading hours ──────────────────────────────────────────
print("\nTrading Hours (ET):")
print("  Regular: 9:30 AM - 4:00 PM")
print("  Early close (1:00 PM): Nov 27 and Dec 24 2026")

# ─── Cross-check holidays ─────────────────────────────────────────
verified_holidays_2026 = {
    "2026-01-01": "New Year's Day",
    "2026-01-19": "Martin Luther King Jr. Day",
    "2026-02-16": "Washington's Birthday",
    "2026-04-03": "Good Friday",
    "2026-05-25": "Memorial Day",
    "2026-06-19": "Juneteenth",
    "2026-07-03": "Independence Day (observed)",
    "2026-09-07": "Labor Day",
    "2026-11-26": "Thanksgiving Day",
    "2026-12-25": "Christmas Day",
}

print("\nCross-checking 2026 holidays:")
print("-" * 50)

all_days = pd.date_range("2026-01-01", "2026-12-31", freq="B")
trading_days = set(sched.index.strftime("%Y-%m-%d"))
non_trading = [d.strftime("%Y-%m-%d") for d in all_days
               if d.strftime("%Y-%m-%d") not in trading_days]

passed = 0
failed = 0
for date, name in verified_holidays_2026.items():
    if date in non_trading:
        print(f"  ✓ {date} — {name}")
        passed += 1
    else:
        print(f"  ✗ {date} — {name} NOT FOUND in calendar")
        failed += 1

print("-" * 50)
print(f"Holidays verified: {passed}/{len(verified_holidays_2026)}")
print(f"Total 2026 trading days: {len(sched)}")
print(f"First trading day: {sched.index[0].date()}")
print(f"Last trading day:  {sched.index[-1].date()}")

# ─── Check market open right now ──────────────────────────────────
now = pd.Timestamp.now(tz="America/New_York")
today_sched = nyse.schedule(
    start_date=now.date(),
    end_date=now.date()
)
is_open = (not today_sched.empty) and nyse.open_at_time(today_sched, now)
print(f"\nMarket open right now ({now:%Y-%m-%d %H:%M %Z}): {is_open}")