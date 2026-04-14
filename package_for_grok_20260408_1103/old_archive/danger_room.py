import os
import getpass
import hashlib
import sys
import code
from datetime import datetime
from pathlib import Path

DANGER_LOG = Path.home() / "Forest" / "danger_room" / "logs" / "access.log"
DANGER_LOG.parent.mkdir(parents=True, exist_ok=True)

# Password set to ForlornHope1417
MASTER_PASSWORD_HASH = hashlib.sha256("ForlornHope1417".encode()).hexdigest()

def log_access(username, action, details=""):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(DANGER_LOG, "a") as f:
        f.write(f"[{timestamp}] User: {username} | Action: {action} | {details}\n")

def enter_danger_room():
    print("\n" + "="*70)
    print("DANGER ROOM PROTOCOL v3 - UNRESTRICTED")
    print("WARNING: Full privileges enabled. All actions are logged.")
    print("="*70 + "\n")

    password = getpass.getpass("Enter Danger Room password: ")
    if hashlib.sha256(password.encode()).hexdigest() != MASTER_PASSWORD_HASH:
        print("Access denied.")
        log_access("UNKNOWN", "FAILED ACCESS ATTEMPT")
        return

    username = input("Enter your identifier (for logging): ").strip() or "Creator"
    log_access(username, "ENTERED DANGER ROOM")

    print(f"\nAccess granted to {username} at {datetime.now()}")
    print("Type 'exit()' or Ctrl+D to leave safely.\n")

    local_vars = {
        "os": os,
        "Path": Path,
        "datetime": datetime,
        "VAULT_DIR": Path.home() / "ForestVault",
        "SANDBOX_DIR": Path.home() / "Forest" / "sandbox",
        "DANGER_DIR": Path.home() / "Forest" / "danger_room",
    }

    banner = "Danger Room Python REPL - Be extremely careful.\nAvailable: os, Path, VAULT_DIR, SANDBOX_DIR"
    code.interact(local=local_vars, banner=banner)

    log_access(username, "EXITED DANGER ROOM")
    print("Danger Room sealed.")

if __name__ == "__main__":
    enter_danger_room()
