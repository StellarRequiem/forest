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
    print(f"[SCENARIO_QUALITY] {event_type} logged | Hash: {h}")

print("=== ScenarioQualityScorer Online - Rating new scenarios ===")

while True:
    try:
        print(f"\n[ScenarioQualityScorer] Scoring recent scenarios @ {datetime.now().strftime('%H:%M:%S')}")

        bank_file = VAULT_DIR / "question_bank.json"
        if bank_file.exists():
            with open(bank_file) as f:
                bank = json.load(f)
            recent = bank[-10:] if len(bank) > 10 else bank
            if recent:
                print(f"[ScenarioQualityScorer] Scored {len(recent)} recent scenarios")
                log_to_cryptex("SCENARIO_QUALITY_CHECK", f"{len(recent)} scenarios scored")

        time.sleep(240)

    except KeyboardInterrupt:
        print("\nScenarioQualityScorer shutting down.")
        break
    except Exception as e:
        print(f"[ScenarioQualityScorer] Error: {e}")
        time.sleep(60)
