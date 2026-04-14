#!/usr/bin/env python3
"""
Forest Auto-Runner v1.14 — Full stack with ForestForge, ScenarioMutator, dynamic scaling, launchd-ready
"""

import time
import sys
import json
import subprocess
import psutil
from pathlib import Path
from cus_langgraph import run_cus_swarm
from the_well import TheWellWorker
from self_improver import SelfImproverWorker
from bug_hunter import BugBountyHunter
from exposure_hunter import ExposureHunter
from architecture_evolver import ArchitectureEvolver
from forest_forge import ForestForge
from scenario_mutator import ScenarioMutator
from forest_auditor import ForestAuditor
from datetime import datetime, timedelta

print(f"🌲 Forest Auto-Runner v1.14 started at {datetime.now()}")
print("Full audacious stack with dynamic scaling")

VAULT = Path.home() / "ForestVault"
LAST_AUDIT_FILE = VAULT / "last_audit.json"

cycle = 0
last_audit_time = None

if LAST_AUDIT_FILE.exists():
    try:
        with open(LAST_AUDIT_FILE, "r") as f:
            data = json.load(f)
            last_audit_time = datetime.fromisoformat(data["last_audit"])
    except:
        pass

while True:
    cycle += 1
    now = datetime.now()

    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory().percent
    load_score = (cpu + ram) / 2

    if load_score < 50:
        rounds = 2
    elif load_score < 75:
        rounds = 1
    else:
        rounds = 1

    print(f"\n=== PARALLEL AUTO CYCLE {cycle} @ {now.strftime('%H:%M:%S')} === Load: {load_score:.1f}% → {rounds} rounds per tester")

    try:
        well = TheWellWorker()
        if well.activate():
            well.perform_task()
    except Exception as e:
        print(f"   → Well skipped: {e}")

    for i in range(rounds):
        for organ in [SelfImproverWorker, BugBountyHunter, ExposureHunter, ArchitectureEvolver, ForestForge, ScenarioMutator]:
            try:
                name = organ.__name__.replace("Worker", "").replace("Hunter", "").replace("Evolver", "").replace("Forge", "").replace("Mutator", "")
                print(f"[PARALLEL] {name} round {i+1}/{rounds}...")
                o = organ()
                if o.activate():
                    o.perform_task()
            except Exception as e:
                print(f"   → {name} skipped: {e}")

    if last_audit_time is None or (now - last_audit_time) > timedelta(hours=24):
        try:
            print("[BACKGROUND AUDIT] Launching ForestAuditor...")
            subprocess.Popen(["python", "forest_auditor.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            last_audit_time = now
            with open(LAST_AUDIT_FILE, "w") as f:
                json.dump({"last_audit": now.isoformat()}, f)
        except Exception as e:
            print(f"   → Background audit failed: {e}")

    try:
        task = "Parallel red vs blue battle cycle with latest recursive + exposure + forge + mutator techniques"
        result = run_cus_swarm(level=1, task=task, background_mode=True)
        print(f"   → CUS parallel cycle complete")
    except Exception as e:
        print(f"   → CUS error: {e}")

    time.sleep(45)
