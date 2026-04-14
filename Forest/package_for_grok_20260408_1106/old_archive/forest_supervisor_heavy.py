import subprocess
import time
from pathlib import Path
from datetime import datetime
import multiprocessing
import psutil
import hashlib   # ← This was missing

VAULT_DIR = Path.home() / "ForestVault"

def log_to_cryptex(event_type, details=""):
    try:
        timestamp = datetime.now().isoformat()
        entry = f"{timestamp} | {event_type} | {details}"
        h = hashlib.sha256(entry.encode()).hexdigest()[:16]
        with open(VAULT_DIR / "training_chain.json", "a") as f:
            f.write(f"{entry} | Hash: {h}\n")
        print(f"[SUPERVISOR] {event_type} logged | Hash: {h}")
    except Exception as e:
        print(f"[SUPERVISOR] Logging failed: {e}")

def check_temp():
    try:
        temps = psutil.sensors_temperatures()
        if 'cpu_thermal' in temps and temps['cpu_thermal']:
            return temps['cpu_thermal'][0].current
    except:
        pass
    return 0

def get_trainer_list():
    # Easy to extend later for enterprise / new trainers
    return [
        "dynamic_trainer_v6.py",
        "phishing_trainer_v5.py",
        "supply_chain_simulator.py",
    ]

def run_cycle(trainer):
    print(f"Running {trainer} headless...")
    try:
        result = subprocess.run(["python", trainer, "--auto"], timeout=240, capture_output=True, text=True)
        print(f"✅ {trainer} completed")
        log_to_cryptex("TRAINER_CYCLE", trainer)
    except Exception as e:
        print(f"Failed {trainer}: {e}")
        log_to_cryptex("TRAINER_FAILED", f"{trainer} - {e}")

def supervisor():
    cycle = 0
    while True:
        cycle += 1
        print(f"\n=== Heavy Cycle {cycle} ===")

        trainers = get_trainer_list()
        processes = []

        for trainer in trainers:
            p = multiprocessing.Process(target=run_cycle, args=(trainer,))
            p.start()
            processes.append(p)

        for p in processes:
            p.join()

        temp = check_temp()
        if temp > 78:
            print(f"CPU temp {temp}°C — throttling 30s")
            time.sleep(30)
        else:
            time.sleep(15)

        if cycle % 5 == 0:
            print("Triggering self-review...")
            log_to_cryptex("SUPERVISOR_SELF_REVIEW", f"Cycle {cycle}")

if __name__ == "__main__":
    print("=== Forest Supervisor - Fixed V2 (Dynamic + Metrics Ready) ===")
    supervisor()
