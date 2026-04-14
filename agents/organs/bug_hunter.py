#!/usr/bin/env python3
"""
Forest Lvl1Worker — BugBountyHunter v1.1
Safe blue-team bug bounty simulation. Generates realistic scenarios + countermeasures.
Never executes real exploits. Fully Enforcer-gated.
"""

from agents.core.lvl1_worker import Lvl1Worker
from agents.organs.forest_brain import log_chain
from agents.organs.enforcer import enforcer
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
    print("[BUGHUNTER] JSON parse failed — returning empty")
    return {}

class BugBountyHunter(Lvl1Worker):
    def __init__(self):
        super().__init__(name="bug_bounty_hunter", model="phi3:mini", role="Safe bug bounty simulation & blue-team countermeasure generator")

    def perform_task(self, task_description: str = "Generate one safe bug bounty scenario + blue countermeasure"):
        if not enforcer.approve(f"BugBountyHunter task: {task_description[:80]}"):
            return "Enforcer blocked"

        print(f"[BUGHUNTER] Starting safe simulation: {task_description}")

        prompt = f"""You are a blue-team BugBountyHunter inside the Forest.
Task: {task_description}
Return ONLY valid JSON with keys: "scenario", "vulnerability", "countermeasure", "correct".
No explanations outside the JSON. Keep it realistic but safe."""

        try:
            response = ollama.generate(model=self.model, prompt=prompt)
            raw = response['response'].strip()
            data = harden_json(raw)
            
            log_chain("BUG_BOUNTY_SIM", f"scenario: {data.get('scenario', 'none')[:60]}")
            print(f"[BUGHUNTER] Safe scenario generated: {data.get('scenario', 'none')[:80]}...")
            return data
        except Exception as e:
            log_chain("BUGHUNTER_ERROR", str(e))
            return {"error": str(e)}

    def should_recycle(self):
        return False

print("=== BugBountyHunter v1.1 Loaded — Clean & Hardened ===")
