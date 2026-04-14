import time
from pathlib import Path
from datetime import datetime
import hashlib
import subprocess

VAULT_DIR = Path.home() / "ForestVault"

def log_to_cryptex(event_type, details=""):
    timestamp = datetime.now().isoformat()
    entry = f"{timestamp} | {event_type} | {details}"
    h = hashlib.sha256(entry.encode()).hexdigest()[:16]
    with open(VAULT_DIR / "training_chain.json", "a") as f:
        f.write(f"{entry} | Hash: {h}\n")
    print(f"[LOG_ANOMALY] {event_type} logged | Hash: {h}")

print("=== Log Anomaly Specialist Online ===")

while True:
    try:
        print(f"\n[Log Anomaly Specialist] Scanning logs @ {datetime.now().strftime('%H:%M:%S')}")
        result = subprocess.run(["ollama", "run", "phi3:mini", "Analyze recent network logs for suspicious patterns. Suggest 1-2 new training scenarios."], capture_output=True, text=True, timeout=50)
        output = result.stdout.strip()
        if output:
            file = VAULT_DIR / f"anomaly_suggestion_{int(time.time())}.md"
            with open(file, "w") as f:
                f.write(f"# Log Anomaly Suggestion - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n{output}")
            print(f"[Log Anomaly Specialist] Suggestion saved: {file.name}")
            log_to_cryptex("ANOMALY_SUGGESTION", file.name)
        time.sleep(210)
    except KeyboardInterrupt:
        break
    except Exception as e:
        print(f"[Log Anomaly Specialist] Error: {e}")
        time.sleep(60)
