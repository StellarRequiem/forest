#!/usr/bin/env python3
"""
Forest Lvl1Worker — ArchitectureEvolver v1.1
Safe self-evolution of Forest architecture. Suggests improvements to CUS, organs, and safety layers.
Never mutates live code without Enforcer + human gate.
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
    print("[ARCHEVOLVER] JSON parse failed — returning empty")
    return {}

class ArchitectureEvolver(Lvl1Worker):
    def __init__(self):
        super().__init__(name="architecture_evolver", model="phi3:mini", role="Safe Forest architecture self-improver")

    def perform_task(self, task_description: str = "Suggest safe improvement to Forest architecture or CUS hierarchy"):
        if not enforcer.approve(f"ArchitectureEvolver task: {task_description[:80]}"):
            return "Enforcer blocked"

        print(f"[ARCHEVOLVER] Starting safe evolution cycle: {task_description}")

        prompt = f"""You are a blue-team ArchitectureEvolver inside the Forest.
Task: {task_description}
Return ONLY valid JSON with keys: "evolution", "benefit", "risk_level", "correct".
No explanations outside the JSON. Keep changes safe and shippable."""

        try:
            response = ollama.generate(model=self.model, prompt=prompt)
            raw = response['response'].strip()
            data = harden_json(raw)
            
            log_chain("ARCH_EVOLUTION", f"evolved: {data.get('evolution', 'none')[:60]}")
            print(f"[ARCHEVOLVER] Safe evolution suggested: {data.get('evolution', 'none')[:80]}...")
            return data
        except Exception as e:
            log_chain("ARCHEVOLVER_ERROR", str(e))
            return {"error": str(e)}

    def should_recycle(self):
        return False

print("=== ArchitectureEvolver v1.1 Loaded — Clean & Hardened ===")
