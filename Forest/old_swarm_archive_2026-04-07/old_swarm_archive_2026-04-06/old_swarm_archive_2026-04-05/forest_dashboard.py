#!/usr/bin/env python3
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from pathlib import Path
import json
from datetime import datetime

console = Console()
VAULT_DIR = Path.home() / "ForestVault"
REWARD_LEDGER = VAULT_DIR / "cus_reward_ledger.json"

def load_reward_ledger():
    if REWARD_LEDGER.exists():
        try:
            with open(REWARD_LEDGER) as f:
                return json.load(f)
        except:
            return {}
    return {}

def show_dashboard():
    ledger = load_reward_ledger()
    layout = Layout()
    layout.split_column(Layout(name="header", size=3), Layout(name="main"))
    layout["main"].split_row(Layout(name="left", ratio=1), Layout(name="right", ratio=1))

    header = Panel(f"[bold blue]Forest CUS Professional Dashboard[/bold blue] — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} — Brain Directed", style="bold")
    layout["header"].update(header)

    left_table = Table(title="CUS Reward Ledger + Active Agents", header_style="bold cyan")
    left_table.add_column("Agent", style="green")
    left_table.add_column("Points", justify="right")
    left_table.add_column("Promotions", justify="right")
    left_table.add_column("Status")
    for name, data in sorted(ledger.items()):
        left_table.add_row(name, str(data.get('total_points', 0)), str(data.get('promotions', 0)), "[green]ACTIVE[/green]")

    layout["left"].update(Panel(left_table, title="Reward & Agents"))

    tools_table = Table(title="Tools, Paths & Commands", header_style="bold magenta")
    tools_table.add_column("Command", style="yellow")
    tools_table.add_column("Path", style="dim")
    tools_table.add_column("Description")
    tools_table.add_row("f status", "~/Forest/forest_orchestrator.py", "Models + Network")
    tools_table.add_row("f chat ...", "~/Forest/forest_orchestrator.py", "Tool calling + Vaccine")
    tools_table.add_row("python forest_repl.py", "~/Forest/forest_repl.py", "Interactive CUS REPL")
    tools_table.add_row("python forest_dashboard.py", "~/Forest/forest_dashboard.py", "This dashboard")
    tools_table.add_row("tmux attach -t brain", "tmux", "Brain director")
    tools_table.add_row("tmux attach -t swarm", "tmux", "Live swarm")

    layout["right"].update(Panel(tools_table, title="Tools, Paths & Commands"))

    console.print(layout)
    console.print("\n[bold]DCP Active — Real human gate enforced — Brain is director[/bold]")

if __name__ == "__main__":
    show_dashboard()
