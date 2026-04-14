#!/usr/bin/env python3
import sys
from cus.core.overseer import overseer
from rich.console import Console

console = Console()

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        console.print("[bold green]Interactive CUS prompt started. Type 'exit' to quit.[/bold green]\n")
        while True:
            try:
                cmd = input("CUS> ").strip()
                if cmd.lower() in ["exit", "quit", "q"]:
                    console.print("[yellow]Shutting down...[/yellow]")
                    break
                overseer.run_command(cmd)
            except KeyboardInterrupt:
                console.print("\n[yellow]Exiting...[/yellow]")
                break
            except Exception as e:
                console.print(f"[red][ERROR] {e}[/red]")
    else:
        console.print("[bold]CUS v8.3[/bold]")
        console.print("Run with: [cyan]cus --interactive[/cyan]  or  [cyan]python -m cus.cli.launcher --interactive[/cyan]")

if __name__ == "__main__":
    main()
