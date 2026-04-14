#!/usr/bin/env python3
"""
🌲 Forest Local Model Manager
"""
import subprocess
import argparse
from datetime import datetime

RECOMMENDED = ["gemma2:2b", "llama3.2:3b", "qwen2.5:3b", "phi3:mini", "mistral:7b"]

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
    for m in sorted(installed) if installed else print("   No models installed yet."):
        print(f"   ✅ {m}")
    print("\n=== Recommended ===")
    for m in RECOMMENDED:
        mark = "✅" if any(m.split(":")[0] in i for i in installed) else "⬜"
        print(f"   {mark} {m}")
    print("\nUsage: python generated/ForestManager_Models.py --status or --pull")

def pull_missing():
    installed = get_installed()
    missing = [m for m in RECOMMENDED if not any(m.split(":")[0] in i for i in installed)]
    if not missing:
        print("✅ All recommended models installed!")
        return
    print(f"🌲 Pulling {len(missing)} missing models...")
    for m in missing:
        print(f"   → Pulling {m} ...")
        try:
            subprocess.run(["ollama", "pull", m], timeout=600)
            print(f"   ✅ {m} ready")
        except Exception as e:
            print(f"   Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pull", action="store_true")
    parser.add_argument("--status", action="store_true")
    args = parser.parse_args()
    if args.pull:
        pull_missing()
    else:
        status()
