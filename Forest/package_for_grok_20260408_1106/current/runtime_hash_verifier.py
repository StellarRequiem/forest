import hashlib
from pathlib import Path

def calculate_file_hash(file_path):
    if not Path(file_path).exists():
        print(f"File not found: {file_path}")
        return None
    with open(file_path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def baseline_hashes():
    trainers = [
        "dynamic_trainer_v6.py",
        "phishing_trainer_v5.py",
        "network_log_analyzer_trainer.py",
        "supply_chain_simulator.py"
    ]
    baseline_file = Path("known_hashes.txt")
    
    print("Re-creating baseline hashes for current clean headless trainers...\n")
    with open(baseline_file, "w") as f:
        for trainer in trainers:
            h = calculate_file_hash(trainer)
            if h:
                f.write(f"{trainer}:{h}\n")
                print(f"Baseline recorded for {trainer}: {h[:16]}...")
            else:
                print(f"Skipped {trainer} (not found)")
    print(f"\nNew baseline saved to {baseline_file}. Future runs will use these hashes.")

def verify_trainer_hash(trainer_name):
    trainer_path = Path(trainer_name)
    if not trainer_path.exists():
        print(f"WARNING: {trainer_name} not found")
        return False
    
    current_hash = calculate_file_hash(trainer_path)
    baseline_file = Path("known_hashes.txt")
    
    if not baseline_file.exists():
        print("No baseline found. Run baseline_hashes() first.")
        return False
    
    known_hashes = {}
    with open(baseline_file) as f:
        for line in f:
            if ':' in line:
                name, h = line.strip().split(':', 1)
                known_hashes[name] = h
    
    expected = known_hashes.get(trainer_name)
    if not expected:
        print(f"No baseline for {trainer_name} - recording current hash.")
        with open(baseline_file, "a") as f:
            f.write(f"{trainer_name}:{current_hash}\n")
        return True
    
    if current_hash != expected:
        print(f"CRITICAL: HASH MISMATCH on {trainer_name}! Possible tampering.")
        print(f"Expected : {expected[:16]}...")
        print(f"Current  : {current_hash[:16]}...")
        return False
    
    print(f"✅ Hash verified for {trainer_name}")
    return True

if __name__ == "__main__":
    baseline_hashes()   # Re-baseline the current clean files
