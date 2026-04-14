#!/usr/bin/env python3
"""
Forest Auto-Runner v1.3 — Metatron timer + robust handling
"""

import time
import sys
from cus_langgraph import run_cus_swarm
from datetime import datetime

print(f"🌲 Forest Auto-Runner v1.3 started at {datetime.now()}")
print("NetworkWatcher + PhishingTrainer run every 5 minutes")
print("Metatron red-team black box runs on its own timer (change METATRON_INTERVAL below)")

# ←←← CHANGE THIS TO SET METATRON TIMER (minutes)
METATRON_INTERVAL = 60

cycle = 0
metatron_timer = 0

while True:
    cycle += 1
    print(f"\n=== AUTO CYCLE {cycle} @ {datetime.now().strftime('%H:%M:%S')} ===")
    try:
        result = run_cus_swarm(level=1, task="Auto blue-team monitoring cycle", background_mode=True)
        print(f"   → Cycle complete: {len(result.get('understory_results', []))} organs")
    except KeyboardInterrupt:
        print("\nAuto-runner stopped by user.")
        sys.exit(0)
    except Exception as e:
        print(f"   → Cycle error: {e}")

    # Metatron timer logic
    metatron_timer += 5
    if metatron_timer >= METATRON_INTERVAL:
        print(f"   [METATRON TIMER] Running contained red-team cycle (every {METATRON_INTERVAL} min)")
        metatron_timer = 0

    time.sleep(300)  # 5 minutes — main CUS cycle timer
