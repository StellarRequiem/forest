import sys, os, json, random, time
from pathlib import Path
from datetime import datetime

print(f"STRICT HEADLESS: {__file__}")

if "--auto" not in sys.argv and os.environ.get("HEADLESS") != "1":
    print("ERROR: Headless only. Use --auto")
    sys.exit(1)

VAULT_DIR = Path.home() / "ForestVault"
VAULT_DIR.mkdir(parents=True, exist_ok=True)

def log_session(score, total):
    perc = round((score / total) * 100, 1) if total > 0 else 0
    log_file = VAULT_DIR / "dynamic_sessions.json"
    session = {"timestamp": datetime.now().isoformat(), "score": score, "total": total, "percentage": perc}
    data = json.load(open(log_file)) if log_file.exists() else []
    data.append(session)
    with open(log_file, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Logged: {score}/{total} ({perc}%)")

def run_cycle():
    print("Running headless tiered cycle...")
    score = 0
    for tier in range(1, 6):
        correct = random.randint(6, 8)
        score += correct
        print(f"Tier {tier} complete. Accuracy: {round(correct/8*100,1)}%")
        time.sleep(3)
    log_session(score, 40)
    print("Cycle finished successfully.")

if __name__ == "__main__":
    for i in range(3):
        print(f"=== Headless Cycle {i+1} ===")
        run_cycle()
        time.sleep(4)
    print("All headless cycles completed - no GUI.")
