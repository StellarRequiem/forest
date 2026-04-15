#!/usr/bin/env python3
"""
Forest Brain v2.2 — realistic varied grading
"""

import hashlib
from datetime import datetime
from pathlib import Path

VAULT_DIR = Path.home() / "ForestVault"
VAULT_DIR.mkdir(exist_ok=True)
CRYPTEX_FILE = VAULT_DIR / "training_chain.json"

def log_chain(event_type: str, details: str = ""):
    timestamp = datetime.now().isoformat()
    entry = f"{timestamp} | {event_type} | {details}"
    h = hashlib.sha256(entry.encode()).hexdigest()[:24]
    with open(CRYPTEX_FILE, "a") as f:
        f.write(f"{entry} | Hash: {h}\n")
    print(f"[BRAIN] {event_type} logged | Hash: {h}")

def spawn_agent(name: str, model: str, role: str):
    credential = f"{name}|cred-{name}-{int(datetime.now().timestamp())}"
    print(f"[BRAIN] Spawned {name} ({model})")
    return credential

print("=== Forest Brain v2.2 Loaded ===")
