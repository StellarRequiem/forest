#!/usr/bin/env python3
"""
Forest Lvl1Worker — PhishingTrainerWorker v2.7
Reliable loading of ALL improvements from SelfImprover + BugHunter + ExposureHunter
"""

import random
import json
from pathlib import Path
from datetime import datetime
from lvl1_worker import Lvl1Worker
from forest_brain import log_chain
import ollama

VAULT = Path.home() / "ForestVault"
WELL_DIR = VAULT / "TheWell"
IMPROVED_DIR = VAULT / "ImprovedTraining"

class PhishingTrainerWorker(Lvl1Worker):
    def __init__(self):
        super().__init__("phishing_trainer", "phi3:mini", "Phishing defense trainer & hard-negative generator")

    def perform_task(self, task_description):
        if not self.credential:
            return "Not activated"

        print(f"[PHISHING TRAINER] Running intelligent training session...")

        email_pool = [
            {"email": "Subject: Urgent Account Verification\n\nYour account needs immediate verification. Click here.", "correct": "phish"},
            {"email": "Subject: Invoice #4782 Attached\n\nPlease review and pay the attached invoice.", "correct": "legit"},
            {"email": "Subject: Password Reset Requested\n\nClick to reset your password now.", "correct": "phish"},
            {"email": "Subject: Weekly Team Update\n\nHere are this week's metrics.", "correct": "legit"},
            {"email": "Subject: Security Alert - Unusual Login\n\nWe detected a login from a new device.", "correct": "legit"},
            {"email": "Subject: Your package is delayed - click to track", "correct": "phish"},
            {"email": "Subject: IT Department - Mandatory MFA Reset", "correct": "phish"},
        ]

        loaded_improvements = 0
        try:
            if IMPROVED_DIR.exists():
                latest = max(IMPROVED_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime)
                with open(latest, "r") as f:
                    data = json.load(f)
                # Merge all possible improvement formats
                blue_from_self = data.get("blue_improvements", [])
                blue_from_bug = data.get("blue_countermeasures", []) + data.get("blue_detection", [])
                all_blue = blue_from_self + blue_from_bug
                if all_blue:
                    email_pool.extend(all_blue)
                    loaded_improvements = len(all_blue)
                    print(f"[PHISHING TRAINER] Loaded {loaded_improvements} new improvements (SelfImprover + BugHunter + ExposureHunter)")
        except Exception as e:
            print(f"[PHISHING TRAINER] Could not load improvements: {e}")

        # Safe sampling
        sample_size = min(random.randint(8, 12), len(email_pool))
        emails = random.sample(email_pool, k=sample_size) if sample_size > 0 else email_pool[:5]

        # Well context
        context = "No nutrients yet."
        try:
            if WELL_DIR.exists():
                latest_well = max(WELL_DIR.glob("nutrient_*.json"), key=lambda p: p.stat().st_mtime)
                with open(latest_well, "r") as f:
                    data = json.load(f)
                context = f"Recent physics sim nutrient quality {data.get('quality_score', 0)}"
        except:
            pass

        correct_count = 0
        hard_negatives = []

        for item in emails:
            prompt = f"""Classify this email as 'phish' or 'legit'. Reply with ONLY one word.
Context from Forest Well: {context}

Email:
{item.get('email', str(item))}

Be critical and vary your judgment slightly."""
            
            response = ollama.generate(model=self.model, prompt=prompt, options={"temperature": 0.85, "top_p": 0.9})
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

        print(f"[PHISHING TRAINER] Session complete — Accuracy: {accuracy:.1f}% | Hard negatives: {len(hard_negatives)} | Improvements loaded: {loaded_improvements}")
        return f"Phishing training complete — Accuracy: {accuracy:.1f}%"

print("=== PhishingTrainerWorker v2.7 loaded — reliable multi-source improvements ===")
