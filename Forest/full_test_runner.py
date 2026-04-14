#!/usr/bin/env python3
"""
Forest Full System Test v1.1 — Fixed counter
"""

import time
from cus_langgraph import run_cus_swarm
import json
from pathlib import Path

VAULT = Path.home() / "ForestVault"
LOG = VAULT / "training_chain.json"

def get_snapshot_count():
    if not LOG.exists():
        return 0
    with open(LOG, "r") as f:
        lines = f.readlines()
    return sum(1 for line in lines if "NETWORK_SNAPSHOT" in line)

def run_full_test():
    print("🌲 === FOREST FULL SYSTEM TEST v1.1 ===\n")
    initial_snapshots = get_snapshot_count()
    print(f"Starting snapshots in log: {initial_snapshots}\n")

    for i in range(5):
        print(f"\n=== CYCLE {i+1}/5 ===")
        try:
            result = run_cus_swarm(level=1, task="Blue-team monitoring cycle")
            print(f"   → Cycle complete: {len(result.get('understory_results', []))} organs")
        except Exception as e:
            print(f"   → Cycle error: {e}")
        time.sleep(2)

    final_snapshots = get_snapshot_count()
    new_snapshots = final_snapshots - initial_snapshots

    print("\n=== TEST COMPLETE ===")
    print(f"New NetworkWatcher snapshots logged: {new_snapshots}/5")
    print(f"Final log size: {LOG.stat().st_size / 1024:.1f} KB")
    print(f"Cryptex entries added: {new_snapshots * 2} (activation + snapshot)")

    if new_snapshots >= 5:
        print("✅ FULL INTEGRATION PASSED — Forest is alive and logging")
    else:
        print("⚠️ Partial pass — check tmux logs for issues")

if __name__ == "__main__":
    run_full_test()
