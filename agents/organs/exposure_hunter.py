#!/usr/bin/env python3
"""
Forest Lvl1Worker — ExposureHunter v1.1
Safe privacy/telemetry exposure hunting. Finds leaks and suggests blue-team fixes.
Never executes real scans on live systems without Enforcer approval.
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
    print("[EXPOSUREHUNTER] JSON parse failed — returning empty")
    return {}

class ExposureHunter(Lvl1Worker):
    def __init__(self):
        super().__init__(name="exposure_hunter", model="phi3:mini", role="Safe privacy & telemetry exposure hunter")

    def perform_task(self, task_description: str = "Hunt for privacy exposures and suggest blue-team countermeasures"):
        if not enforcer.approve(f"ExposureHunter task: {task_description[:80]}"):
            return "Enforcer blocked"

        print(f"[EXPOSUREHUNTER] Starting safe exposure hunt: {task_description}")

        prompt = f"""You are a blue-team ExposureHunter inside the Forest.
Task: {task_description}
Return ONLY valid JSON with keys: "exposure", "risk_level", "countermeasure", "correct".
No explanations outside the JSON. Focus on safe, realistic privacy/telemetry issues."""

        try:
            response = ollama.generate(model=self.model, prompt=prompt)
            raw = response['response'].strip()
            data = harden_json(raw)
            
            log_chain("EXPOSURE_HUNT", f"found: {data.get('exposure', 'none')[:60]}")
            print(f"[EXPOSUREHUNTER] Safe exposure found: {data.get('exposure', 'none')[:80]}...")
            return data
        except Exception as e:
            log_chain("EXPOSUREHUNTER_ERROR", str(e))
            return {"error": str(e)}

    def should_recycle(self):
        return False

print("=== ExposureHunter v1.1 Loaded — Clean & Hardened ===")
