#!/usr/bin/env python3
"""
Forest System Verification — checks ALL paths are working as intended.
Run this anytime to get a full health report.
"""
import os
import subprocess
from pathlib import Path
from datetime import datetime

VAULT = Path.home() / "ForestVault"
print("🌲 Forest Verification Report")
print("=" * 60)
print(f"Time: {datetime.now()}")
print()

def check_path(path, name, must_exist=True, executable=False):
    p = Path(path)
    if must_exist and not p.exists():
        print(f"❌ {name}: MISSING")
        return False
    if executable and p.exists() and not os.access(p, os.X_OK):
        print(f"⚠️  {name}: exists but not executable")
        return False
    print(f"✅ {name}: OK")
    return True

checks = [
    (VAULT, "ForestVault directory"),
    (VAULT / "TheWell", "TheWell nutrient directory"),
    (VAULT / "DailyReports", "DailyReports directory"),
    ("the_well.py", "TheWell script"),
    ("self_improver.py", "SelfImprover"),
    ("bug_hunter.py", "BugHunter"),
    ("exposure_hunter.py", "ExposureHunter"),
    ("architecture_evolver.py", "ArchitectureEvolver"),
    ("scenario_mutator.py", "ScenarioMutator"),
    ("forest_forge.py", "ForestForge"),
    ("forest_workday_runner.py", "Workday Runner"),
    ("forest_dashboard.py", "Dashboard"),
    ("enforcer.py", "Enforcer"),
    ("forest_brain.py", "Forest Brain"),
]

all_good = True
for path, name in checks:
    if not check_path(path, name):
        all_good = False

# tmux check
try:
    result = subprocess.run(["tmux", "ls"], capture_output=True, text=True, timeout=5)
    if "forest" in result.stdout:
        print("✅ tmux session 'forest': running")
    else:
        print("⚠️  tmux session 'forest': not found")
        all_good = False
except:
    print("❌ tmux command not found or not running")
    all_good = False

# Latest nutrient check
try:
    latest = max((VAULT / "TheWell").glob("nutrient_*.json"), key=lambda p: p.stat().st_mtime, default=None)
    if latest:
        print(f"✅ Latest nutrient: {latest.name} ({datetime.fromtimestamp(latest.stat().st_mtime)})")
    else:
        print("⚠️  No nutrients found")
        all_good = False
except:
    print("❌ Could not read TheWell directory")
    all_good = False

# Latest report
reports = list((VAULT / "DailyReports").glob("work_report_*.md"))
if reports:
    latest_report = max(reports, key=lambda p: p.stat().st_mtime)
    print(f"✅ Latest report: {latest_report.name}")
else:
    print("⚠️  No reports found")
    all_good = False

# Last Cryptex entry
try:
    with open(VAULT / "training_chain.json") as f:
        lines = f.readlines()
    if lines:
        print(f"✅ Last Cryptex entry: {lines[-1].strip()[:80]}...")
    else:
        print("⚠️  Cryptex log is empty")
        all_good = False
except:
    print("❌ Could not read Cryptex log")
    all_good = False

print("\n" + "=" * 60)
if all_good:
    print("✅ ALL PATHS ARE WORKING AS INTENDED")
    print("The Forest is healthy and ready for the next cycle.")
else:
    print("⚠️  Some paths need attention — check the errors above.")
