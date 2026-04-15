#!/usr/bin/env python3
"""
Forest CUS — Desktop Launcher
build/ForestLauncher.py

Bundled by PyInstaller into Forest.app.
Three screens:
  1. Welcome / prerequisite check (Ollama, venv, models)
  2. Setup wizard (runs setup.sh with live output when needed)
  3. Main control panel (Start/Stop/Pause/Dashboard + status)

Project location discovery order:
  1. ~/ForestVault/.project_path  (written after first successful locate)
  2. ~/Forest                     (default git clone location)
  3. Directory adjacent to Forest.app
  4. Manual file dialog
"""

import os
import queue
import signal
import subprocess
import sys
import threading
import time
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as filedialog
from pathlib import Path
from tkinter import font as tkfont

# ── Project discovery ─────────────────────────────────────────────────────────

VAULT_DIR     = Path.home() / "ForestVault"
PATH_CACHE    = VAULT_DIR / ".project_path"
PID_FILE      = VAULT_DIR / ".monitor_pid"
PAUSE_FILE    = VAULT_DIR / ".paused"
LOG_FILE      = VAULT_DIR / "monitor.log"


def _find_project() -> Path | None:
    candidates = []

    # 1. Cached path from previous launch
    if PATH_CACHE.exists():
        try:
            p = Path(PATH_CACHE.read_text().strip())
            if (p / "core" / "cus_langgraph.py").exists():
                candidates.insert(0, p)
        except Exception:
            pass

    # 2. Default git clone location
    candidates.append(Path.home() / "Forest")

    # 3. Adjacent to this .app bundle (if running from inside project)
    if getattr(sys, "frozen", False):
        # sys.executable is Forest.app/Contents/MacOS/Forest
        app_parent = Path(sys.executable).parent.parent.parent.parent
        candidates.append(app_parent)

    # 4. Same directory as this script (development mode)
    candidates.append(Path(__file__).parent.parent)

    for p in candidates:
        if (p / "core" / "cus_langgraph.py").exists():
            return p.resolve()
    return None


PROJECT_DIR = _find_project()


def _save_project_path(p: Path) -> None:
    VAULT_DIR.mkdir(exist_ok=True)
    PATH_CACHE.write_text(str(p))


# ── Process helpers ───────────────────────────────────────────────────────────

def _is_running() -> bool:
    if not PID_FILE.exists():
        return False
    try:
        pid = int(PID_FILE.read_text().strip())
        os.kill(pid, 0)
        return True
    except (OSError, ValueError):
        PID_FILE.unlink(missing_ok=True)
        return False


def _is_paused() -> bool:
    return PAUSE_FILE.exists()


def _ollama_installed() -> bool:
    return subprocess.run(
        ["which", "ollama"], capture_output=True
    ).returncode == 0


def _ollama_running() -> bool:
    try:
        import urllib.request
        urllib.request.urlopen("http://localhost:11434/api/tags", timeout=2)
        return True
    except Exception:
        return False


def _venv_ready() -> bool:
    if PROJECT_DIR is None:
        return False
    return (PROJECT_DIR / "venv" / "bin" / "python3").exists()


def _python_bin() -> Path | None:
    if PROJECT_DIR is None:
        return None
    p = PROJECT_DIR / "venv" / "bin" / "python3"
    return p if p.exists() else None


def _last_log_lines(n: int = 4) -> str:
    if not LOG_FILE.exists():
        return ""
    try:
        lines = LOG_FILE.read_text(errors="replace").splitlines()
        return "\n".join(lines[-n:])
    except Exception:
        return ""


def start_monitoring(interval: int = 30) -> None:
    if PROJECT_DIR is None or not _python_bin():
        return
    VAULT_DIR.mkdir(exist_ok=True)
    PAUSE_FILE.unlink(missing_ok=True)
    proc = subprocess.Popen(
        [str(_python_bin()), str(PROJECT_DIR / "core" / "cus_langgraph.py"),
         "--continuous", str(interval), "--alert"],
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
    if PROJECT_DIR is None or not _python_bin():
        return
    # Kill stale Streamlit
    subprocess.run("lsof -ti:8501 | xargs kill -9 2>/dev/null || true",
                   shell=True, capture_output=True)
    time.sleep(0.5)
    subprocess.Popen(
        [str(_python_bin()), "-m", "streamlit", "run",
         str(PROJECT_DIR / "dashboard" / "app.py"),
         "--server.headless", "true",
         "--server.port", "8501",
         "--browser.gatherUsageStats", "false"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    time.sleep(2)
    subprocess.run(["open", "http://localhost:8501"], check=False)


def start_ollama() -> None:
    subprocess.Popen(["ollama", "serve"],
                     stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL,
                     start_new_session=True)


# ── Theme ─────────────────────────────────────────────────────────────────────

BG        = "#0d1117"
BG2       = "#161b22"
BG3       = "#21262d"
FG        = "#e6edf3"
FG_DIM    = "#8b949e"
GREEN     = "#3fb950"
YELLOW    = "#d29922"
RED       = "#f85149"
BLUE      = "#58a6ff"
BORDER    = "#30363d"

BTN_GREEN  = {"bg": "#238636", "fg": "#ffffff", "activebackground": "#2ea043",
              "activeforeground": "#ffffff", "relief": "flat",
              "cursor": "hand2", "bd": 0}
BTN_RED    = {"bg": "#da3633", "fg": "#ffffff", "activebackground": "#f85149",
              "activeforeground": "#ffffff", "relief": "flat",
              "cursor": "hand2", "bd": 0}
BTN_BLUE   = {"bg": "#1f6feb", "fg": "#ffffff", "activebackground": "#388bfd",
              "activeforeground": "#ffffff", "relief": "flat",
              "cursor": "hand2", "bd": 0}
BTN_GHOST  = {"bg": BG3, "fg": FG, "activebackground": BORDER,
              "activeforeground": FG, "relief": "flat",
              "cursor": "hand2", "bd": 0}


# ── Main application window ───────────────────────────────────────────────────

class ForestApp(tk.Tk):
    POLL_MS   = 2000
    W, H      = 460, 540

    def __init__(self):
        super().__init__()
        self.title("Forest CUS")
        self.geometry(f"{self.W}x{self.H}")
        self.minsize(self.W, self.H)
        self.configure(bg=BG)
        self.resizable(False, False)

        self._setup_fonts()
        self._current_screen = None
        self._setup_q: queue.Queue = queue.Queue()

        # Show appropriate first screen
        if PROJECT_DIR is None:
            self._show_locate_screen()
        elif not _ollama_installed():
            self._show_ollama_screen()
        elif not _venv_ready():
            self._show_setup_screen()
        else:
            self._show_main_screen()

    # ── Fonts ─────────────────────────────────────────────────────────────────

    def _setup_fonts(self):
        self.f_h1    = tkfont.Font(family="SF Pro Display", size=22, weight="bold")
        self.f_h2    = tkfont.Font(family="SF Pro Text",    size=14, weight="bold")
        self.f_body  = tkfont.Font(family="SF Pro Text",    size=12)
        self.f_small = tkfont.Font(family="SF Pro Text",    size=11)
        self.f_mono  = tkfont.Font(family="SF Mono",        size=10)
        self.f_btn   = tkfont.Font(family="SF Pro Text",    size=12, weight="bold")
        self.f_giant = tkfont.Font(family="SF Pro Display", size=42)

    # ── Screen helper ─────────────────────────────────────────────────────────

    def _clear(self):
        for w in self.winfo_children():
            w.destroy()
        self._current_screen = None

    def _header(self, parent) -> tk.Frame:
        """Shared top bar with logo."""
        bar = tk.Frame(parent, bg=BG, pady=0)
        bar.pack(fill="x")
        tk.Label(bar, text="🌲  Forest CUS", font=self.f_h2,
                 bg=BG, fg=FG).pack(side="left", padx=20, pady=14)
        tk.Frame(bar, bg=BORDER, height=1).pack(fill="x", side="bottom")
        return bar

    def _btn(self, parent, text, cmd, style=BTN_GREEN, width=20, pady=8) -> tk.Button:
        b = tk.Button(parent, text=text, command=cmd, font=self.f_btn,
                      width=width, pady=pady, **style)
        b.pack(pady=5)
        return b

    # ── Screen 0: Locate project ──────────────────────────────────────────────

    def _show_locate_screen(self):
        self._clear()
        self._header(self)

        body = tk.Frame(self, bg=BG, padx=30)
        body.pack(fill="both", expand=True, pady=20)

        tk.Label(body, text="🔍  Where is Forest?", font=self.f_h1,
                 bg=BG, fg=FG).pack(pady=(10, 6))
        tk.Label(
            body,
            text=(
                "Forest CUS could not find the project folder.\n\n"
                "Expected: ~/Forest\n\n"
                "Click below to locate it, or move the Forest folder\n"
                "to your home directory and relaunch."
            ),
            font=self.f_body, bg=BG, fg=FG_DIM, justify="center", wraplength=380,
        ).pack(pady=10)

        self._btn(body, "📂  Locate Forest folder…", self._locate_folder)
        tk.Label(body, text="or", font=self.f_small, bg=BG, fg=FG_DIM).pack()
        self._btn(body, "🔄  Re-check ~/Forest", self._recheck_location,
                  style=BTN_GHOST)

    def _locate_folder(self):
        global PROJECT_DIR
        path = filedialog.askdirectory(
            title="Select the Forest CUS project folder",
            initialdir=str(Path.home()),
        )
        if path:
            p = Path(path)
            if (p / "core" / "cus_langgraph.py").exists():
                PROJECT_DIR = p
                _save_project_path(p)
                self._advance_from_locate()
            else:
                tk.messagebox.showerror(
                    "Wrong folder",
                    "That doesn't look like the Forest CUS project.\n"
                    "Please select the folder that contains 'core/', "
                    "'dashboard/', and 'setup.sh'."
                )

    def _recheck_location(self):
        global PROJECT_DIR
        PROJECT_DIR = _find_project()
        if PROJECT_DIR:
            _save_project_path(PROJECT_DIR)
            self._advance_from_locate()
        else:
            tk.messagebox.showinfo(
                "Not found",
                "Still can't find the project at ~/Forest.\n"
                "Use 'Locate Forest folder…' to point to it manually."
            )

    def _advance_from_locate(self):
        if not _ollama_installed():
            self._show_ollama_screen()
        elif not _venv_ready():
            self._show_setup_screen()
        else:
            self._show_main_screen()

    # ── Screen 1: Ollama missing ──────────────────────────────────────────────

    def _show_ollama_screen(self):
        self._clear()
        self._header(self)

        body = tk.Frame(self, bg=BG, padx=30)
        body.pack(fill="both", expand=True, pady=20)

        tk.Label(body, text="🤖  Ollama Required", font=self.f_h1,
                 bg=BG, fg=FG).pack(pady=(10, 6))
        tk.Label(
            body,
            text=(
                "Forest CUS runs AI models locally using Ollama.\n\n"
                "Ollama is free, runs entirely on your Mac,\n"
                "and doesn't send any data to the cloud.\n\n"
                "Click below to download it, then relaunch Forest."
            ),
            font=self.f_body, bg=BG, fg=FG_DIM, justify="center", wraplength=380,
        ).pack(pady=10)

        self._btn(body, "⬇️  Download Ollama (ollama.ai)",
                  lambda: subprocess.run(["open", "https://ollama.ai"], check=False))
        tk.Label(body,
                 text="After installing Ollama, click below:",
                 font=self.f_small, bg=BG, fg=FG_DIM).pack(pady=(15, 4))
        self._btn(body, "🔄  I've installed Ollama — continue",
                  self._check_ollama_retry, style=BTN_GHOST)

    def _check_ollama_retry(self):
        if _ollama_installed():
            if not _venv_ready():
                self._show_setup_screen()
            else:
                self._show_main_screen()
        else:
            tk.messagebox.showinfo(
                "Not found yet",
                "Ollama doesn't appear to be installed yet.\n"
                "Download it from https://ollama.ai and install it,\n"
                "then click the button again."
            )

    # ── Screen 2: Setup wizard ────────────────────────────────────────────────

    def _show_setup_screen(self):
        self._clear()
        self._header(self)
        self._current_screen = "setup"

        body = tk.Frame(self, bg=BG, padx=24)
        body.pack(fill="both", expand=True)

        tk.Label(body, text="⚙️  First-Time Setup", font=self.f_h1,
                 bg=BG, fg=FG).pack(pady=(14, 4))
        tk.Label(
            body,
            text="Downloads AI models and installs Python dependencies.\nRuns once — takes about 5–10 minutes.",
            font=self.f_body, bg=BG, fg=FG_DIM, justify="center",
        ).pack(pady=(0, 10))

        # Progress output box
        log_frame = tk.Frame(body, bg=BG2, bd=0, highlightbackground=BORDER,
                             highlightthickness=1)
        log_frame.pack(fill="both", expand=True, pady=(0, 10))

        self._setup_log = tk.Text(
            log_frame, bg=BG2, fg=FG_DIM, font=self.f_mono,
            relief="flat", state="disabled", wrap="word",
            bd=0, padx=8, pady=6,
        )
        sb = tk.Scrollbar(log_frame, command=self._setup_log.yview)
        self._setup_log.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self._setup_log.pack(fill="both", expand=True)

        # Progress bar
        self._setup_progress = ttk.Progressbar(
            body, mode="indeterminate", length=380
        )
        self._setup_progress.pack(pady=(0, 8))

        # Buttons
        btn_row = tk.Frame(body, bg=BG)
        btn_row.pack(pady=(0, 14))

        self._setup_btn = tk.Button(
            btn_row, text="▶  Run Setup", font=self.f_btn,
            padx=20, pady=8, command=self._run_setup, **BTN_GREEN,
        )
        self._setup_btn.pack(side="left", padx=6)

        self._setup_done_btn = tk.Button(
            btn_row, text="Launch Forest →", font=self.f_btn,
            padx=20, pady=8, command=self._show_main_screen,
            state="disabled", **BTN_BLUE,
        )
        self._setup_done_btn.pack(side="left", padx=6)

    def _setup_log_append(self, text: str):
        self._setup_log.configure(state="normal")
        self._setup_log.insert("end", text)
        self._setup_log.see("end")
        self._setup_log.configure(state="disabled")

    def _run_setup(self):
        if PROJECT_DIR is None:
            return
        self._setup_btn.configure(state="disabled", text="Running…")
        self._setup_progress.start(12)
        self._setup_log_append("Starting setup.sh…\n\n")

        def _worker():
            try:
                proc = subprocess.Popen(
                    ["bash", str(PROJECT_DIR / "setup.sh")],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    cwd=str(PROJECT_DIR),
                )
                for line in proc.stdout:
                    self._setup_q.put(("log", line))
                proc.wait()
                if proc.returncode == 0:
                    self._setup_q.put(("done", None))
                else:
                    self._setup_q.put(("error", f"\nSetup exited with code {proc.returncode}"))
            except Exception as exc:
                self._setup_q.put(("error", str(exc)))

        threading.Thread(target=_worker, daemon=True).start()
        self._drain_setup_queue()

    def _drain_setup_queue(self):
        try:
            while True:
                kind, payload = self._setup_q.get_nowait()
                if kind == "log":
                    self._setup_log_append(payload)
                elif kind == "done":
                    self._setup_progress.stop()
                    self._setup_log_append("\n✓  Setup complete!\n")
                    self._setup_btn.configure(text="✓  Done", bg="#2ea043")
                    self._setup_done_btn.configure(state="normal")
                    return
                elif kind == "error":
                    self._setup_progress.stop()
                    self._setup_log_append(f"\n✗  Error: {payload}\n")
                    self._setup_btn.configure(state="normal", text="▶  Retry Setup")
                    return
        except queue.Empty:
            pass
        self.after(100, self._drain_setup_queue)

    # ── Screen 3: Main control panel ──────────────────────────────────────────

    def _show_main_screen(self):
        self._clear()
        self._current_screen = "main"
        self._header(self)

        body = tk.Frame(self, bg=BG, padx=24)
        body.pack(fill="both", expand=True)

        # ── Big status indicator ──────────────────────────────────────────────
        status_card = tk.Frame(body, bg=BG2, highlightbackground=BORDER,
                               highlightthickness=1)
        status_card.pack(fill="x", pady=(14, 0))

        self._status_icon = tk.Label(status_card, text="●", font=self.f_giant,
                                     bg=BG2, fg=FG_DIM)
        self._status_icon.pack(pady=(14, 0))

        self._status_label = tk.Label(status_card, text="Checking…",
                                      font=self.f_h2, bg=BG2, fg=FG)
        self._status_label.pack()

        self._threat_label = tk.Label(status_card, text="",
                                      font=self.f_small, bg=BG2, fg=FG_DIM)
        self._threat_label.pack(pady=(2, 14))

        # ── Control buttons ───────────────────────────────────────────────────
        btn_card = tk.Frame(body, bg=BG)
        btn_card.pack(fill="x", pady=12)

        btn_row1 = tk.Frame(btn_card, bg=BG)
        btn_row1.pack()

        self._start_btn = tk.Button(
            btn_row1, text="▶  Start Monitoring", font=self.f_btn,
            padx=18, pady=9, command=self._on_start, **BTN_GREEN,
        )
        self._start_btn.grid(row=0, column=0, padx=5, pady=4)

        self._stop_btn = tk.Button(
            btn_row1, text="■  Stop", font=self.f_btn,
            padx=18, pady=9, command=self._on_stop, state="disabled",
            **BTN_RED,
        )
        self._stop_btn.grid(row=0, column=1, padx=5, pady=4)

        btn_row2 = tk.Frame(btn_card, bg=BG)
        btn_row2.pack()

        self._pause_btn = tk.Button(
            btn_row2, text="⏸  Pause", font=self.f_btn,
            padx=18, pady=9, command=self._on_pause, state="disabled",
            **BTN_GHOST,
        )
        self._pause_btn.grid(row=0, column=0, padx=5, pady=4)

        self._dash_btn = tk.Button(
            btn_row2, text="🌐  Open Dashboard", font=self.f_btn,
            padx=18, pady=9,
            command=lambda: threading.Thread(target=open_dashboard, daemon=True).start(),
            **BTN_BLUE,
        )
        self._dash_btn.grid(row=0, column=1, padx=5, pady=4)

        # ── Log preview ───────────────────────────────────────────────────────
        tk.Frame(body, bg=BORDER, height=1).pack(fill="x", pady=(8, 6))

        tk.Label(body, text="RECENT ACTIVITY", font=self.f_small,
                 bg=BG, fg=FG_DIM).pack(anchor="w")

        self._log_text = tk.Text(
            body, bg=BG2, fg=FG_DIM, font=self.f_mono,
            relief="flat", state="disabled", wrap="word",
            bd=0, padx=8, pady=6, height=5,
            highlightbackground=BORDER, highlightthickness=1,
        )
        self._log_text.pack(fill="x", pady=(4, 0))

        # Start polling
        self._poll_status()

    # ── Status polling ────────────────────────────────────────────────────────

    def _poll_status(self):
        if self._current_screen != "main":
            return
        self._refresh_main()
        self.after(self.POLL_MS, self._poll_status)

    def _refresh_main(self):
        running = _is_running()
        paused  = _is_paused()

        # Icon + label
        if running and not paused:
            self._status_icon.configure(fg=GREEN)
            self._status_label.configure(text="Monitoring Active", fg=FG)
        elif running and paused:
            self._status_icon.configure(fg=YELLOW)
            self._status_label.configure(text="Monitoring Paused", fg=YELLOW)
        else:
            self._status_icon.configure(fg=FG_DIM)
            self._status_label.configure(text="Not Monitoring", fg=FG_DIM)

        # Threat level from recent proposals
        threat = self._read_threat_level()
        self._threat_label.configure(
            text=f"Threat Level: {threat['label']}",
            fg=threat["color"],
        )

        # Buttons
        if running:
            self._start_btn.configure(state="disabled")
            self._stop_btn.configure(state="normal")
            self._pause_btn.configure(state="normal")
            if paused:
                self._pause_btn.configure(text="▶  Resume", **BTN_GREEN)
            else:
                self._pause_btn.configure(text="⏸  Pause", **BTN_GHOST)
        else:
            self._start_btn.configure(state="normal")
            self._stop_btn.configure(state="disabled")
            self._pause_btn.configure(state="disabled", text="⏸  Pause")

        # Log lines
        log_text = _last_log_lines(5)
        self._log_text.configure(state="normal")
        self._log_text.delete("1.0", "end")
        self._log_text.insert("end", log_text or "No log yet — start monitoring to see activity.")
        self._log_text.configure(state="disabled")

    def _read_threat_level(self) -> dict:
        """Read the last few proposals and derive a threat level."""
        if PROJECT_DIR is None:
            return {"label": "⚪ Unknown", "color": FG_DIM}

        proposals_dir = VAULT_DIR / "proposals"
        if not proposals_dir.exists():
            return {"label": "⚪ No data", "color": FG_DIM}

        try:
            files = sorted(proposals_dir.glob("*.md"),
                           key=lambda p: p.stat().st_mtime, reverse=True)[:4]
            if not files:
                return {"label": "⚪ No data", "color": FG_DIM}

            import re
            scores, blocked = [], []
            drift_verdict = ""

            for f in files:
                text = f.read_text(errors="replace")
                # Score
                m = re.search(r"\*\*Grade\*\*:\s*([\d.]+)", text)
                if m:
                    scores.append(float(m.group(1)))
                # Decision
                if "BLOCKED" in text:
                    blocked.append(f.name)
                # Drift
                for verdict in ("SIGNIFICANT_DRIFT", "MODERATE_DRIFT", "MINOR_DRIFT"):
                    if verdict in text:
                        drift_verdict = verdict
                        break

            if blocked or drift_verdict == "SIGNIFICANT_DRIFT" or (scores and min(scores) < 65):
                return {"label": "🔴 RED — Review required", "color": RED}
            if drift_verdict in ("MODERATE_DRIFT", "MINOR_DRIFT") or (scores and min(scores) < 80):
                return {"label": "🟡 YELLOW — Minor anomalies", "color": YELLOW}
            if scores:
                avg = sum(scores) / len(scores)
                return {"label": f"🟢 GREEN — Nominal (avg {avg:.0f})", "color": GREEN}
        except Exception:
            pass

        return {"label": "⚪ No data", "color": FG_DIM}

    # ── Button handlers ───────────────────────────────────────────────────────

    def _on_start(self):
        # Start Ollama if not running
        if not _ollama_running():
            self._status_label.configure(text="Starting Ollama…", fg=YELLOW)
            self.update()
            threading.Thread(target=start_ollama, daemon=True).start()
            time.sleep(3)
        threading.Thread(target=start_monitoring, args=(30,), daemon=True).start()
        time.sleep(0.8)
        self._refresh_main()

    def _on_stop(self):
        stop_monitoring()
        self._refresh_main()

    def _on_pause(self):
        if _is_paused():
            PAUSE_FILE.unlink(missing_ok=True)
        else:
            PAUSE_FILE.touch()
        self._refresh_main()


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # On macOS, Tkinter needs to run on the main thread
    app = ForestApp()
    app.mainloop()
