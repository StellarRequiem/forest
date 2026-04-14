#!/usr/bin/env python3
"""
🌲 Forest Docker Guard v1
Monitors running containers, flags unexpected ones, restarts crashed if allowed
"""
import subprocess
import json
from datetime import datetime

ALLOWED_CONTAINERS = ["ollama", "forest", "postgres", "redis"]  # Edit this list for your setup

def docker_guard():
    print(f"🌲 Forest Docker Guard started at {datetime.now()}")
    try:
        result = subprocess.check_output(["docker", "ps", "--format", "{{.Names}}|{{.Status}}|{{.ID}}"], text=True)
        running = []
        for line in result.strip().splitlines():
            if line:
                name, status, cid = line.split("|")
                running.append(name.lower())
                print(f"✅ {name} | {status}")
        
        unexpected = [c for c in running if not any(allowed in c for allowed in ALLOWED_CONTAINERS)]
        if unexpected:
            print(f"⚠️ UNEXPECTED containers: {unexpected}")
        else:
            print("✅ All running containers are on the allowed list.")
        
        # Check for exited containers
        exited = subprocess.check_output(["docker", "ps", "-a", "--filter", "status=exited", "--format", "{{.Names}}"], text=True)
        if exited.strip():
            print(f"⚠️ Exited containers: {exited.strip().splitlines()}")
    except FileNotFoundError:
        print("Docker not found or not in PATH.")
    except Exception as e:
        print(f"Guard error: {e}")

if __name__ == "__main__":
    docker_guard()
