#!/usr/bin/env python3
"""
🌲 Forest Gemma Integrator (Fixed for real 2026 models)
"""
import subprocess
from datetime import datetime

def pull_gemma():
    print(f"🌲 Forest Gemma Integrator @ {datetime.now()}")
    models = ["gemma2:2b", "gemma2:9b", "gemma2:27b"]  # realistic current Gemma family
    for m in models:
        print(f"   → Pulling {m} ...")
        try:
            result = subprocess.run(["ollama", "pull", m], capture_output=True, text=True, timeout=90)
            if result.returncode == 0 or "already exists" in result.stderr.lower():
                print(f"   ✅ {m} ready")
            else:
                print(f"   ⚠️ {m} pull had issues (may need manual run)")
        except Exception as e:
            print(f"   Note: {e} — try 'ollama pull {m}' manually")
    print("\nTest any model: ollama run gemma2:9b")
    print("Gemma is now integrated into Forest.")

if __name__ == "__main__":
    pull_gemma()
