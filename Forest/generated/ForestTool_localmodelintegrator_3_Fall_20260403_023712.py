#!/usr/bin/env python3
"""
🌲 Forest Local Model Integrator v2
Pulls small, actually available Ollama models
"""
import subprocess
from datetime import datetime

def pull_local_models():
    print(f"🌲 Forest Local Model Integrator @ {datetime.now()}")
    models = [
        "gemma2:2b",      # Small & fast
        "phi4:mini",      # Good performance
        "llama3.2:3b",    # Very popular
        "qwen2.5:3b",     # Strong small model
        "mistral:7b"      # Classic
    ]
    print("Trying to pull the following small models:\n")
    for m in models:
        print(f"   → Pulling {m} ...")
        try:
            result = subprocess.run(["ollama", "pull", m], capture_output=True, text=True, timeout=180)
            if result.returncode == 0 or "already exists" in (result.stderr or "").lower():
                print(f"   ✅ {m} is ready")
            else:
                print(f"   ⚠️ {m} failed or not found — you can try manually later")
        except Exception as e:
            print(f"   Note: {e} (Make sure Ollama is running)")
    print("\nTo test any model:")
    print("   ollama run gemma2:2b")
    print("   ollama run llama3.2:3b")
    print("\nAll models stay 100% local on your machine.")

if __name__ == "__main__":
    pull_local_models()
