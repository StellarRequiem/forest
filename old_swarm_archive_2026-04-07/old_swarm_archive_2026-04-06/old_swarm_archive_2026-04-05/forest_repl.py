#!/usr/bin/env python3
"""
Forest CUS REPL v2.1 — Now includes professional dashboard
"""

import sys
import time
from pathlib import Path

try:
    from forest_brain import spawn_agent, cus_grade_and_reward, print_reward_summary, log_chain
    from forest_dashboard import show_dashboard
except ImportError:
    print("ERROR: Missing core files. Run launcher first.")
    sys.exit(1)

def repl_help():
    print("\n=== Forest CUS REPL v2.1 ===")
    print("Commands:")
    print("  status / grade  - Show reward ledger")
    print("  dashboard       - Professional graphical overview")
    print("  spawn <name>    - Spawn agent (real y/n gate)")
    print("  swarm           - Trigger swarm cycle")
    print("  exit / quit     - Exit REPL")
    print("All actions gated by brain.\n")

def main():
    print("=== Forest CUS REPL v2.1 — Brain Directed ===")
    print("Type 'help' or 'dashboard' for overview.")
    print_reward_summary()

    while True:
        try:
            cmd = input("\nforest> ").strip().lower()
            
            if cmd in ["exit", "quit"]:
                print("Exiting REPL. Brain and swarm continue running.")
                break
            elif cmd == "help":
                repl_help()
            elif cmd in ["status", "grade"]:
                print_reward_summary()
            elif cmd == "dashboard":
                show_dashboard()
            elif cmd.startswith("spawn "):
                parts = cmd.split(maxsplit=1)
                if len(parts) < 2:
                    print("Usage: spawn <agent_name>")
                    continue
                name = parts[1]
                print(f"[REPL] Requesting spawn of {name} → routing to brain...")
                cred = spawn_agent(name, "phi3:mini", f"User-requested agent: {name}")
                if cred:
                    grade = cus_grade_and_reward(cred, blue_team_score=75, accuracy=70, compliance=90)
                    print(f"[REPL] Agent {name} spawned and graded successfully.")
            elif cmd == "swarm":
                print("[REPL] Triggering swarm cycle → brain will handle with human gate...")
                try:
                    from cus_langgraph import run_forest_swarm
                    run_forest_swarm()
                except Exception as e:
                    print(f"[REPL] Swarm trigger failed: {e}")
            else:
                print("Unknown command. Type 'help' or 'dashboard'.")
                
        except KeyboardInterrupt:
            print("\nExiting REPL...")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
