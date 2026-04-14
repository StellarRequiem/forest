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
    print(f"[PROMPT_AUDITOR] {event_type} logged | Hash: {h}")

print("=== Prompt Auditor Online - Reducing hallucination ===")

while True:
    try:
        print(f"\n[Prompt Auditor] Reviewing prompts @ {datetime.now().strftime('%H:%M:%S')}")
        result = subprocess.run(["ollama", "run", "qwen2:0.5b", "Review recent Forest prompts and suggest 2-3 small improvements to reduce hallucination."], capture_output=True, text=True, timeout=50)
        output = result.stdout.strip()
        if output:
            file = VAULT_DIR / f"prompt_suggestion_{int(time.time())}.md"
            with open(file, "w") as f:
                f.write(f"# Prompt Auditor Suggestion - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n{output}")
            print(f"[Prompt Auditor] Suggestion saved: {file.name}")
            log_to_cryptex("PROMPT_SUGGESTION", file.name)
        time.sleep(180)
    except KeyboardInterrupt:
        break
    except Exception as e:
        print(f"[Prompt Auditor] Error: {e}")
        time.sleep(60)
