import time
from pathlib import Path
from datetime import datetime
import hashlib
import subprocess
import json
import psutil

VAULT_DIR = Path.home() / "ForestVault"
LOG_DIR = VAULT_DIR / "network_logs"

def log_to_cryptex(event_type, details=""):
    timestamp = datetime.now().isoformat()
    entry = f"{timestamp} | {event_type} | {details}"
    h = hashlib.sha256(entry.encode()).hexdigest()[:16]
    with open(VAULT_DIR / "training_chain.json", "a") as f:
        f.write(f"{entry} | Hash: {h}\n")
    print(f"[PRINCIPLE_AUDITOR] {event_type} logged | Hash: {h}")

print("=== Principle Auditor Online - Continuous Self-Audit & Early Correction ===")

while True:
    try:
        print(f"\n[Principle Auditor] Full system health check @ {datetime.now().strftime('%H:%M:%S')}")

        issues = []

        # 1. Check for latest network snapshot
        snapshots = sorted(LOG_DIR.glob("*.json"))
        if not snapshots:
            issues.append("No network snapshots found - watcher may be stalled")
        else:
            latest = snapshots[-1]
            age = time.time() - latest.stat().st_mtime
            if age > 180:
                issues.append(f"Network snapshot is stale ({age:.0f} seconds old)")

        # 2. Check active tmux sessions
        try:
            tmux = subprocess.run(["tmux", "ls"], capture_output=True, text=True)
            if "hallmonitor" not in tmux.stdout or "mouth" not in tmux.stdout:
                issues.append("Critical organs (Hall Monitor or Mouth) not running")
        except:
            issues.append("Cannot check tmux sessions")

        # 3. Check for stale processes
        stale = 0
        for proc in psutil.process_iter(['cmdline']):
            try:
                cmd = ' '.join(proc.info['cmdline'] or [])
                if "forest_" in cmd and "python" in cmd:
                    if "zombie" in str(proc):
                        stale += 1
            except:
                pass
        if stale > 0:
            issues.append(f"{stale} stale Forest processes detected")

        # 4. Check proposal quality in Forge sandbox
        forge_files = list((VAULT_DIR / "forge_sandbox").glob("*.md"))
        if forge_files:
            for f in forge_files[-3:]:
                with open(f) as fh:
                    content = fh.read(300)
                if "Thinking" in content or "Okay, let's" in content:
                    issues.append(f"Low-quality proposal detected: {f.name} (contains thinking text)")

        # Report findings
        if issues:
            print(f"[Principle Auditor] Found {len(issues)} issues:")
            for issue in issues:
                print(f"  • {issue}")
            log_to_cryptex("PRINCIPLE_ISSUE", f"{len(issues)} issues detected")
        else:
            print("[Principle Auditor] All systems nominal.")

        time.sleep(120)  # every 2 minutes

    except KeyboardInterrupt:
        print("\nPrinciple Auditor shutting down.")
        break
    except Exception as e:
        print(f"[Principle Auditor] Error: {e}")
        time.sleep(60)
