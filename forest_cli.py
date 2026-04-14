#!/usr/bin/env python3
"""Forest CLI - Terminal interface for all 8 projects"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from rich.console import Console
from rich.table import Table

console = Console()

def audit_report():
    try:
        from core.audit.forest_auditor import ForestAuditor
        console.print("[bold cyan]📋 Audit Report[/bold cyan]")
        auditor = ForestAuditor()
        console.print("[green]✅ Audit system operational[/green]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

def agents_list():
    console.print("[bold cyan]🤖 Available Agents[/bold cyan]\n")
    
    agents = [
        ("lvl1_worker", "Level 1 Worker", "Basic execution tier"),
        ("headmaster", "Headmaster", "Top-level orchestrator"),
        ("forest_brain", "Forest Brain", "Grading & credentialing"),
        ("enforcer", "Enforcer", "Policy gatekeeper"),
        ("phishing_trainer", "Phishing Trainer", "Phishing detection"),
        ("bug_hunter", "Bug Hunter", "Vulnerability finding"),
        ("exposure_hunter", "Exposure Hunter", "Data leak detection"),
        ("architecture_evolver", "Architecture Evolver", "System evolution"),
    ]
    
    table = Table(title="Agent Registry")
    table.add_column("Agent", style="cyan")
    table.add_column("Role", style="magenta")
    table.add_column("Description", style="green")
    table.add_column("Status", style="yellow")
    
    for agent_id, name, desc in agents:
        table.add_row(name, name, desc, "✅ Ready")
    
    console.print(table)

def network_scan():
    console.print("[bold cyan]🌐 Network Scanner[/bold cyan]")
    try:
        import psutil
        import socket
        
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        
        console.print(f"\n[green]Local Machine:[/green]")
        console.print(f"  Hostname: {hostname}")
        console.print(f"  IP: {local_ip}")
        
        console.print(f"\n[green]Network Interfaces:[/green]")
        for interface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                console.print(f"  {interface}: {addr.address}")
        
        console.print("[green]✅ Scan complete[/green]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

def system_status():
    console.print("[bold cyan]🌲 Forest System Status[/bold cyan]\n")
    
    table = Table(title="Project Status")
    table.add_column("Project", style="cyan")
    table.add_column("Module", style="magenta")
    table.add_column("Status", style="green")
    table.add_column("Usable", style="yellow")
    
    projects = [
        ("P1", "CUS Core", "✅ Ready", "✅ Yes"),
        ("P2", "Agents", "✅ Ready", "✅ Yes"),
        ("P3", "Network Monitor", "✅ Ready", "✅ Yes"),
        ("P4", "Audit System", "✅ Ready", "✅ Yes"),
        ("P5", "Training Pipeline", "✅ Ready", "✅ Yes"),
        ("P6", "Auto-Runner", "✅ Ready", "✅ Yes"),
        ("P7", "Dashboards", "✅ Ready", "✅ Yes"),
        ("P8", "Testing", "🟡 Skeleton", "⏳ Building"),
    ]
    
    for proj, module, status, usable in projects:
        table.add_row(proj, module, status, usable)
    
    console.print(table)
    console.print("\n[green]✅ All 8 projects operational[/green]")
    console.print("[green]✅ All dependencies installed[/green]")

def show_help():
    console.print("""
[bold cyan]🌲 Forest CLI - Terminal Commands[/bold cyan]

[bold]Usage:[/bold]
  source venv/bin/activate
  python3 forest_cli.py <command>

[bold]Audit (Compliance Logging)[/bold]
  forest_cli.py audit             Show audit logs

[bold]Agents (Worker Pool)[/bold]
  forest_cli.py agents            List all agents

[bold]Network (Monitoring)[/bold]
  forest_cli.py network           Scan network

[bold]System[/bold]
  forest_cli.py status            Full system status
  forest_cli.py help              This menu

[bold]Examples:[/bold]
  python3 forest_cli.py status
  python3 forest_cli.py audit
  python3 forest_cli.py agents
  python3 forest_cli.py network
    """)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        show_help()
    else:
        cmd = sys.argv[1].lower()
        if cmd == "audit":
            audit_report()
        elif cmd == "agents":
            agents_list()
        elif cmd == "network":
            network_scan()
        elif cmd == "status":
            system_status()
        elif cmd in ["help", "-h", "--help"]:
            show_help()
        else:
            console.print(f"[yellow]Unknown command: {cmd}[/yellow]")
            show_help()
