#!/usr/bin/env python3
"""
Forest Live Dashboard v2.0 — Network + Phishing stats in real time
"""

import json
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from pathlib import Path
import time
from datetime import datetime

VAULT = Path.home() / "ForestVault"
LOG = VAULT / "training_chain.json"
PHISH_LOG = VAULT / "phishing_training_sessions.json"

console = Console()

def get_stats():
    stats = {"snapshots": 0, "last_snapshot": "Never", "log_size": "0 KB", "last_hash": "N/A",
             "phish_accuracy": "N/A", "hard_negatives": 0}

    # Network snapshots
    if LOG.exists():
        with open(LOG, "r") as f:
            lines = f.readlines()
        stats["snapshots"] = sum(1 for line in lines if "NETWORK_SNAPSHOT" in line)
        log_size = LOG.stat().st_size / 1024
        stats["log_size"] = f"{log_size:.1f} KB"
        last_line = lines[-1] if lines else ""
        stats["last_hash"] = last_line.split("Hash: ")[-1].strip() if "Hash:" in last_line else "N/A"
        stats["last_snapshot"] = last_line.split("|")[0].strip() if last_line else "Never"

    # Phishing stats (latest session)
    if PHISH_LOG.exists():
        with open(PHISH_LOG, "r") as f:
            lines = f.readlines()
        if lines:
            last_session = json.loads(lines[-1])
            stats["phish_accuracy"] = f"{last_session.get('accuracy', 0):.1f}%"
            stats["hard_negatives"] = last_session.get("hard_negatives_generated", 0)

    return stats

layout = Layout()
layout.split_column(
    Layout(name="header", size=3),
    Layout(name="main"),
)

def generate_table():
    stats = get_stats()
    table = Table(title="Forest Live Status")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("Network Snapshots", str(stats["snapshots"]))
    table.add_row("Last Snapshot", stats["last_snapshot"])
    table.add_row("Log Size", stats["log_size"])
    table.add_row("Last Cryptex Hash", stats["last_hash"])
    table.add_row("Phishing Accuracy (last)", stats["phish_accuracy"])
    table.add_row("Hard Negatives (last)", str(stats["hard_negatives"]))
    return table

def update_dashboard():
    layout["header"].update(Panel(f"[bold]🌲 Forest Live Dashboard v2.0 — {datetime.now().strftime('%H:%M:%S')}[/bold]", style="bold blue"))
    layout["main"].update(generate_table())

with Live(layout, refresh_per_second=1, screen=True) as live:
    while True:
        update_dashboard()
        time.sleep(5)
