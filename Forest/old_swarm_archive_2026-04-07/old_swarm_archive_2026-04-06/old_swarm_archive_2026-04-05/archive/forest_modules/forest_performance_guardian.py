import time
from pathlib import Path
from datetime import datetime
import hashlib
import json

VAULT_DIR = Path.home() / "ForestVault"

def log_to_cryptex(event_type, details=""):
    timestamp = datetime.now().isoformat()
    entry = f"{timestamp} | {event_type} | {details}"
    h = hashlib.sha256(entry.encode()).hexdigest()[:16]
    with open(VAULT_DIR / "training_chain.json", "a") as f:
        f.write(f"{entry} | Hash: {h}\n")
    print(f"[PERF_GUARDIAN] {event_type} logged | Hash: {h}")

print("=== Performance Guardian Online ===")

while True:
    try:
        print(f"\n[Performance Guardian] Checking trainer performance @ {datetime.now().strftime('%H:%M:%S')}")
        sessions_file = VAULT_DIR / "dynamic_sessions.json"
        if sessions_file.exists():
            with open(sessions_file) as f:
                sessions = json.load(f)
            if sessions:
                recent = sessions[-10:]
                avg = sum(s.get("percentage", 0) for s in recent) / len(recent)
                print(f"Recent avg accuracy: {avg:.1f}%")
                if avg < 80:
                    log_to_cryptex("PERF_WARNING", f"Low accuracy: {avg:.1f}%")
        time.sleep(240)
    except KeyboardInterrupt:
        break
    except Exception as e:
        print(f"[Performance Guardian] Error: {e}")
        time.sleep(60)
