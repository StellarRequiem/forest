import time
from pathlib import Path
from datetime import datetime
import hashlib
import subprocess
import json
import sys

VAULT_DIR = Path.home() / "ForestVault"
LOG_DIR = VAULT_DIR / "network_logs"
LOG_DIR.mkdir(exist_ok=True)

# Expanded known hosts + your Mac
KNOWN_HOSTS = {
    "192.168.68.78": "This Machine (Alex's Mac)",
    "192.168.68.1":  "Router/Gateway",
    "b8:94:d9:9b:95:d": "This Machine (Alex's Mac)",   # your Wi-Fi MAC
}

# Local OUI / vendor database (expanded)
VENDOR_MAP = {
    "b8:94:d9": "Apple (Mac / iOS device)",
    "5c:a6:e6": "Router (common ISP equipment)",
    "c4:dd:57": "IoT / Camera",
    "44:0:49":  "Apple",
    "48:e1:e9": "Apple",
    "9c:76:13": "Apple",
    "34:3e:a4": "Apple",
    "e0:ac:cb": "Unknown IoT",
    "50:a6:d8": "Unknown",
}

def log_to_cryptex(event_type, details=""):
    timestamp = datetime.now().isoformat()
    entry = f"{timestamp} | {event_type} | {details}"
    h = hashlib.sha256(entry.encode()).hexdigest()[:16]
    with open(VAULT_DIR / "training_chain.json", "a") as f:
        f.write(f"{entry} | Hash: {h}\n")

def trace_device(identifier):
    """Safe local + optional Scout lookup for a single device/MAC/IP"""
    print(f"[Tracer] Looking up {identifier}...")
    # Local lookup first
    for ip_or_mac, name in KNOWN_HOSTS.items():
        if identifier in ip_or_mac:
            return f"✅ Known: {name}"
    for oui, vendor in VENDOR_MAP.items():
        if oui in identifier.lower():
            return f"✅ Local match: {vendor}"
    return f"⚠️ No local match for {identifier} — Scout air-lock can be used for public lookup if you approve."

def run_snapshot(deep=False):
    # ... (existing snapshot code stays the same, just call trace_device on unknowns if you want)
    # For now we keep it simple and fast
    timestamp = int(time.time())
    snapshot = {"type": "deep" if deep else "light", "timestamp": timestamp, "datetime": datetime.now().isoformat(),
                "devices": [], "known_devices": [], "unknown_devices": [], "suspicious_flags": []}

    try:
        arp = subprocess.run(["arp", "-a"], capture_output=True, text=True, timeout=15)
        raw_lines = [line.strip() for line in arp.stdout.splitlines() if line.strip()]
        for line in raw_lines:
            classified = classify_device(line)   # from previous version
            snapshot["devices"].append(f"{classified} | {line}")
            if "Unknown" in classified:
                snapshot["unknown_devices"].append(line)
            else:
                snapshot["known_devices"].append(line)
    except Exception as e:
        snapshot["devices"] = [f"Scan failed: {e}"]

    snapshot_file = LOG_DIR / f"{'deep_' if deep else 'light_'}{timestamp}.json"
    with open(snapshot_file, "w") as f:
        json.dump(snapshot, f, indent=2)

    print(f"[Network Watcher] Snapshot saved — {len(snapshot['known_devices'])} known, {len(snapshot['unknown_devices'])} unknown")
    log_to_cryptex("NETWORK_SNAPSHOT", f"{snapshot['type']} | Known: {len(snapshot['known_devices'])}")
    return snapshot_file

def classify_device(dev_line):
    dev_lower = dev_line.lower()
    for ip_or_mac, name in KNOWN_HOSTS.items():
        if ip_or_mac in dev_line:
            return name
    for oui, vendor in VENDOR_MAP.items():
        if oui in dev_lower:
            return f"{vendor} Device"
    return "Unknown Device"

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--trace":
        result = trace_device(sys.argv[2])
        print(result)
    elif len(sys.argv) > 1 and sys.argv[1] == "--oneshot":
        run_snapshot(deep=True)
    else:
        print("=== Network Watcher + Tracer Online ===")
        deep_counter = 0
        while True:
            try:
                run_snapshot(deep=False)
                deep_counter += 1
                if deep_counter >= 8:
                    run_snapshot(deep=True)
                    deep_counter = 0
                time.sleep(45)
            except KeyboardInterrupt:
                print("\nWatcher stopped.")
                break
            except Exception as e:
                print(f"Watcher error: {e}")
                time.sleep(30)
