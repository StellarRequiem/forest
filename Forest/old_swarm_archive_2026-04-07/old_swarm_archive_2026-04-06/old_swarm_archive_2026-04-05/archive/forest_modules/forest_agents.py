import subprocess
import json
import time
from pathlib import Path
from datetime import datetime
import hashlib
import re

VAULT_DIR = Path.home() / "ForestVault"
AGENT_DIR = VAULT_DIR / "agents"
AGENT_DIR.mkdir(exist_ok=True)

def log_chain(event_type, details=""):
    timestamp = datetime.now().isoformat()
    entry = f"{timestamp} | {event_type} | {details}"
    h = hashlib.sha256(entry.encode()).hexdigest()
    with open(VAULT_DIR / "training_chain.json", "a") as f:
        f.write(f"{entry} | Hash: {h}\n")
    print(f"[AGENT] {event_type} logged | Hash: {h[:12]}...")

def run_network_watcher():
    print("[network_watcher] Starting specialized monitoring + anomaly flagging on en1...")
    log_chain("AGENT_START", "network_watcher")
    interface = "en1"
    anomaly_count = 0
    try:
        while True:
            try:
                result = subprocess.run([
                    "tcpdump", "-i", interface, "-c", "60", "-nn", "-q", "not port 22 and not port 443"
                ], capture_output=True, text=True, timeout=25)
                raw = result.stdout.strip()
                summary = raw[:1000] if raw else "Quiet period"

                suspicious = False
                lines = len(raw.splitlines())
                if lines > 35:  # high volume
                    suspicious = True
                if re.search(r'\d+\.\d+\.\d+\.\d+:\d+ > .*?:[1-9]\d{3,4}', raw):  # unusual high ports
                    suspicious = True
                if "SYN" in raw and raw.count("SYN") > 15:  # possible scan
                    suspicious = True

                log_file = VAULT_DIR / f"netwatch_{int(time.time())}.log"
                with open(log_file, "w") as f:
                    f.write(f"[{datetime.now()}] Network snapshot on {interface}:\n{summary}\n")
                    if suspicious:
                        f.write("\n⚠️ ANOMALY DETECTED: High volume, unusual ports, or possible scan\n")
                        anomaly_count += 1
                        log_chain("NETWATCH_ANOMALY", f"Count: {anomaly_count} | Lines: {lines}")

                status = "⚠️ ANOMALY" if suspicious else "Normal"
                print(f"[network_watcher] Logged snapshot ({lines} lines) {status}")
                log_chain("NETWATCH_SNAPSHOT", f"{lines} lines")

            except subprocess.TimeoutExpired:
                print("[network_watcher] Light cycle - no heavy traffic")
            except Exception as e:
                print(f"[network_watcher] Capture error: {e}")
            time.sleep(90)
    except Exception as e:
        print(f"[network_watcher] Fatal error: {e}")
        log_chain("AGENT_ERROR", str(e))

def run_scenario_mutator():
    print("[scenario_mutator] Starting specialized mutation from real weak areas...")
    log_chain("AGENT_START", "scenario_mutator")
    try:
        while True:
            sessions = sorted(VAULT_DIR.glob("*sessions*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
            if sessions:
                try:
                    with open(sessions[0]) as f:
                        data = json.load(f)
                    avg_acc = sum(s.get("percentage", 0) for s in data if isinstance(s, dict)) / len([s for s in data if isinstance(s, dict)]) if data else 82.0
                    weak_hint = "focus on low-accuracy tiers, social engineering, and prompt injection" if avg_acc < 85 else "increase difficulty in supply-chain and red-team simulation"
                    prompt = f"""Current training accuracy ~{avg_acc:.1f}%. Generate 5 new realistic blue/red-team scenarios targeting weak areas ({weak_hint}).
Output ONLY valid JSON array. Keys: "scenario", "correct", "feedback_correct", "feedback_incorrect".
No thinking, no extra text. Start with [ and end with ]."""
                    result = subprocess.run(["ollama", "run", "phi3:mini", prompt], capture_output=True, text=True, timeout=70)
                    clean = result.stdout.strip()
                    if clean and clean.startswith('['):
                        new_file = VAULT_DIR / f"proposed_real_{int(time.time())}.json"
                        new_file.write_text(clean)
                        print(f"[scenario_mutator] Generated 5 new targeted scenarios → {new_file.name}")
                        log_chain("MUTATOR_GENERATED", new_file.name)
                except Exception as inner_e:
                    print(f"[scenario_mutator] Session parse error: {inner_e}")
            time.sleep(180)
    except Exception as e:
        print(f"[scenario_mutator] Fatal error: {e}")
        log_chain("AGENT_ERROR", str(e))

if __name__ == "__main__":
    print("=== Forest Specialized Agents Online - Phase 1 (Anomaly Flagging) ===")
    from multiprocessing import Process
    p1 = Process(target=run_network_watcher, daemon=True)
    p2 = Process(target=run_scenario_mutator, daemon=True)
    p1.start()
    p2.start()
    print("Agents running with anomaly flagging. Data feeds back to vault.")
    try:
        p1.join()
        p2.join()
    except KeyboardInterrupt:
        print("\nAgents shutting down gracefully.")
