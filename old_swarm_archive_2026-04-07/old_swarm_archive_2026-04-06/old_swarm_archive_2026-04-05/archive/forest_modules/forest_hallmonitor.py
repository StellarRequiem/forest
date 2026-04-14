import subprocess
import time
from pathlib import Path
from datetime import datetime
import hashlib
import psutil

VAULT_DIR = Path.home() / "ForestVault"

def log_to_cryptex(event_type, details=""):
    timestamp = datetime.now().isoformat()
    entry = f"{timestamp} | {event_type} | {details}"
    h = hashlib.sha256(entry.encode()).hexdigest()[:16]
    with open(VAULT_DIR / "training_chain.json", "a") as f:
        f.write(f"{entry} | Hash: {h}\n")
    print(f"[CRYPTEX] {event_type} logged | Hash: {h}")

def describe_file(f):
    name = f.name
    if name.startswith("purged_proposed_real_"):
        return "Old proposed scenario file (previously purged)"
    elif name.startswith("denied_"):
        return "Previously denied Forge or mouth proposal"
    elif name.startswith("old_"):
        return "Old backup or renamed file"
    elif "forge_proposal" in name:
        return "Forge self-improvement proposal (in sandbox)"
    else:
        return "Unknown redundant file"

def deep_scan():
    print(f"\n[HALL MONITOR] Deep scan started @ {datetime.now().strftime('%H:%M:%S')}")

    # Check redundant files
    redundant = list(VAULT_DIR.glob("denied_*")) + list(VAULT_DIR.glob("purged_*")) + list(VAULT_DIR.glob("old_*"))
    
    if not redundant:
        print("No redundant files found.")
        return

    print(f"\nFound {len(redundant)} potentially redundant files:")
    for i, f in enumerate(redundant, 1):
        desc = describe_file(f)
        print(f"  {i}. {f.name}  →  {desc}")

    choice = input("\nPurge ALL these files? (yes/no/skip): ").strip().lower()
    if choice == "yes":
        purged_count = 0
        for f in redundant:
            try:
                f.unlink()
                print(f"Purged: {f.name}")
                log_to_cryptex("PURGED_REDUNDANT", f.name)
                purged_count += 1
            except Exception as e:
                print(f"Failed to purge {f.name}: {e}")
        print(f"\nPurged {purged_count} files.")
        log_to_cryptex("BATCH_PURGE_COMPLETE", f"{purged_count} files")
    else:
        print("No files purged.")

    print("[HALL MONITOR] Scan complete.")

print("=== Forest Hall Monitor - Interactive with File Descriptions ===")
print("Commands: scan, status, exit\n")

while True:
    try:
        cmd = input("Hall> ").strip().lower()
        if cmd in ["exit", "quit"]:
            print("Hall Monitor shutting down.")
            break
        elif cmd in ["scan", "test"]:
            deep_scan()
        elif cmd == "status":
            print("Status: Hall Monitor running. Use 'scan' to audit.")
        else:
            print("Available: scan, status, exit")
    except KeyboardInterrupt:
        print("\nInterrupted.")
        break
    except Exception as e:
        print(f"Error: {e}")
