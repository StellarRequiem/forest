#!/usr/bin/env python3
"""
Forest CUS Launcher — Starts the new CUS LangGraph v3.4 as the main brain
"""

import time
import subprocess
from pathlib import Path

print("=== Forest CUS Brain Launcher v1.0 ===")
print("Starting CUS LangGraph v3.4 as primary brain...")

try:
    # Run the CUS graph in a loop (or as a long-running process)
    while True:
        print("\n=== Starting new CUS Cycle ===")
        result = subprocess.run(["python", "cus_langgraph.py"], 
                              capture_output=False, 
                              text=True, 
                              check=True)
        print("Cycle completed. Waiting 60s before next cycle...")
        time.sleep(60)  # Run a cycle every minute for now
except KeyboardInterrupt:
    print("\nCUS Brain stopped by user.")
except Exception as e:
    print(f"Error in CUS brain: {e}")
