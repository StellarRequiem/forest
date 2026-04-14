#!/usr/bin/env python3
"""
🌲 Forest Local Model Manager — Final Clean Version
"""

import subprocess
import argparse
from datetime import datetime

RECOMMENDED = ["gemma2:2b", "llama3.2:3b", "qwen2.5:3b", "phi4:mini"]

def get_installed():
    try:
        out = subprocess.check_output(["ollama", "list"], text=True)
        return [line.split()[0] for line in out.strip().splitlines()[1:] if line.strip()]
    except:
        return []

def status():
    print(f"🌲 Forest Local Model Manager @ {datetime.now()}")
    installed = get_installed()
    
    print(f"\n=== Installed Models ({len(installed)}) ===")
    if installed:
        for m in sorted(installed):
            print(f"   ✅ {m}")
    else:
        print("   No models installed yet.")
    
    print("\n=== Recommended Small Models ===")
    for m in RECOMMENDED:
        mark = "✅" if any(m.split(":")[0] in i for i in installed) else "⬜"
        print(f"   {mark} {m}")
    
    print("\nHow to use:")
    print("   python generated/ForestModelManager.py --status")
    print("   python generated/ForestModelManager.py --pull")

def pull_missing():
    installed = get_installed()
    missing = [m for m in RECOMMENDED if not any(m.split(":")[0] in i for i in installed)]
    if not missing:
        print("✅ All recommended models are already installed!")
        return
    print(f"🌲 Pulling {len(missing)} missing models...")
    for m in missing:
        print(f"   → Pulling {m} ...")
        try:
            subprocess.run(["ollama", "pull", m], timeout=300)
            print(f"   ✅ {m} ready")
        except Exception as e:
            print(f"   Error pulling {m}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Forest Local Model Manager")
    parser.add_argument("--pull", action="store_true", help="Pull missing recommended models")
    parser.add_argument("--status", action="store_true", help="Show status")
    args = parser.parse_args()
    
    if args.pull:
        pull_missing()
    else:
        status()
