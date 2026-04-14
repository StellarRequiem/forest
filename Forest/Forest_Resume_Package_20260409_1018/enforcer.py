#!/usr/bin/env python3
"""
Forest Enforcer v3.0 — Ruthless, Real, CUS-Aligned
Kills bad actors, blocks unsigned actions, forces human gate when needed.
"""

import subprocess
import psutil
import time
from pathlib import Path
from datetime import datetime
import hashlib
import os

VAULT_DIR = Path.home() / "ForestVault"
VAULT_DIR.mkdir(exist_ok=True)
CRYPTEX_FILE = VAULT_DIR / "training_chain.json"

def log_to_cryptex(event_type: str, details: str = ""):
    timestamp = datetime.now().isoformat()
    entry = f"{timestamp} | {event_type} | {details}"
    h = hashlib.sha256(entry.encode()).hexdigest()[:24]
    with open(CRYPTEX_FILE, "a") as f:
        f.write(f"{entry} | Hash: {h}\n")
    print(f"[ENFORCER] {event_type} | {details[:80]}... | Hash: {h}")

class EnforcerTeam:
    def __init__(self):
        self.blocked_count = 0

    def scan_swarm(self, status: dict = None):
        print("[ENFORCER] Scanning active tmux sessions and processes...")
        try:
            result = subprocess.run(["tmux", "ls"], capture_output=True, text=True)
            sessions = [line.split(":")[0] for line in result.stdout.splitlines() if line.strip()]
            
            for sess in sessions:
                if "forest" in sess.lower() or sess in ["brain", "mouth", "forge", "warden", "cusbrain"]:
                    continue
                print(f"[ENFORCER] Killing suspicious session: {sess}")
                subprocess.run(["tmux", "kill-session", "-t", sess], stdout=subprocess.DEVNULL)
                log_to_cryptex("SESSION_KILLED", sess)
                self.blocked_count += 1
        except Exception as e:
            log_to_cryptex("SCAN_ERROR", str(e))

        # Light process check
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmd = ' '.join(proc.info['cmdline'] or [])
                if "ollama" in cmd and "--danger" in cmd:
                    print(f"[ENFORCER] Killing dangerous Ollama process {proc.info['pid']}")
                    proc.kill()
                    log_to_cryptex("PROCESS_KILLED", f"pid:{proc.info['pid']}")
            except:
                pass
        return {"status": "scanned", "blocked": self.blocked_count}

    def approve(self, action: str) -> bool:
        print(f"\n🔒 ENFORCER GATE: {action}")
        print("Type 'yes' to approve, anything else to BLOCK.")
        try:
            choice = input("ENFORCER APPROVE? > ").strip().lower()
            if choice == "yes":
                log_to_cryptex("ACTION_APPROVED", action[:100])
                return True
            else:
                log_to_cryptex("ACTION_BLOCKED", action[:100])
                self.blocked_count += 1
                return False
        except:
            log_to_cryptex("ACTION_BLOCKED", "input failed")
            return False

    def enforce_constitution(self, output: str) -> bool:
        bad_phrases = ["hack", "steal", "phish real user", "install malware", "ddos"]
        if any(phrase in output.lower() for phrase in bad_phrases):
            log_to_cryptex("CONSTITUTION_VIOLATION", output[:80])
            return False
        return True

enforcer = EnforcerTeam()

print("=== Forest Enforcer v3.0 Loaded — Ruthless Mode Active ===")
