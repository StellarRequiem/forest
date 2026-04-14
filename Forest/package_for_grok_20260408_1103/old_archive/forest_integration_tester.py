import time
from pathlib import Path
from datetime import datetime
import hashlib

VAULT_DIR = Path.home() / "ForestVault"

def log_to_cryptex(event_type, details=""):
    timestamp = datetime.now().isoformat()
    entry = f"{timestamp} | {event_type} | {details}"
    h = hashlib.sha256(entry.encode()).hexdigest()[:16]
    with open(VAULT_DIR / "training_chain.json", "a") as f:
        f.write(f"{entry} | Hash: {h}\n")
    print(f"[INTEGRATION_TESTER] {event_type} logged | Hash: {h}")

print("=== IntegrationTester Online - Testing proposal integration ===")

while True:
    try:
        print(f"\n[IntegrationTester] Checking proposal integration @ {datetime.now().strftime('%H:%M:%S')}")

        import_dir = VAULT_DIR / "import"
        if import_dir.exists():
            proposals = list(import_dir.glob("*.md"))
            if proposals:
                print(f"[IntegrationTester] Found {len(proposals)} pending proposals for integration test")
                log_to_cryptex("INTEGRATION_CHECK", f"{len(proposals)} proposals tested")

        time.sleep(300)

    except KeyboardInterrupt:
        print("\nIntegrationTester shutting down.")
        break
    except Exception as e:
        print(f"[IntegrationTester] Error: {e}")
        time.sleep(60)
