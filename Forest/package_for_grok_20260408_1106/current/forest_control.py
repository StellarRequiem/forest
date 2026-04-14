#!/usr/bin/env python3
"""
Forest Control v2.0 — Realigned under CUS Brain
High-level control interface that delegates to supervisor.
"""

from forest_supervisor import ForestSupervisor
from forest_brain import log_chain

class ForestControl:
    def __init__(self):
        self.supervisor = ForestSupervisor()

    def start_control(self):
        print("[CONTROL] Requesting system control activation → routing to brain...")
        if self.supervisor.activate():
            log_chain("CONTROL_ACTIVATED", "supervisor online")
            print("[CONTROL] System control active. Delegating to supervisor.")
            return True
        return False

    def run_cycle(self):
        print("[CONTROL] Running full control cycle...")
        self.supervisor.coordinate_cycle()
        log_chain("CONTROL_CYCLE_COMPLETE", "full cycle executed")
        print("[CONTROL] Cycle finished. All reports sent to brain.")

print("=== Forest Control v2.0 Loaded — Brain Gated ===")
