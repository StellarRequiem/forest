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
    print(f"[GROWTH_FORECASTER] {event_type} logged | Hash: {h}")

print("=== GrowthForecaster Online - Predicting future growth ===")

while True:
    try:
        print(f"\n[GrowthForecaster] Forecasting growth @ {datetime.now().strftime('%H:%M:%S')}")

        bank_file = VAULT_DIR / "question_bank.json"
        if bank_file.exists():
            with open(bank_file) as f:
                bank = json.load(f)
            current_size = len(bank)
            print(f"[GrowthForecaster] Current bank size: {current_size} scenarios")
            log_to_cryptex("GROWTH_FORECAST", f"Bank size: {current_size}")

        time.sleep(360)  # every 6 minutes

    except KeyboardInterrupt:
        print("\nGrowthForecaster shutting down.")
        break
    except Exception as e:
        print(f"[GrowthForecaster] Error: {e}")
        time.sleep(60)
