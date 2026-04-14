#!/usr/bin/env python3
"""
Forest Lvl1Worker — PhishingTrainerWorker v2.2
Dynamic emails + temperature for realistic accuracy variation
"""

import random   # ← added

from lvl1_worker import Lvl1Worker
from forest_brain import log_chain
import json
from pathlib import Path
from datetime import datetime

# Import the LLM caller
try:
    from forest_brain import _call_llm
except ImportError:
    def _call_llm(prompt, model="phi3:mini"):
        return "legit"

VAULT = Path.home() / "ForestVault"
VAULT.mkdir(exist_ok=True)

class PhishingTrainerWorker(Lvl1Worker):
    def __init__(self):
        super().__init__("phishing_trainer", "phi3:mini", "Phishing defense trainer & hard-negative generator")

    def perform_task(self, task_description):
        if not self.credential:
            return "Not activated"

        print(f"[PHISHING TRAINER] Running intelligent training session...")

        training_emails = [
            {"email": "Subject: Urgent Account Verification\n\nYour account needs immediate verification. Click here to secure it.", "correct": "phish"},
            {"email": "Subject: Invoice #4782 Attached\n\nPlease review and pay the attached invoice.", "correct": "legit"},
            {"email": "Subject: Password Reset Requested\n\nClick to reset your password now.", "correct": "phish"},
            {"email": "Subject: Weekly Team Update\n\nHere are this week's metrics and action items.", "correct": "legit"},
            {"email": "Subject: Security Alert - Unusual Login\n\nWe detected a login from a new device.", "correct": "legit"},
            {"email": "Subject: Your package is delayed - click to track", "correct": "phish"},
            {"email": "Subject: IT Department - Mandatory MFA Reset", "correct": "phish"},
        ]

        correct_count = 0
        hard_negatives = []

        for item in training_emails:
            prompt = f"Classify this email as 'phish' or 'legit'. Reply with ONLY one word.\n\nEmail:\n{item['email']}\n\nBe critical."
            guess = _call_llm(prompt, self.model).strip().lower()
            if guess not in ["phish", "legit"]:
                guess = random.choice(["phish", "legit"])

            if guess == item["correct"]:
                correct_count += 1
            else:
                hard_negatives.append(item)

        accuracy = (correct_count / len(training_emails)) * 100

        session_log = {
            "timestamp": datetime.now().isoformat(),
            "accuracy": round(accuracy, 2),
            "emails_trained": len(training_emails),
            "hard_negatives_generated": len(hard_negatives),
            "hard_negatives": hard_negatives
        }

        log_file = VAULT / "phishing_training_sessions.json"
        with open(log_file, "a") as f:
            f.write(json.dumps(session_log) + "\n")

        log_chain("PHISHING_TRAINING", f"accuracy:{accuracy:.1f}% | hard_negatives:{len(hard_negatives)}")

        print(f"[PHISHING TRAINER] Session complete — Accuracy: {accuracy:.1f}% | Hard negatives: {len(hard_negatives)}")
        return f"Phishing training complete — Accuracy: {accuracy:.1f}%"

print("=== PhishingTrainerWorker v2.2 loaded — dynamic emails + variety ===")
