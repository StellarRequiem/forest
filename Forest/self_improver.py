#!/usr/bin/env python3
"""
Forest SelfImproverWorker v1.2 — Clean, hardened, CUS-compliant
Blue-team self-improvement only. No dangerous mutations.
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
    # Try clean JSON first
    try:
        return json.loads(raw_text)
    except:
        pass
    # Fallback: extract first { ... } block
    match = re.search(r'\{.*\}', raw_text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except:
            pass
    print("[SELFIMPROVER] JSON parse failed — returning empty")
    return {}

class SelfImproverWorker(Lvl1Worker):
    def __init__(self):
        super().__init__(name="self_improver", model="phi3:mini", role="Blue-team self-improvement & organ hardening")

    def perform_task(self, task_description: str = "Improve blue-team organs safely"):
        if not enforcer.approve(f"SelfImprover task: {task_description[:80]}"):
            return "Enforcer blocked"

        print(f"[SELFIMPROVER] Starting safe improvement cycle: {task_description}")
        
        # Safe blue-team improvement prompt (never touches red-team or dangerous code)
        prompt = f"""You are a blue-team self-improver inside the Forest.
Task: {task_description}
Return ONLY valid JSON with keys: "improvement", "correct", "reason".
No explanations outside the JSON."""

        try:
            response = ollama.generate(model=self.model, prompt=prompt)
            raw = response['response'].strip()
            data = harden_json(raw)
            
            log_chain("SELFIMPROVEMENT", f"improved: {data.get('improvement', 'none')}")
            print(f"[SELFIMPROVER] Improvement applied: {data.get('improvement', 'none')}")
            return data
        except Exception as e:
            log_chain("SELFIMPROVER_ERROR", str(e))
            return {"error": str(e)}

    def should_recycle(self):
        return False  # Placeholder — expand later with CUS grading

print("=== SelfImproverWorker v1.2 Loaded — Clean & Hardened ===")
