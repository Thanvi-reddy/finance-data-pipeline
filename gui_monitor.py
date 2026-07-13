"""
Stock Pipeline Monitor
-----------------------
Read-only Windows desktop app to monitor pipeline runs.
Shows market status, last run, log viewer, next run countdown,
data summary, and a manual refresh button.

Run: python gui_monitor.py
"""

import tkinter as tk
from tkinter import ttk, font
from pathlib import Path
import pandas as pd
import pandas_market_calendars as mcal
from datetime import datetime, timedelta
import threading
import time

# ─── Config ───────────────────────────────────────────────────────
LOG_FILE = Path("logs/run.log")
DATA_DIR = Path(r"C:\Users\thanv\finance-data-pipeline\data\raw")
TICKERS_FILE = Path("tickers.csv")
REFRESH_INTERVAL = 30000  # 30 seconds


# ─── Market Status ────────────────────────────────────────────────
def get_market_status():
    try:
        nyse = mcal.get_calendar("NYSE")
        now = pd.Timestamp.now(tz="America/New_York")
        sched = nyse.schedule(start_date=now.date(), end_date=now.date())
        is_open = (not sched.empty) and nyse.open_at_time(sched, now)
        return is_open, now
    except Exception as e:
        return False, None


def get_next_run(interval_minutes=30):
    now = datetime.utcnow()
    minutes = now.minute
    next_slot = (minutes // interval_minutes + 1) * interval_minutes
    if next_slot >= 60:
        next_time = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    else:
        next_time = now.replace(minute=next_slot, second=0, microsecond=0)
    delta = next_time - now
    mins = int(delta.total_seconds() // 60)
    secs = int(delta.total_seconds() % 60)
    return f"{mins}m {secs}s"


def get_last_run():
    if not LOG_FILE.exists():
        return "No runs yet", "—"
    lines = LOG_FILE.read_text().strip().splitlines()
    if not lines:
        return "No runs yet", "—"
    last = lines[-1]
    status = "RUN" if "RUN" in last else "SKIP"
    return last, status


def get_data_summary():
    if not DATA_DIR.exists():
        return []
    summaries = []
    csv_files = sorted(DATA_DIR.glob("*_max.csv"))
    for f in csv_files:
        try:
            df = pd.read_csv(f, index_col=0)
            ticker = f.stem.replace("_max", "")
            latest = str(df.index[-1])[:10]
            rows = len(df)
            summaries.append((ticker, rows, latest))
        except Exception as e:
            summaries.append((f.stem, 0, f"Error: {str(e)[:20]}"))
    return summaries


# ─── Main GUI ─────────────────────────────────────────────────────
class PipelineMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("Stock Pipeline Monitor")
        self.root.geometry("800x650")
        self.root.configure(bg="#1e1e2e")
        self.root.resizable(True, True)

        self.font_title = ("Consolas", 16, "bold")
        self.font_header = ("Consolas", 11, "bold")
        self.font_body = ("Consolas", 10)
        self.font_small = ("Consolas", 9)

        self.build_ui()
        self.refresh()

    def build_ui(self):
        # ── Title bar ──
        title_frame = tk.Frame(self.root, bg="#1e1e2e")
        title_frame.pack(fill="x", padx=15, pady=(15, 5))

        tk.Label(
            title_frame,
            text="◈  STOCK PIPELINE MONITOR",
            font=self.font_title,
            bg="#1e1e2e",
            fg="#cdd6f4"
        ).pack(side="left")

        self.time_label = tk.Label(
            title_frame,
            text="",
            font=self.font_small,
            bg="#1e1e2e",
            fg="#6c7086"
        )
        self.time_label.pack(side="right")

        tk.Frame(self.root, bg="#313244", height=1).pack(fill="x", padx=15)

        # ── Status row ──
        status_frame = tk.Frame(self.root, bg="#1e1e2e")
        status_frame.pack(fill="x", padx=15, pady=10)

        # Market status
        market_box = tk.Frame(status_frame, bg="#181825", padx=15, pady=10)
        market_box.pack(side="left", fill="both", expand=True, padx=(0, 5))

        tk.Label(market_box, text="MARKET STATUS",
                 font=self.font_header, bg="#181825", fg="#6c7086").pack(anchor="w")
        self.market_dot = tk.Label(market_box, text="● CHECKING...",
                                   font=("Consolas", 13, "bold"),
                                   bg="#181825", fg="#f9e2af")
        self.market_dot.pack(anchor="w", pady=(5, 0))
        self.market_time = tk.Label(market_box, text="",
                                    font=self.font_small, bg="#181825", fg="#6c7086")
        self.market_time.pack(anchor="w")

        # Last run
        run_box = tk.Frame(status_frame, bg="#181825", padx=15, pady=10)
        run_box.pack(side="left", fill="both", expand=True, padx=(5, 5))

        tk.Label(run_box, text="LAST RUN",
                 font=self.font_header, bg="#181825", fg="#6c7086").pack(anchor="w")
        self.last_run_label = tk.Label(run_box, text="—",
                                       font=self.font_body, bg="#181825",
                                       fg="#cdd6f4", wraplength=200, justify="left")
        self.last_run_label.pack(anchor="w", pady=(5, 0))
        self.last_run_status = tk.Label(run_box, text="",
                                        font=("Consolas", 11, "bold"),
                                        bg="#181825", fg="#a6e3a1")
        self.last_run_status.pack(anchor="w")

        # Next run
        next_box = tk.Frame(status_frame, bg="#181825", padx=15, pady=10)
        next_box.pack(side="left", fill="both", expand=True, padx=(5, 0))

        tk.Label(next_box, text="NEXT RUN IN",
                 font=self.font_header, bg="#181825", fg="#6c7086").pack(anchor="w")
        self.next_run_label = tk.Label(next_box, text="—",
                                       font=("Consolas", 20, "bold"),
                                       bg="#181825", fg="#89b4fa")
        self.next_run_label.pack(anchor="w", pady=(5, 0))
        tk.Label(next_box, text="(30 min cadence)",
                 font=self.font_small, bg="#181825", fg="#6c7086").pack(anchor="w")

        # ── Data summary ──
        tk.Label(self.root, text="  DATA SUMMARY",
                 font=self.font_header, bg="#1e1e2e", fg="#6c7086").pack(anchor="w", padx=15)

        summary_frame = tk.Frame(self.root, bg="#181825", padx=10, pady=8)
        summary_frame.pack(fill="x", padx=15, pady=(2, 8))

        summary_scroll = tk.Scrollbar(summary_frame)
        summary_scroll.pack(side="right", fill="y")
        self.summary_label = tk.Text(
            summary_frame,
            font=self.font_small,
            bg="#181825",
            fg="#cdd6f4",
            relief="flat",
            height=8,
            yscrollcommand=summary_scroll.set,
            state="disabled"
        )
        self.summary_label.pack(fill="both", expand=True)
        summary_scroll.config(command=self.summary_label.yview)

        # ── Log viewer ──
        tk.Label(self.root, text="  RUN LOG  (most recent first)",
                 font=self.font_header, bg="#1e1e2e", fg="#6c7086").pack(anchor="w", padx=15)

        log_frame = tk.Frame(self.root, bg="#181825")
        log_frame.pack(fill="both", expand=True, padx=15, pady=(2, 8))

        scrollbar = tk.Scrollbar(log_frame)
        scrollbar.pack(side="right", fill="y")

        self.log_box = tk.Text(
            log_frame,
            font=self.font_small,
            bg="#181825",
            fg="#cdd6f4",
            insertbackground="#cdd6f4",
            selectbackground="#313244",
            relief="flat",
            yscrollcommand=scrollbar.set,
            state="disabled"
        )
        self.log_box.pack(fill="both", expand=True, padx=5, pady=5)
        scrollbar.config(command=self.log_box.yview)

        self.log_box.tag_config("run", foreground="#a6e3a1")
        self.log_box.tag_config("skip", foreground="#6c7086")
        self.log_box.tag_config("error", foreground="#f38ba8")

        # ── Bottom bar ──
        bottom = tk.Frame(self.root, bg="#181825", pady=8)
        bottom.pack(fill="x", padx=15, pady=(0, 10))

        tk.Button(
            bottom,
            text="⟳  REFRESH",
            font=self.font_header,
            bg="#313244",
            fg="#cdd6f4",
            activebackground="#45475a",
            activeforeground="#cdd6f4",
            relief="flat",
            padx=20,
            pady=5,
            cursor="hand2",
            command=self.refresh
        ).pack(side="left")

        self.status_bar = tk.Label(
            bottom,
            text="Ready",
            font=self.font_small,
            bg="#181825",
            fg="#6c7086"
        )
        self.status_bar.pack(side="right", padx=10)

    def refresh(self):
        now_utc = datetime.utcnow()
        self.time_label.config(text=f"UTC {now_utc:%Y-%m-%d %H:%M:%S}")

        is_open, now_et = get_market_status()
        if is_open:
            self.market_dot.config(text="● OPEN", fg="#a6e3a1")
        else:
            self.market_dot.config(text="● CLOSED", fg="#f38ba8")
        if now_et:
            self.market_time.config(text=f"ET: {now_et:%H:%M:%S}")

        last_run, run_status = get_last_run()
        self.last_run_label.config(
            text=last_run[:50] + "..." if len(last_run) > 50 else last_run)
        if run_status == "RUN":
            self.last_run_status.config(text="✓ RAN", fg="#a6e3a1")
        elif run_status == "SKIP":
            self.last_run_status.config(text="○ SKIPPED", fg="#6c7086")
        else:
            self.last_run_status.config(text="— No runs yet", fg="#6c7086")

        self.next_run_label.config(text=get_next_run(30))

        summaries = get_data_summary()
        self.summary_label.config(state="normal")
        self.summary_label.delete("1.0", tk.END)
        if summaries:
            lines = f"{'Ticker':<10} {'Rows':<8} {'Latest'}\n"
            lines += "─" * 35 + "\n"
            for ticker, rows, latest in summaries:
                lines += f"{ticker:<10} {rows:<8} {latest}\n"
            self.summary_label.insert(tk.END, lines)
        else:
            self.summary_label.insert(
                tk.END, "No data found. Run the pipeline first.")
        self.summary_label.config(state="disabled")

        self.log_box.config(state="normal")
        self.log_box.delete("1.0", tk.END)
        if LOG_FILE.exists():
            lines = LOG_FILE.read_text().strip().splitlines()[::-1]
            for line in lines:
                if "RUN" in line:
                    self.log_box.insert(tk.END, line + "\n", "run")
                elif "SKIP" in line:
                    self.log_box.insert(tk.END, line + "\n", "skip")
                else:
                    self.log_box.insert(tk.END, line + "\n", "error")
        else:
            self.log_box.insert(
                tk.END, "No log file found. Waiting for first run...\n", "skip")
        self.log_box.config(state="disabled")
        self.status_bar.config(text=f"Last refreshed: {datetime.now():%H:%M:%S}")

        self.root.after(REFRESH_INTERVAL, self.refresh)


# ─── Run ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = PipelineMonitor(root)
    root.mainloop()