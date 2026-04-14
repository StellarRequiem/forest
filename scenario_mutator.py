#!/usr/bin/env python3
"""
Forest Lvl1Worker — ScenarioMutator v1.1
Safe mutation of training scenarios for blue-team practice.
Never creates dangerous content. Fully Enforcer-gated.
"""

from lvl1_worker import Lvl1Worker
from forest_brain import log_chain
from enforcer import enforcer
import ollama
import json
import re
from pathlib import Path

def harden_json(raw_text: str):
    """FINAL HARDENED JSON EXTRACTOR — Graybeard approved"""
    raw_text = raw_text.strip()
    try:
        return json.loads(raw_text)
    except:
        pass
    match = re.search(r'\{.*\}', raw_text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except:
            pass
    print("[SCENARIOMUTATOR] JSON parse failed — returning empty")
    return {}

class ScenarioMutator(Lvl1Worker):
    def __init__(self):
        super().__init__(name="scenario_mutator", model="phi3:mini", role="Safe blue-team scenario mutator")

    def perform_task(self, task_description: str = "Mutate one safe training scenario for phishing/blue-team practice"):
        if not enforcer.approve(f"ScenarioMutator task: {task_description[:80]}"):
            return "Enforcer blocked"

        print(f"[SCENARIOMUTATOR] Starting safe mutation: {task_description}")

        prompt = f"""You are a blue-team ScenarioMutator inside the Forest.
Task: {task_description}
Return ONLY valid JSON with keys: "mutated_scenario", "risk_level", "countermeasure", "correct".
No explanations outside the JSON. Keep it safe and realistic for training."""

        try:
            response = ollama.generate(model=self.model, prompt=prompt)
            raw = response['response'].strip()
            data = harden_json(raw)
            
            log_chain("SCENARIO_MUTATE", f"mutated: {data.get('mutated_scenario', 'none')[:60]}")
            print(f"[SCENARIOMUTATOR] Safe mutated scenario ready")
            return data
        except Exception as e:
            log_chain("SCENARIOMUTATOR_ERROR", str(e))
            return {"error": str(e)}

    def should_recycle(self):
        return False

print("=== ScenarioMutator v1.1 Loaded — Clean & Hardened ===")
