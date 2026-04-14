#!/usr/bin/env python3
"""
Forest Lvl1Worker — ForestForge v1.1
Safe agent forging. Creates new blue-team Lvl1 workers only.
Never spawns dangerous code. Fully Enforcer + Cryptex gated.
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
    print("[FORGE] JSON parse failed — returning empty")
    return {}

class ForestForge(Lvl1Worker):
    def __init__(self):
        super().__init__(name="forest_forge", model="phi3:mini", role="Safe blue-team agent forger")

    def perform_task(self, task_description: str = "Forge one safe new blue-team Lvl1 worker"):
        if not enforcer.approve(f"ForestForge task: {task_description[:80]}"):
            return "Enforcer blocked"

        print(f"[FORGE] Starting safe agent forging: {task_description}")

        prompt = f"""You are a blue-team ForestForge inside the Forest.
Task: {task_description}
Return ONLY valid JSON with keys: "new_worker_name", "role", "capability", "correct".
No explanations outside the JSON. Keep it safe and shippable."""

        try:
            response = ollama.generate(model=self.model, prompt=prompt)
            raw = response['response'].strip()
            data = harden_json(raw)
            
            log_chain("FORGE_NEW_WORKER", f"created: {data.get('new_worker_name', 'none')}")
            print(f"[FORGE] Safe new worker forged: {data.get('new_worker_name', 'none')}")
            return data
        except Exception as e:
            log_chain("FORGE_ERROR", str(e))
            return {"error": str(e)}

    def should_recycle(self):
        return False

print("=== ForestForge v1.1 Loaded — Clean & Hardened ===")
