#!/usr/bin/env python3
"""
🌲 Forest Ollama Traffic Watcher v1
Monitors port 11434 for unexpected connections
"""
import subprocess
from datetime import datetime
import time
import argparse

def ollama_watcher(watch=False, interval=15):
    print(f"🌲 Forest Ollama Watcher started at {datetime.now()}")
    while True:
        try:
            result = subprocess.check_output(["lsof", "-i", ":11434", "-n", "-P"], text=True, stderr=subprocess.DEVNULL)
            lines = [line.strip() for line in result.splitlines() if "LISTEN" not in line and line.strip()]
            if lines:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Ollama has {len(lines)} connection(s):")
                for line in lines:
                    print(f"   → {line}")
            else:
                print(f"✅ Ollama port 11434 is quiet at {datetime.now().strftime('%H:%M:%S')}")
        except:
            print(f"✅ No activity on Ollama port at {datetime.now().strftime('%H:%M:%S')}")
        
        if not watch:
            break
        time.sleep(interval)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--watch", action="store_true")
    parser.add_argument("--interval", type=int, default=15)
    args = parser.parse_args()
    ollama_watcher(watch=args.watch, interval=args.interval)
