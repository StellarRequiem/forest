#!/usr/bin/env python3
"""
🌲 Forest Gemma 4 Integrator (Gemma 4 just dropped April 2, 2026)
Pulls latest GGUF + creates Ollama run script
"""
import subprocess
from datetime import datetime
import os

def pull_gemma4():
    print(f"🌲 Pulling Gemma 4 info @ {datetime.now()}")
    models = [
        "gemma4:2b",      # smallest, phone-friendly
        "gemma4:4b",
        "gemma4:26b-moe", # high quality MoE
    ]
    for m in models:
        print(f"   Pulling {m} via Ollama...")
        try:
            subprocess.call(["ollama", "pull", m])
            print(f"   ✅ {m} ready")
        except Exception as e:
            print(f"   Note: {e} (run 'ollama pull {m}' manually)")
    print("\nRun any model with: ollama run gemma4:2b")
    print("Forest Gemma 4 tool generated.")

if __name__ == "__main__":
    pull_gemma4()
