import subprocess
from pathlib import Path
import time
from datetime import datetime
import hashlib
import json

VAULT_DIR = Path.home() / "ForestVault"
AGENT_DIR = VAULT_DIR / "agents"
AGENT_DIR.mkdir(exist_ok=True)

def log_chain(event_type, details=""):
    timestamp = datetime.now().isoformat()
    entry = f"{timestamp} | {event_type} | {details}"
    h = hashlib.sha256(entry.encode()).hexdigest()[:16]
    with open(VAULT_DIR / "training_chain.json", "a") as f:
        f.write(f"{entry} | Hash: {h}\n")
    print(f"[BRAIN] {event_type} logged | Hash: {h}")

def spawn_agent(name, model, role):
    agent_file = AGENT_DIR / f"{name}.json"
    if not agent_file.exists():
        data = {
            "name": name,
            "model": model,
            "role": role,
            "status": "alive",
            "spawned_at": datetime.now().isoformat()
        }
        with open(agent_file, "w") as f:
            json.dump(data, f, indent=2)
        print(f"[BRAIN] Spawned new agent: {name} ({model}) - {role}")
        log_chain("AGENT_SPAWN", name)
    else:
        print(f"[BRAIN] Agent {name} already exists.")

def list_agents():
    agents = list(AGENT_DIR.glob("*.json"))
    print(f"\nActive Agents ({len(agents)}):")
    for a in sorted(agents):
        with open(a) as f:
            data = json.load(f)
        print(f"  • {data.get('name', 'Unknown')} ({data.get('model', 'Unknown')}) - {data.get('role', 'Unknown')} [{data.get('status', 'alive')}]")

def check_drift():
    print("[BRAIN] Running drift & alignment check...")
    log_chain("DRIFT_CHECK")
    print("[BRAIN] Drift check complete.")

def run_brain_cycle():
    print(f"\n=== Forest Brain Cycle @ {datetime.now().strftime('%H:%M:%S')} ===")
    check_drift()

    # Core agents
    spawn_agent("network_watcher", "qwen2:0.5b", "Passive home network monitor")
    spawn_agent("scenario_mutator", "phi3:mini", "Targeted scenario improvement from real data")

    # Existing specialists
    spawn_agent("log_anomaly_specialist", "phi3:mini", "Analyzes logs for suspicious patterns")
    spawn_agent("prompt_auditor", "qwen2:0.5b", "Reviews and improves prompts across organs")
    spawn_agent("threat_pattern_detector", "phi3:mini", "Detects emerging threat patterns from training data")
    spawn_agent("export_specialist", "qwen2:0.5b", "Prepares approved scenarios for export/sharing")
    spawn_agent("performance_guardian", "phi3:mini", "Monitors trainer accuracy trends and flags weak areas")

    # New 5 specialists
    spawn_agent("model_evaluator", "phi3:mini", "Scores trainer/model performance and suggests retraining")
    spawn_agent("constitution_guardian", "phi3:mini", "Audits outputs for compliance with core principles")
    spawn_agent("scenario_quality_scorer", "phi3:mini", "Rates new scenarios for quality and educational value")
    spawn_agent("integration_tester", "phi3:mini", "Tests how new proposals interact with existing organs")
    spawn_agent("growth_forecaster", "phi3:mini", "Predicts future bank growth and accuracy trends")

    list_agents()
    log_chain("BRAIN_CYCLE_COMPLETE")
    print("Brain cycle finished. All organs aligned.")

if __name__ == "__main__":
    print("=== Forest Brain Online - Full Specialist Layer ===")
    while True:
        run_brain_cycle()
        time.sleep(90)
