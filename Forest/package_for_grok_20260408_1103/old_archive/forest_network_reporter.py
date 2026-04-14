import time
from pathlib import Path
from datetime import datetime
import json
import sys

VAULT_DIR = Path.home() / "ForestVault"
LOG_DIR = VAULT_DIR / "network_logs"

def get_latest_snapshot(deep=False):
    prefix = "deep_" if deep else "light_"
    snapshots = sorted(LOG_DIR.glob(f"{prefix}*.json"))
    if not snapshots:
        return {"error": "No snapshots collected yet. Run a live scan first."}
    latest = snapshots[-1]
    for attempt in range(8):
        try:
            with open(latest) as f:
                data = json.load(f)
            return data
        except:
            time.sleep(0.3)
    return {"error": "Snapshot exists but could not be read."}

def format_report(snapshot):
    if "error" in snapshot:
        return snapshot["error"]

    devices = snapshot.get("devices", [])
    flags = snapshot.get("suspicious_flags", [])
    timestamp = snapshot.get("datetime", "unknown")

    known = []
    unknown = []
    for d in devices:
        if "router" in d.lower() or "gateway" in d.lower():
            known.append(d)
        else:
            unknown.append(d)

    report = f"Network Report - {timestamp}\n"
    report += f"Total devices detected: {len(devices)}\n"
    report += f"Known devices (router/gateway): {len(known)}\n"
    report += f"Unknown/unresolved devices: {len(unknown)}\n"
    report += f"Suspicious flags: {len(flags)}\n\n"

    if flags:
        report += "Suspicious signals:\n"
        for f in flags:
            report += f"  • {f}\n"
        report += "\n"

    report += "Recent devices (first 25):\n"
    for d in devices[:25]:
        report += f"  • {d}\n"
    if len(devices) > 25:
        report += "  ... and more\n"

    return report

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--report":
        snapshot = get_latest_snapshot(deep=True)
        print(format_report(snapshot))
    else:
        print("=== Network Reporter Online ===")
        print("Use --report for formatted reports")
