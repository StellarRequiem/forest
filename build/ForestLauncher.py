#!/usr/bin/env python3
"""
Forest CUS Launcher — build/ForestLauncher.py

A minimal Tkinter app bundled by PyInstaller into Forest.app.
It manages the background monitoring process and opens the dashboard.

What it does NOT bundle:
  - Streamlit (too large; uses the installed venv)
  - Ollama (system-level installation)
  - Python venv (created by setup.sh)

First-run flow:
  User opens Forest.app → launcher checks for venv →
  if missing, shows setup instructions →
  if present, shows Start/Stop/Dashboard buttons

This is the pragmatic "consumer wrapper" approach:
  - setup.sh handles all installation (run once)
  - Forest.app handles all day-to-day interactions
"""

import os
import signal
import subprocess
import sys
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import font as tkfont

# ── Paths ─────────────────────────────────────────────────────────────────────

# When bundled by PyInstaller, __file__ lives inside the .app bundle.
# We look for the Forest project root relative to the .app's Resources dir.
if getattr(sys, "frozen", False):
    # Running inside .app bundle — project root is two levels up from MacOS/
    BUNDLE_DIR  = Path(sys.executable).parent
    # Try: Forest.app/Contents/MacOS/../../.. → user's installation
    PROJECT_DIR = BUNDLE_DIR.parent.parent.parent
else:
    PROJECT_DIR = Path(__file__).parent.parent

VAULT_DIR  = Path.home() / "ForestVault"
PID_FILE   = VAULT_DIR / ".monitor_pid"
PAUSE_FILE = VAULT_DIR / ".paused"
LOG_FILE   = VAULT_DIR / "monitor.log"
VENV_DIR   = PROJECT_DIR / "venv"
PYTHON     = VENV_DIR / "bin" / "python3"
CORE       = PROJECT_DIR / "core" / "cus_langgraph.py"
DASH       = PROJECT_DIR / "dashboard" / "app.py"

# ── Colors ────────────────────────────────────────────────────────────────────

BG       = "#1a1a2e"
BG_CARD  = "#16213e"
FG       = "#e0e0e0"
GREEN    = "#00d26a"
YELLOW   = "#ffd60a"
RED      = "#ff4757"
BLUE     = "#4fc3f7"
GRAY     = "#555577"


# ── Process helpers ───────────────────────────────────────────────────────────

def _is_running() -> bool:
    if not PID_FILE.exists():
        return False
    try:
        pid = int(PID_FILE.read_text().strip())
        os.kill(pid, 0)
        return True
    except (OSError, ValueError):
        return False


def _is_paused() -> bool:
    return PAUSE_FILE.exists()


def start_monitoring(interval: int = 30) -> None:
    VAULT_DIR.mkdir(exist_ok=True)
    PAUSE_FILE.unlink(missing_ok=True)
    proc = subprocess.Popen(
        [str(PYTHON), str(CORE), "--continuous", str(interval), "--alert"],
        stdout=open(LOG_FILE, "a"),
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    PID_FILE.write_text(str(proc.pid))


def stop_monitoring() -> None:
    if not PID_FILE.exists():
        return
    try:
        pid = int(PID_FILE.read_text().strip())
        os.kill(pid, signal.SIGTERM)
    except (OSError, ValueError):
        pass
    PID_FILE.unlink(missing_ok=True)
    PAUSE_FILE.unlink(missing_ok=True)


def open_dashboard() -> None:
    subprocess.Popen(
        [str(PYTHON), "-m", "streamlit", "run", str(DASH),
         "--server.headless", "true",
         "--server.port", "8501",
         "--browser.gatherUsageStats", "false"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    time.sleep(2)
    subprocess.run(["open", "http://localhost:8501"], check=False)


# ── GUI ───────────────────────────────────────────────────────────────────────

class ForestApp(tk.Tk):

    POLL_MS = 3000   # refresh status every 3 seconds

    def __init__(self):
        super().__init__()

        self.title("Forest CUS")
        self.geometry("380x280")
        self.resizable(False, False)
        self.configure(bg=BG)

        # Keep on top (like a status widget)
        self.attributes("-topmost", False)

        self._setup_fonts()
        self._build_ui()
        self._check_prerequisites()
        self._poll_status()

    def _setup_fonts(self):
        self.f_title  = tkfont.Font(family="SF Pro Display", size=18, weight="bold")
        self.f_status = tkfont.Font(family="SF Pro Text",    size=13)
        self.f_small  = tkfont.Font(family="SF Pro Text",    size=11)
        self.f_btn    = tkfont.Font(family="SF Pro Text",    size=12, weight="bold")

    def _build_ui(self):
        # Title row
        tk.Label(self, text="🌲 Forest CUS", font=self.f_title,
                 bg=BG, fg=FG).pack(pady=(18, 2))
        tk.Label(self, text="Blue-Team AI Monitoring", font=self.f_small,
                 bg=BG, fg=GRAY).pack(pady=(0, 12))

        # Status pill
        self.status_var = tk.StringVar(value="Checking…")
        self.status_lbl = tk.Label(self, textvariable=self.status_var,
                                   font=self.f_status, bg=BG, fg=GRAY)
        self.status_lbl.pack(pady=(0, 16))

        # Button row
        btn_frame = tk.Frame(self, bg=BG)
        btn_frame.pack(pady=(0, 12))

        self.start_btn = tk.Button(
            btn_frame, text="▶  Start",
            font=self.f_btn, bg=GREEN, fg="#000000",
            relief="flat", padx=16, pady=8,
            command=self._start,
        )
        self.start_btn.grid(row=0, column=0, padx=6)

        self.pause_btn = tk.Button(
            btn_frame, text="⏸  Pause",
            font=self.f_btn, bg=YELLOW, fg="#000000",
            relief="flat", padx=16, pady=8,
            command=self._toggle_pause,
        )
        self.pause_btn.grid(row=0, column=1, padx=6)

        self.stop_btn = tk.Button(
            btn_frame, text="■  Stop",
            font=self.f_btn, bg=RED, fg="#ffffff",
            relief="flat", padx=16, pady=8,
            command=self._stop,
        )
        self.stop_btn.grid(row=0, column=2, padx=6)

        # Dashboard button
        tk.Button(
            self, text="Open Dashboard  →",
            font=self.f_btn, bg=BLUE, fg="#000000",
            relief="flat", padx=20, pady=8,
            command=lambda: threading.Thread(target=open_dashboard, daemon=True).start(),
        ).pack(pady=(0, 10))

        # Setup warning label (hidden unless needed)
        self.setup_lbl = tk.Label(
            self, text="", font=self.f_small,
            bg=BG, fg=YELLOW, wraplength=340, justify="center",
        )
        self.setup_lbl.pack()

    def _check_prerequisites(self):
        if not VENV_DIR.exists() or not PYTHON.exists():
            self.setup_lbl.config(
                text="⚠  Setup required. Open Terminal and run:\n"
                     "    cd ~/Forest && bash setup.sh"
            )
            self.start_btn.config(state="disabled")

    def _poll_status(self):
        self._refresh_status()
        self.after(self.POLL_MS, self._poll_status)

    def _refresh_status(self):
        if _is_running():
            if _is_paused():
                self.status_var.set("⏸  Paused — cycles skipping")
                self.status_lbl.config(fg=YELLOW)
                self.pause_btn.config(text="▶  Resume")
                self.start_btn.config(state="disabled")
                self.stop_btn.config(state="normal")
            else:
                self.status_var.set("●  Monitoring active")
                self.status_lbl.config(fg=GREEN)
                self.pause_btn.config(text="⏸  Pause")
                self.start_btn.config(state="disabled")
                self.stop_btn.config(state="normal")
        else:
            self.status_var.set("○  Not monitoring")
            self.status_lbl.config(fg=GRAY)
            self.pause_btn.config(text="⏸  Pause")
            self.start_btn.config(state="normal")
            self.stop_btn.config(state="disabled")

    def _start(self):
        threading.Thread(target=start_monitoring, args=(30,), daemon=True).start()
        time.sleep(0.5)
        self._refresh_status()

    def _stop(self):
        stop_monitoring()
        self._refresh_status()

    def _toggle_pause(self):
        if _is_paused():
            PAUSE_FILE.unlink(missing_ok=True)
        else:
            PAUSE_FILE.touch()
        self._refresh_status()


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = ForestApp()
    app.mainloop()
