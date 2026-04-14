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
    print(f"[MODEL_EVALUATOR] {event_type} logged | Hash: {h}")

print("=== ModelEvaluator Online - Scoring trainer performance ===")

while True:
    try:
        print(f"\n[ModelEvaluator] Evaluating models @ {datetime.now().strftime('%H:%M:%S')}")

        sessions_file = VAULT_DIR / "dynamic_sessions.json"
        if sessions_file.exists():
            with open(sessions_file) as f:
                sessions = json.load(f)
            if sessions:
                recent = sessions[-20:]
                avg_accuracy = sum(s.get("percentage", 0) for s in recent) / len(recent)
                print(f"[ModelEvaluator] Recent avg accuracy: {avg_accuracy:.1f}%")
                if avg_accuracy < 75:
                    log_to_cryptex("MODEL_WARNING", f"Low accuracy trend: {avg_accuracy:.1f}% - suggest retraining")
                    suggestion_file = VAULT_DIR / f"model_suggestion_{int(time.time())}.md"
                    with open(suggestion_file, "w") as f:
                        f.write(f"# ModelEvaluator Suggestion - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
                        f.write(f"Recent trainer accuracy trending low ({avg_accuracy:.1f}%). Recommend focusing Forge on weak trainers.\n")
                    print(f"[ModelEvaluator] Suggestion saved: {suggestion_file.name}")

        time.sleep(300)  # every 5 minutes

    except KeyboardInterrupt:
        print("\nModelEvaluator shutting down.")
        break
    except Exception as e:
        print(f"[ModelEvaluator] Error: {e}")
        time.sleep(60)
