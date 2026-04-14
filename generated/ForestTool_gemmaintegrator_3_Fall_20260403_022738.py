#!/usr/bin/env python3
"""
🌲 Forest Gemma Integrator
"""
import subprocess
from datetime import datetime

def pull_gemma():
    print(f"🌲 Forest Gemma Integrator @ {datetime.now()}")
    models = ["gemma2:2b", "gemma2:9b", "gemma2:27b"]
    for m in models:
        print(f"   → Pulling {m} ...")
        try:
            result = subprocess.run(["ollama", "pull", m], capture_output=True, text=True, timeout=90)
            if result.returncode == 0 or "already exists" in (result.stderr or "").lower():
                print(f"   ✅ {m} ready")
            else:
                print(f"   ⚠️ {m} had issues — try manually")
        except Exception as e:
            print(f"   Note: {e}")
    print("\nTest: ollama run gemma2:9b")
if __name__ == "__main__":
    pull_gemma()
