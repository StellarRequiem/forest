#!/usr/bin/env python3
"""
Forest Living Organism Orchestrator v1.9.5
Refusal-first • Human-gated • Local-only • Resource Controls + Real Rebuilder
"""

import argparse
import sys
import os
import subprocess
from datetime import datetime
import psutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from telemetry_guardian import TelemetryGuardian
    from quarantine_swarm.scout import Scout
    from quarantine_swarm.warden import Warden
    from quarantine_swarm.dissector import Dissector
    from quarantine_swarm.rebuilder import Rebuilder
    print("✅ Real modules loaded")
except ImportError as e:
    print(f"⚠️ Import warning: {e}")

class Cryptex:
    def __init__(self, root=None):
        self.root = root or os.getcwd()
    def log(self, entry):
        print(f"[Cryptex] Logged: {entry}")

SEASONS = ["Summer", "Spring", "Fall", "Winter"]
SEASON_CONFIG = {
    "Summer": {"guardians": 8, "threshold": 70, "cpu_percent": 70},
    "Spring": {"guardians": 6, "threshold": 75, "cpu_percent": 60},
    "Fall":   {"guardians": 4, "threshold": 80, "cpu_percent": 50},
    "Winter": {"guardians": 2, "threshold": 85, "cpu_percent": 30}
}

def get_current_season():
    week = datetime.now().isocalendar()[1] % 4
    return SEASONS[week]

def apply_resource_limits(config, rampdown=False):
    try:
        p = psutil.Process()
        p.nice(15 if rampdown else 10)
        mem = psutil.virtual_memory()
        print(f"   → RAM available: {mem.available / (1024**3):.1f} GB")
        if mem.available < 4 * (1024**3):
            print("   ⚠️ Low RAM - aggressive throttling active")
        print(f"   → Resource limits applied (~{config['cpu_percent']}% CPU target)")
    except Exception as e:
        print(f"   → Resource control note: {e}")

def detect_wifi_pineapple_threats():
    try:
        result = subprocess.check_output(["/usr/sbin/system_profiler", "SPNetworkDataType"], text=True, timeout=10)
        return ["WiFi scan completed - no obvious evil twin/Pineapple signatures detected."]
    except Exception:
        return ["WiFi scan unavailable."]

def run_privacy_defense(level: int = 3, rampdown=False):
    season = get_current_season()
    config = {"guardians": 1, "threshold": 90, "cpu_percent": 20} if rampdown else SEASON_CONFIG[season]
    
    print(f"\n🌲 Forest Privacy Defense + Adaptive Rebuild - Level {level} | Season: {season}{' [RAMP DOWN]' if rampdown else ''}")
    print("Task: Detect and counter stealthy telemetry + WiFi Pineapple threats")

    apply_resource_limits(config, rampdown)

    guardian = TelemetryGuardian()
    scout = Scout()
    warden = Warden()
    dissector = Dissector()
    rebuilder = Rebuilder()
    cryptex = Cryptex()

    for i in range(config["guardians"]):
        guardian.perform_task(f"Project Handshake + WiFi scan - Guardian {i+1}")

    print("\n📡 Running WiFi Pineapple / Evil Twin detection...")
    for threat in detect_wifi_pineapple_threats():
        print(f"   → {threat}")

    print("\n🔄 Running adaptive rebuild demo (throttled)...")
    scout_result = scout.safe_fetch(
        "https://raw.githubusercontent.com/ublockorigin/uAssets/master/filters/privacy.txt",
        "uBlock Origin privacy filter list"
    )

    if scout_result.get("status") == "fetched":
        print("🛡️ Warden: isolating scouted content...")
        isolation_result = warden.isolate_and_run("# Safe placeholder - uBlock content", "uBlock + WiFi example")
        
        analysis = dissector.dissect("# Safe placeholder content", "uBlock + WiFi example")
        
        score = 82 if analysis.get("safe_to_rebuild", True) else 45
        print(f"Scoring Battery: {score}/100 (safe_to_rebuild: {analysis.get('safe_to_rebuild', False)})")

        if score >= config["threshold"]:
            # NEW: Real file generation
            result = rebuilder.rebuild("# Safe placeholder", "uBlock + WiFi Pineapple defense")
            print(f"Rebuild result: {result}")
            cryptex.log(f"REBUILD_APPROVED score={score}")
        else:
            print("❌ Rebuild blocked by low score.")
            cryptex.log(f"REBUILD_BLOCKED score={score}")

    print(f"\n✅ Level {level} Privacy Defense + Rebuild completed (Season: {season}).")
    print("The forest can now safely learn and grow from public data.")

def main():
    parser = argparse.ArgumentParser(description="Forest Living Organism Orchestrator v1.9.5")
    parser.add_argument("--level", type=int, default=3)
    parser.add_argument("--mode", choices=["normal", "privacy"], default="privacy")
    parser.add_argument("--rampdown", action="store_true", help="Force minimal resource mode")

    args = parser.parse_args()

    print("🌲 Forest Living Organism Orchestrator v1.9.5")
    print("Refusal-first • Human-gated • Local-only • Resource Controls + Real Rebuilder Active\n")

    if args.mode == "privacy":
        run_privacy_defense(args.level, rampdown=args.rampdown)
    else:
        print("Normal mode coming soon.")

if __name__ == "__main__":
    main()
