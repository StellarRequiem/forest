import subprocess
from pathlib import Path
import json
import re
import time
from datetime import datetime
import hashlib
from playwright.sync_api import sync_playwright

VAULT_DIR = Path.home() / "ForestVault"
QUARANTINE_DIR = VAULT_DIR / "quarantine"
QUARANTINE_DIR.mkdir(exist_ok=True)

def log_chain(event_type, details=""):
    timestamp = datetime.now().isoformat()
    entry = f"{timestamp} | {event_type} | {details}"
    h = hashlib.sha256(entry.encode()).hexdigest()
    with open(VAULT_DIR / "training_chain.json", "a") as f:
        f.write(f"{entry} | Hash: {h}\n")
    print(f"[SCOUT] {event_type} logged | Hash: {h[:12]}...")

def safe_search(query):
    print(f"[scout] Air-lock search activated for: {query}")
    log_chain("SCOUT_START", query)
    
    raw_text = ""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(f"https://www.google.com/search?q={query.replace(' ', '+')}", wait_until="domcontentloaded")
            page.wait_for_timeout(4000)  # give results time to load
            raw_text = page.content()
            browser.close()
    except Exception as e:
        print(f"[scout] Browser error: {e}")
        log_chain("SCOUT_ERROR", str(e))
        return None
    
    # Safety filter
    raw_text = re.sub(r'<script.*?</script>', '', raw_text, flags=re.DOTALL | re.IGNORECASE)
    raw_text = re.sub(r'(exploit|malware|payload|backdoor|hack|inject|prompt injection)', '[FILTERED]', raw_text, flags=re.IGNORECASE)
    
    # Save to quarantine
    quarantine_file = QUARANTINE_DIR / f"quarantine_{int(time.time())}.txt"
    with open(quarantine_file, "w") as f:
        f.write(f"Search query: {query}\nTimestamp: {datetime.now()}\n\nRaw filtered content:\n{raw_text[:10000]}\n")
    
    print(f"[scout] Raw results saved to quarantine: {quarantine_file.name}")
    print(f"[scout] Review the file manually before promoting to main vault.")
    log_chain("SCOUT_QUARANTINE", quarantine_file.name)
    
    return quarantine_file

if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        safe_search(query)
    else:
        print("Usage: python forest_scout.py \"your search query\"")
        print("Example: python forest_scout.py \"Claude leak details 2026\"")
