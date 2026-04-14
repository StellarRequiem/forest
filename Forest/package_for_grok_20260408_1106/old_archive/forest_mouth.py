import subprocess
from pathlib import Path
import json
import re
import time
from datetime import datetime

VAULT_DIR = Path.home() / "ForestVault"
LOG_DIR = VAULT_DIR / "network_logs"
MEMORY_FILE = VAULT_DIR / "mouth_history.json"

def load_memory():
    if MEMORY_FILE.exists():
        try:
            with open(MEMORY_FILE) as f:
                return json.load(f)
        except:
            return []
    return []

def save_memory(history):
    if len(history) > 80:
        history = history[-80:]
    with open(MEMORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def trigger_live_scan(deep=False):
    print("Mouth: Triggering live network scan...")
    mode = "--deep" if deep else "--oneshot"
    try:
        result = subprocess.run(["python", "forest_network_watcher.py", mode], capture_output=True, text=True, timeout=90)
        if result.returncode == 0:
            print("Live scan completed.")
            time.sleep(1.0)
            return True
        else:
            return False
    except Exception as e:
        print(f"Live scan error: {e}")
        return False

def get_network_report():
    try:
        result = subprocess.run(["python", "forest_network_reporter.py", "--report"], capture_output=True, text=True, timeout=15)
        return result.stdout.strip()
    except Exception as e:
        return f"Report generation failed: {e}"

print("=== Forest Mouth Online - Clean & Readable Reports ===")
print("Say 'do a live scan', 'run deep scan', 'what is on my network?'\n")

history = load_memory()

while True:
    try:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ["exit", "quit"]:
            print("Mouth shutting down.")
            break

        lower = user_input.lower()

        if any(p in lower for p in ["live scan", "network scan", "deep scan", "fresh scan", "scan the network"]):
            deep = "deep" in lower
            success = trigger_live_scan(deep=deep)
            if success:
                response = get_network_report()
            else:
                response = "Live scan failed to complete."
        else:
            recent = "\n".join([f"You: {h['user']}\nForest: {h['forest']}" for h in history[-8:]])

            full_prompt = f"""You are Forest. Use the latest network report when asked.

Recent conversation:
{recent}

User: {user_input}

Rules:
- Be concise and helpful.
- Only report real data.
- Never invent information.

Output ONLY the final response."""

            result = subprocess.run(["ollama", "run", "qwen3:8b", full_prompt], capture_output=True, text=True, timeout=70)
            response = result.stdout.strip()
            response = re.sub(r'Thinking\.\.\..*?done thinking\.', '', response, flags=re.DOTALL | re.IGNORECASE).strip()

        print(f"Forest: {response}")

        history.append({"user": user_input, "forest": response})
        save_memory(history)

    except KeyboardInterrupt:
        print("\nInterrupted.")
        break
    except Exception as e:
        print(f"Error: {e}")
