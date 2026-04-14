#!/usr/bin/env python3
"""
🌲 Forest Local Model Integrator (Ollama only)
Pulls small, useful models you can run right now
"""
import subprocess
from datetime import datetime

def pull_models():
    print(f"🌲 Forest Local Model Integrator @ {datetime.now()}")
    models = ["gemma2:2b", "phi4:mini", "llama3.2:3b", "qwen2.5:3b"]
    for m in models:
        print(f"   → Pulling {m} ...")
        try:
            result = subprocess.run(["ollama", "pull", m], capture_output=True, text=True, timeout=120)
            if result.returncode == 0 or "already exists" in (result.stderr or "").lower():
                print(f"   ✅ {m} ready")
            else:
                print(f"   ⚠️ {m} had issues — run manually if needed")
        except Exception as e:
            print(f"   Note: {e} (Ollama may not be running)")
    print("\nTest any model with: ollama run gemma2:2b")
    print("All models stay 100% local.")

if __name__ == "__main__":
    pull_models()
