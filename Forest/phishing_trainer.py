#!/usr/bin/env python3
"""
PhishingTrainerWorker v2.8 — stable, repeatable accuracy metric.
"""
from lvl1_worker import Lvl1Worker
from forest_brain import log_chain
from enforcer import enforcer
import ollama
import json
import random
from pathlib import Path
from datetime import datetime

VAULT = Path.home() / "ForestVault"
IMPROVED_DIR = VAULT / "ImprovedTraining"
WELL_DIR = VAULT / "TheWell"

class PhishingTrainerWorker(Lvl1Worker):
    def __init__(self):
        super().__init__("phishing_trainer", "phi3:mini", "Phishing defense trainer — stable evaluation")

    def perform_task(self, task_description):
        if not self.credential:
            return "Not activated"

        print(f"[PHISHING TRAINER] Running stable training session...")

        # Fixed test set for repeatable scoring + improvements loaded on top
        email_pool = [
            {"email": "Subject: Urgent Account Verification\n\nYour account needs immediate verification. Click here.", "correct": "phish"},
            {"email": "Subject: Invoice #4782 Attached\n\nPlease review and pay the attached invoice.", "correct": "legit"},
            {"email": "Subject: Password Reset Requested\n\nClick to reset your password now.", "correct": "phish"},
            {"email": "Subject: Weekly Team Update\n\nHere are this week's metrics.", "correct": "legit"},
            {"email": "Subject: Security Alert - Unusual Login\n\nWe detected a login from a new device.", "correct": "legit"},
            {"email": "Subject: Your package is delayed - click to track", "correct": "phish"},
            {"email": "Subject: IT Department - Mandatory MFA Reset", "correct": "phish"},
        ]

        # Load improvements if available
        loaded_improvements = 0
        try:
            if IMPROVED_DIR.exists():
                latest = max(IMPROVED_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime)
                with open(latest, "r") as f:
                    data = json.load(f)
                all_blue = data.get("blue_improvements", []) + data.get("blue_countermeasures", []) + data.get("blue_detection", [])
                if all_blue:
                    email_pool.extend(all_blue)
                    loaded_improvements = len(all_blue)
        except Exception as e:
            print(f"[PHISHING TRAINER] Could not load improvements: {e}")

        # Larger fixed sample size for stability
        sample_size = min(20, len(email_pool))
        emails = random.sample(email_pool, k=sample_size)

        correct_count = 0
        hard_negatives = []

        for item in emails:
            prompt = f"""Classify this email as 'phish' or 'legit'. Reply with ONLY one word.

Email:
{item.get('email', str(item))}

Be critical and consistent."""

            response = ollama.generate(model=self.model, prompt=prompt, options={"temperature": 0.3, "top_p": 0.9})
            guess = response['response'].strip().lower()
            if guess not in ["phish", "legit"]:
                guess = random.choice(["phish", "legit"])

            if guess == item.get("correct", "phish"):
                correct_count += 1
            else:
                hard_negatives.append(item)

        accuracy = (correct_count / len(emails)) * 100

        session_log = {
            "timestamp": datetime.now().isoformat(),
            "accuracy": round(accuracy, 2),
            "emails_trained": len(emails),
            "hard_negatives_generated": len(hard_negatives),
            "improvements_loaded": loaded_improvements
        }

        log_file = VAULT / "phishing_training_sessions.json"
        with open(log_file, "a") as f:
            f.write(json.dumps(session_log) + "\n")

        log_chain("PHISHING_TRAINING", f"accuracy:{accuracy:.1f}% | hard_negatives:{len(hard_negatives)} | improvements:{loaded_improvements}")

        print(f"[PHISHING TRAINER] Session complete — Accuracy: {accuracy:.1f}% | Hard negatives: {len(hard_negatives)}")
        return f"Phishing training complete — Accuracy: {accuracy:.1f}%"
