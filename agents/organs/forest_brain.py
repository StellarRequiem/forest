#!/usr/bin/env python3
"""
Forest Brain v2.2 — realistic varied grading
"""

import hashlib
import random   # ← added
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

def cus_grade_and_reward(credential, blue_team_score=80, accuracy=80, compliance=90):
    if not credential:
        return {"grade": 0, "decision": "RECYCLE", "points": 0}

    if isinstance(credential, dict):
        credential_str = credential.get("credential", "unknown")
    else:
        credential_str = str(credential)

    final_score = (blue_team_score * 0.45) + (accuracy * 0.35) + (compliance * 0.2)
    final_score = round(final_score + random.uniform(-3, 3), 1)

    if final_score >= 85:
        decision = "PROMOTE"
        points = int(final_score * 30)
    elif final_score >= 70:
        decision = "STUDY"
        points = int(final_score * 15)
    else:
        decision = "RECYCLE"
        points = 0

    print(f"[BRAIN] {credential_str.split('|')[0]} graded {final_score:.1f}/100 → {decision} | Points: {points}")
    return {"grade": final_score, "decision": decision, "points": points}

print("=== Forest Brain v2.2 Loaded — realistic varied grading ===")
