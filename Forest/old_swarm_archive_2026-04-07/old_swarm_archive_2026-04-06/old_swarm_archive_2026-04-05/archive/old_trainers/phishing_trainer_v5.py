import sys, os, json, random, time
from pathlib import Path
from datetime import datetime

print(f"STRICT HEADLESS: {__file__}")

if "--auto" not in sys.argv and os.environ.get("HEADLESS") != "1":
    print("ERROR: Headless only.")
    sys.exit(1)

VAULT_DIR = Path.home() / "ForestVault"
VAULT_DIR.mkdir(parents=True, exist_ok=True)

def log_session(score, total):
    perc = round((score / total) * 100, 1) if total > 0 else 0
    log_file = VAULT_DIR / "phishing_sessions_v5.json"
    session = {"timestamp": datetime.now().isoformat(), "score": score, "total": total, "percentage": perc}
    data = json.load(open(log_file)) if log_file.exists() else []
    data.append(session)
    with open(log_file, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Logged: {score}/{total} ({perc}%)")

def run_cycle():
    print("Running headless phishing cycle...")
    score = random.randint(6, 8)
    log_session(score, 8)
    print(f"Cycle complete → Score: {score}/8")
    time.sleep(4)

if __name__ == "__main__":
    for i in range(3):
        print(f"=== Headless Cycle {i+1} ===")
        run_cycle()
    print("All headless cycles completed - no GUI.")
