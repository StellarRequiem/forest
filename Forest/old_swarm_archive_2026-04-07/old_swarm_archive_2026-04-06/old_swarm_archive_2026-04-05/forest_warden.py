#!/usr/bin/env python3
"""
Forest Warden v2.0 — Realigned under CUS Brain
Monitoring and enforcement layer. All actions gated by brain.
"""

from lvl1_worker import Lvl1Worker, TelemetryGuardian
from forest_brain import log_chain
import time

class ForestWarden:
    def __init__(self):
        self.workers = []

    def activate_guard(self, guard_type="standard"):
        if guard_type == "telemetry":
            guard = TelemetryGuardian()
        else:
            guard = Lvl1Worker(f"warden_guard_{len(self.workers)+1}", "phi3:mini", "Warden monitoring agent — blue-team LVL1")
        
        if guard.activate():
            self.workers.append(guard)
            log_chain("WARDEN_GUARD_ACTIVATED", guard.name)
            return guard
        return None

    def patrol(self):
        print("[WARDEN] Starting patrol cycle under brain direction...")
        for guard in self.workers:
            result = guard.perform_task("Routine system integrity check")
            print(f"[WARDEN] {guard.name}: {result}")
        log_chain("WARDEN_PATROL_COMPLETE", f"{len(self.workers)} guards")
        print("[WARDEN] Patrol complete. Report sent to brain.")

# Simple hallmonitor wrapper for backward compatibility
class ForestHallmonitor:
    def __init__(self):
        self.warden = ForestWarden()

    def monitor(self):
        print("[HALLMONITOR] Activating monitoring via warden...")
        self.warden.patrol()

print("=== Forest Warden + Hallmonitor v2.0 Loaded — Brain Gated ===")
