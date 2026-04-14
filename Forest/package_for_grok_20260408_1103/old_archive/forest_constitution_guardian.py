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
    print(f"[CONSTITUTION_GUARDIAN] {event_type} logged | Hash: {h}")

print("=== ConstitutionGuardian Online - Auditing outputs for compliance ===")

while True:
    try:
        print(f"\n[ConstitutionGuardian] Auditing outputs @ {datetime.now().strftime('%H:%M:%S')}")

        prompt = """Review recent Forest outputs (Mouth, Forge, proposals) for compliance with core principles:
- Human autonomy first
- No harm, no coercion, no lying
- Ethical blue-team focus

Flag any violations or risks. Suggest fixes if needed.

Output only:
COMPLIANCE: [Status] - [Brief summary]"""

        result = subprocess.run(["ollama", "run", "phi3:mini", prompt], capture_output=True, text=True, timeout=50)
        output = result.stdout.strip()

        if output and "violation" in output.lower():
            log_to_cryptex("CONSTITUTION_VIOLATION", output[:100])
            print(f"[ConstitutionGuardian] Potential issue detected: {output[:80]}...")

        time.sleep(180)

    except KeyboardInterrupt:
        print("\nConstitutionGuardian shutting down.")
        break
    except Exception as e:
        print(f"[ConstitutionGuardian] Error: {e}")
        time.sleep(60)
