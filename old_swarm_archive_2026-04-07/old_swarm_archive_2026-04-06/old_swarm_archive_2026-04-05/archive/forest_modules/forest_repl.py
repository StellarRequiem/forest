import json
from pathlib import Path
import time
from datetime import datetime
import hashlib
import re

VAULT_DIR = Path.home() / "ForestVault"
FORGE_SANDBOX = VAULT_DIR / "forge_sandbox"
IMPORT_DIR = VAULT_DIR / "import"
IMPORT_DIR.mkdir(exist_ok=True)

def log_to_cryptex(event_type, details=""):
    timestamp = datetime.now().isoformat()
    entry = f"{timestamp} | {event_type} | {details}"
    h = hashlib.sha256(entry.encode()).hexdigest()[:16]
    with open(VAULT_DIR / "training_chain.json", "a") as f:
        f.write(f"{entry} | Hash: {h}\n")
    print(f"[CRYPTEX] {event_type} logged | Hash: {h}")

def clean_summary(text):
    # Aggressive removal of thinking text
    text = re.sub(r'Thinking\.\.\..*?done thinking\.', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'Okay, let.*?\.\.\.', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'First, I need to.*?\.', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'I should.*?\.', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'Let me start by.*?\.', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'Let me try to figure out.*?\.', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'Since I don\'t have the actual code.*?\.', '', text, flags=re.DOTALL | re.IGNORECASE)

    # Keep lines that look like actual suggestions
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    useful = []
    for line in lines:
        if any(k in line.lower() for k in ["improve", "fix", "add", "update", "change", "refactor", "audit", "error handling", "input validation", "logging"]):
            useful.append(line)
    if useful:
        return '\n'.join(useful[:10])
    return text[:600]  # fallback

def show_status():
    bank_file = VAULT_DIR / "question_bank.json"
    bank_size = len(json.load(open(bank_file))) if bank_file.exists() else 0
    print(f"\n=== Forest Status ===")
    print(f"Question Bank: {bank_size} scenarios")
    print("Forge proposals waiting in forge_sandbox/")
    print("Type 'approve' to review one by one.")

def approve_proposed():
    forge_files = sorted(FORGE_SANDBOX.glob("forge_proposal_*.md"))
    if not forge_files:
        print("No Forge proposals in sandbox right now.")
        return

    print(f"\nFound {len(forge_files)} Forge proposals. Reviewing one by one.\n")

    for f in forge_files:
        try:
            with open(f) as fh:
                raw = fh.read(2000)
            summary = clean_summary(raw)
            
            print(f"\nProposal: {f.name}")
            print("What it does:")
            print(summary)
            print("-" * 60)

            while True:
                choice = input("Approve this idea? (yes / no / skip): ").strip().lower()
                if choice in ["yes", "no", "skip"]:
                    break
                print("Please answer yes, no, or skip.")

            if choice == "yes":
                log_to_cryptex("HUMAN_APPROVED_IDEA", f"{f.name} - Approved")
                f.rename(IMPORT_DIR / f.name)
                print(f"✅ Approved and moved to import/: {f.name}")
            elif choice == "no":
                log_to_cryptex("HUMAN_DENIED_IDEA", f"{f.name}")
                f.rename(VAULT_DIR / f"denied_{f.name}")
                print(f"❌ Denied and archived: {f.name}")
            else:
                print(f"Skipped: {f.name}")

        except Exception as e:
            print(f"Error reading {f.name}: {e}")

    print("\nReview session complete.")

while True:
    try:
        cmd = input("\nForest> ").strip()
        if not cmd:
            continue
        if cmd.lower() in ["exit", "quit"]:
            print("REPL shutting down.")
            break
        elif cmd.lower() == "status":
            show_status()
        elif cmd.lower() == "approve":
            approve_proposed()
        else:
            print("Available: status, approve, exit")
    except KeyboardInterrupt:
        print("\nInterrupted.")
        break
    except Exception as e:
        print(f"Error: {e}")
