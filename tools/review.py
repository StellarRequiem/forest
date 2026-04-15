#!/usr/bin/env python3
"""
Forest Proposal Review — tools/review.py

Interactive CLI for reading, ranking, and archiving worker proposals
stored in ~/ForestVault/proposals/.

Usage:
    python3 tools/review.py             # interactive mode
    python3 tools/review.py --summary   # one-shot table, no interaction
    python3 tools/review.py --clear     # archive all current proposals

No external dependencies — stdlib only.
"""

import re
import sys
import shutil
import textwrap
from datetime import datetime
from pathlib import Path

# ── Vault paths ───────────────────────────────────────────────────────────────

VAULT         = Path.home() / "ForestVault"
PROPOSALS_DIR = VAULT / "proposals"
ARCHIVE_DIR   = VAULT / "proposals_archive"
CHAIN_FILE    = VAULT / "training_chain.json"
DAILY_DIR     = VAULT / "DailyReports"

PROPOSALS_DIR.mkdir(exist_ok=True)
ARCHIVE_DIR.mkdir(exist_ok=True)


# ── Terminal helpers ──────────────────────────────────────────────────────────

WIDTH = min(shutil.get_terminal_size().columns, 100)

RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
GREEN  = "\033[32m"
YELLOW = "\033[33m"
RED    = "\033[31m"
CYAN   = "\033[36m"
WHITE  = "\033[97m"

_USE_COLOR = sys.stdout.isatty()

def _c(text: str, *codes: str) -> str:
    """Wrap text in ANSI codes if stdout is a tty."""
    if not _USE_COLOR:
        return text
    return "".join(codes) + text + RESET

def _pad(text: str, width: int, align: str = "<") -> str:
    """
    Pad `text` to `width` columns using visible length (ignoring ANSI escapes).
    align: '<' left, '>' right.
    """
    ansi_escape = re.compile(r"\033\[[0-9;]*m")
    visible_len = len(ansi_escape.sub("", text))
    padding = max(0, width - visible_len)
    if align == ">":
        return " " * padding + text
    return text + " " * padding

def _hr(char: str = "─") -> str:
    return char * WIDTH

def _decision_color(decision: str) -> str:
    if "PROMOTE" in decision:
        return _c(decision, GREEN, BOLD)
    if "MAINTAIN" in decision:
        return _c(decision, YELLOW)
    return _c(decision, RED)


# ── Proposal parser ───────────────────────────────────────────────────────────

class Proposal:
    __slots__ = ("path", "worker", "timestamp", "task", "output", "score",
                 "decision", "points")

    def __init__(self, path: Path):
        self.path      = path
        self.worker    = "unknown"
        self.timestamp = ""
        self.task      = ""
        self.output    = ""
        self.score     = 0.0
        self.decision  = "REVIEW"
        self.points    = 0
        self._parse(path.read_text(errors="replace"))

    def _parse(self, text: str) -> None:
        # Header: # worker_name — YYYY-MM-DD HH:MM:SS
        m = re.match(r"#\s+(\S+)\s+[—-]\s+(.+)", text)
        if m:
            self.worker    = m.group(1)
            self.timestamp = m.group(2).strip()

        # Task
        m = re.search(r"\*\*Task\*\*:\s*(.+)", text)
        if m:
            self.task = m.group(1).strip()

        # Output block
        m = re.search(r"\*\*Output\*\*:\s*\n(.*?)\n\*\*Grade\*\*", text, re.DOTALL)
        if m:
            self.output = m.group(1).strip()

        # Grade: score → DECISION (+points pts)
        m = re.search(r"\*\*Grade\*\*:\s*([\d.]+)\s*[→>]\s*(\w+)\s*\(\+(\d+)", text)
        if m:
            self.score    = float(m.group(1))
            self.decision = m.group(2)
            self.points   = int(m.group(3))

    @property
    def short_output(self) -> str:
        """First ~75 chars of output, single line."""
        first = self.output.replace("\n", " ").strip()
        if len(first) > 75:
            return first[:72] + "…"
        return first

    @property
    def short_time(self) -> str:
        """HH:MM extracted from timestamp."""
        m = re.search(r"\d{2}:\d{2}", self.timestamp)
        return m.group(0) if m else self.timestamp[:5]


def load_proposals() -> list[Proposal]:
    files = sorted(PROPOSALS_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    proposals = []
    for f in files:
        try:
            proposals.append(Proposal(f))
        except Exception:
            pass
    return proposals


# ── Vault stats ───────────────────────────────────────────────────────────────

def vault_stats() -> dict:
    stats = {
        "proposals":    len(list(PROPOSALS_DIR.glob("*.md"))),
        "archived":     len(list(ARCHIVE_DIR.rglob("*.md"))),
        "chain_events": 0,
        "daily_reports": 0,
    }
    if CHAIN_FILE.exists():
        try:
            stats["chain_events"] = sum(1 for _ in CHAIN_FILE.open())
        except Exception:
            pass
    if DAILY_DIR.exists():
        stats["daily_reports"] = len(list(DAILY_DIR.glob("*.md")))
    return stats


# ── Display functions ─────────────────────────────────────────────────────────

def print_header(stats: dict) -> None:
    print()
    print(_c("  🌲 Forest Proposal Review", BOLD, WHITE))
    print(_c(_hr(), DIM))
    print(
        f"  {_c(str(stats['proposals']), BOLD)} proposals in queue  │  "
        f"{_c(str(stats['archived']), DIM)} archived  │  "
        f"{_c(str(stats['chain_events']), DIM)} audit events  │  "
        f"{_c(str(stats['daily_reports']), DIM)} daily reports"
    )
    print(_c(_hr(), DIM))


def print_table(proposals: list[Proposal]) -> None:
    if not proposals:
        print(_c("  No proposals in queue.", DIM))
        return

    # Sort: PROMOTE first, then by score descending
    ranked = sorted(proposals, key=lambda p: (p.decision != "PROMOTE", -p.score))

    # Column widths
    w_num  = 4
    w_who  = 26
    w_time = 6
    w_score= 7
    w_dec  = 10
    w_find = WIDTH - w_num - w_who - w_time - w_score - w_dec - 6

    header = (
        f"  {'#':<{w_num}}"
        f"{'Worker':<{w_who}}"
        f"{'Time':<{w_time}}"
        f"{'Score':>{w_score}}"
        f"  {'Decision':<{w_dec}}"
        f"  Finding"
    )
    print(_c(header, DIM))
    print(_c("  " + _hr("─"), DIM))

    for i, p in enumerate(ranked, 1):
        score_str = f"{p.score:.1f}"
        col_num   = _pad(_c(str(i), BOLD, CYAN),         w_num)
        col_who   = _pad(p.worker,                        w_who)
        col_time  = _pad(p.short_time,                    w_time)
        col_score = _pad(_c(score_str, BOLD),             w_score, ">")
        col_dec   = _pad(_decision_color(p.decision),     w_dec)
        col_find  = _c(p.short_output, DIM)
        print(f"  {col_num}{col_who}{col_time}{col_score}  {col_dec}  {col_find}")

    print(_c("  " + _hr("─"), DIM))
    print()
    return ranked


def print_full(proposal: Proposal) -> None:
    print()
    print(_c(_hr(), DIM))
    print(f"  {_c('Worker', DIM)}: {_c(proposal.worker, BOLD, WHITE)}")
    print(f"  {_c('Time', DIM)}  : {proposal.timestamp}")
    print(f"  {_c('Task', DIM)}  : {proposal.task}")
    print(f"  {_c('Grade', DIM)} : {_c(str(proposal.score), BOLD)} → "
          f"{_decision_color(proposal.decision)}  (+{proposal.points} pts)")
    print(_c(_hr(), DIM))
    print()
    # Word-wrap output at WIDTH-4
    for line in proposal.output.splitlines():
        if line.strip():
            for wrapped in textwrap.wrap(line, WIDTH - 4):
                print(f"    {wrapped}")
        else:
            print()
    print()
    print(_c(_hr(), DIM))
    print()


def print_help() -> None:
    print(
        _c(
            "  Commands:\n"
            "    [number]  — view full output of that proposal\n"
            "    a         — view all proposals in full\n"
            "    c         — archive (clear) the queue\n"
            "    r         — refresh table\n"
            "    q         — quit",
            DIM,
        )
    )
    print()


# ── Archive ───────────────────────────────────────────────────────────────────

def archive_proposals(proposals: list[Proposal]) -> int:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest  = ARCHIVE_DIR / stamp
    dest.mkdir(exist_ok=True)
    moved = 0
    for p in proposals:
        try:
            shutil.move(str(p.path), str(dest / p.path.name))
            moved += 1
        except Exception as exc:
            print(f"  Warning: could not move {p.path.name}: {exc}")
    return moved


# ── Main loops ────────────────────────────────────────────────────────────────

def run_interactive() -> None:
    while True:
        proposals = load_proposals()
        stats     = vault_stats()
        print_header(stats)
        ranked    = print_table(proposals)
        print_help()

        if not proposals:
            print("  Nothing to review. Run a swarm cycle first.")
            print()
            return

        try:
            cmd = input("  > ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return

        if cmd in ("q", "quit", "exit"):
            return

        if cmd in ("r", "refresh", ""):
            continue

        if cmd in ("c", "clear", "archive"):
            n = archive_proposals(proposals)
            print(f"\n  {_c(str(n), GREEN, BOLD)} proposals archived to {ARCHIVE_DIR}\n")
            continue

        if cmd in ("a", "all"):
            for p in ranked:
                print_full(p)
            input(_c("  Press Enter to continue…", DIM))
            continue

        # Numeric selection
        try:
            idx = int(cmd) - 1
            if 0 <= idx < len(ranked):
                print_full(ranked[idx])
                input(_c("  Press Enter to continue…", DIM))
            else:
                print(_c(f"  No proposal #{cmd}. Enter 1–{len(ranked)}.", RED))
        except ValueError:
            print(_c(f"  Unknown command '{cmd}'.", RED))


def run_summary() -> None:
    """Print table and exit — no interaction."""
    proposals = load_proposals()
    stats     = vault_stats()
    print_header(stats)
    print_table(proposals)


def run_clear() -> None:
    proposals = load_proposals()
    if not proposals:
        print("  Queue is already empty.")
        return
    n = archive_proposals(proposals)
    print(f"  Archived {n} proposals to {ARCHIVE_DIR}")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    args = sys.argv[1:]
    if "--summary" in args or "-s" in args:
        run_summary()
    elif "--clear" in args or "-c" in args:
        run_clear()
    else:
        run_interactive()
