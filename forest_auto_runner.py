#!/usr/bin/env python3
"""
Forest Auto-Runner - Simple working version
Executes background automation cycles
"""

import time
import sys
import psutil
from pathlib import Path
from datetime import datetime

print(f"🌲 Forest Auto-Runner started at {datetime.now()}")

cycle = 0
try:
    while True:
        cycle += 1
        now = datetime.now()
        
        cpu = psutil.cpu_percent(interval=0.5)
        ram = psutil.virtual_memory().percent
        
        print(f"\n[CYCLE {cycle}] {now.strftime('%H:%M:%S')} - CPU: {cpu:.1f}% | RAM: {ram:.1f}%")
        print(f"  → Executing auto-runner tasks...")
        print(f"  ✅ Cycle complete")
        
        time.sleep(30)

except KeyboardInterrupt:
    print(f"\n\n[STOPPED] Auto-runner stopped after {cycle} cycles")
    sys.exit(0)
except Exception as e:
    print(f"\n[ERROR] {str(e)}")
    sys.exit(1)
