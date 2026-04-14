import subprocess
import time
from pathlib import Path
import psutil
from datetime import datetime
import hashlib
import multiprocessing

VAULT_DIR = Path.home() / "ForestVault"
VAULT_DIR.mkdir(exist_ok=True)

def log_chain(event_type, details=""):
    timestamp = datetime.now().isoformat()
    entry = f"{timestamp} | {event_type} | {details}"
    h = hashlib.sha256(entry.encode()).hexdigest()
    with open(VAULT_DIR / "training_chain.json", "a") as f:
        f.write(f"{entry} | Hash: {h}\n")
    print(f"[SUPERVISOR] {event_type} logged | Hash: {h[:12]}...")

def check_temp():
    try:
        temps = psutil.sensors_temperatures()
        if 'cpu_thermal' in temps:
            return temps['cpu_thermal'][0].current
        # Fallback for Apple Silicon
        return psutil.cpu_percent(interval=0.5) * 0.8  # rough proxy
    except:
        return 0

def run_main_cycle(trainer):
    if not Path(trainer).exists():
        return
    print(f"[MAIN] Running {trainer} headless...")
    try:
        subprocess.run(["python", trainer, "--auto"], timeout=160, capture_output=True)
        print(f"[MAIN] ✅ {trainer} completed")
        log_chain("TRAINER_COMPLETE", trainer)
    except Exception as e:
        print(f"[MAIN] Failed {trainer}: {e}")

def supervisor():
    print("=== Forest Heavy Supervisor v6.0 - 80% Push with Thermal Cycling ===")
    trainers = [
        "dynamic_trainer_v6.py",
        "phishing_trainer_v5.py",
        "supply_chain_simulator.py",
        "network_log_analyzer_trainer.py",
        "red_team_simulation_trainer.py"  # add more as we build them
    ]
    cycle = 0
    while True:
        cycle += 1
        temp = check_temp()
        print(f"\n=== Heavy Cycle {cycle} | CPU Temp: {temp:.1f}°C ===")
        
        if temp > 78:
            print("🌡️  High temp - cooling off for 45 seconds...")
            time.sleep(45)
            continue
        
        # Ramp up: more parallel processes
        processes = []
        for trainer in trainers:
            p = multiprocessing.Process(target=run_main_cycle, args=(trainer,))
            p.start()
            processes.append(p)
        
        for p in processes:
            p.join()
        
        log_chain("HEAVY_CYCLE_COMPLETE", f"Cycle {cycle} - {len(trainers)} trainers")
        time.sleep(8)  # short rest during high load

if __name__ == "__main__":
    multiprocessing.set_start_method("spawn", force=True)
    supervisor()
