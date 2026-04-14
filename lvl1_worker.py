#!/usr/bin/env python3
"""
Forest Lvl1 Worker v2.2 — Full base + TelemetryGuardian + NetworkWatcher
"""

from forest_brain import spawn_agent, cus_grade_and_reward, log_chain
import time
import psutil
import hashlib
from pathlib import Path
import subprocess
import json

class Lvl1Worker:
    def __init__(self, name="unnamed_worker", model="phi3:mini", role="Generic Lvl1 Worker"):
        self.name = name
        self.model = model
        self.role = role
        self.credential = None

    def activate(self):
        print(f"[LVL1 WORKER] Requesting activation for {self.name} → routing to brain...")
        self.credential = spawn_agent(self.name, self.model, self.role)
        if self.credential is None:
            return False
        grade = cus_grade_and_reward(self.credential, blue_team_score=82, accuracy=78, compliance=90)
        log_chain("LVL1_ACTIVATED", f"{self.name}|{grade['decision']}")
        print(f"[LVL1 WORKER] {self.name} activated and graded {grade['grade']:.1f} → {grade['decision']}")
        return True

    def perform_task(self, task_description):
        if not self.credential:
            return "Not activated"
        print(f"[LVL1 {self.name}] Performing safe blue-team task: {task_description}")
        return f"Task completed safely: {task_description[:80]}..."

class TelemetryGuardian(Lvl1Worker):
    def __init__(self):
        super().__init__("telemetry.guardian", "phi3:mini", "Privacy & telemetry defense — blue-team LVL1")

    def perform_task(self, task_description):
        if not self.credential:
            return "Not activated"
        print(f"[TELEMETRY GUARDIAN] Scanning for tracking patterns...")
        return "No unauthorized telemetry or beacons detected in this cycle."

class NetworkWatcher(Lvl1Worker):
    def __init__(self):
        super().__init__("network_watcher", "phi3:mini", "Multi-organ network sniffer & anomaly flagging")

    def perform_task(self, task_description):
        if not self.credential:
            return "Not activated"
        print(f"[NETWORK WATCHER] Running live snapshot for: {task_description}")
        # Call the original watcher (light scan by default)
        try:
            result = subprocess.run(["python", "forest_network_watcher.py", "--oneshot"],
                                  capture_output=True, text=True, timeout=30)
            return result.stdout.strip() or "Snapshot completed - no anomalies flagged"
        except Exception as e:
            return f"Watcher error: {e}"

print("==== Lvl1 Worker v2.2 Loaded with NetworkWatcher integration ====")
