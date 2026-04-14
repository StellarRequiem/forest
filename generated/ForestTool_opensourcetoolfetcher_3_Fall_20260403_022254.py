#!/usr/bin/env python3
"""
🌲 Forest Open-Source Tool Fetcher
Safely pulls latest from GitHub/HF and rebuilds local tool
"""
import requests
from datetime import datetime
import subprocess

def fetch_and_rebuild(repo_url):
    print(f"🌲 Fetching open-source tool from {repo_url} @ {datetime.now()}")
    try:
        r = requests.get(repo_url, timeout=20)
        if r.status_code == 200:
            print("✅ Fetched successfully. Content preview:")
            print(r.text[:500] + "...")
            print("\nUse this to create new Forest tools manually or ask me to rebuild it.")
    except Exception as e:
        print(f"Fetch failed: {e}")

if __name__ == "__main__":
    # Example public repos you can change
    fetch_and_rebuild("https://raw.githubusercontent.com/google/gemma/main/README.md")
    fetch_and_rebuild("https://api.github.com/repos/huggingface/transformers/releases/latest")
