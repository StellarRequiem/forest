import time
import psutil
import multiprocessing
from lvl1_worker import Lvl1Worker
from enforcer import EnforcerTeam
from datetime import datetime

class DivisionSpawner:
    def __init__(self):
        self.divisions = {
            "network": "NETWORK_ANALYSIS",
            "research": "RESEARCH",
            "code": "CODE_REVIEW",
            "audit": "AUDIT",
            "general": "GENERAL",
            "log": "LOG_ANALYSIS"
        }

    def spawn_division(self, division: str, count: int = 5):
        division = division.lower()
        purpose = self.divisions.get(division, "GENERAL")
        print(f"Spawning {count} Lvl 1 workers in {division.upper()} division...")
        return [Lvl1Worker(purpose=purpose) for _ in range(count)]

class StressTestModeV13:
    def __init__(self):
        self.level = 1
        self.max_workers = {1: 4, 2: 8, 3: 12, 4: 20, 5: 30, 6: 50, 7: 80, 8: 120, 9: 200}
        self.sleep_between = {1: 2.0, 2: 1.0, 3: 0.5, 4: 0.3, 5: 0.2, 6: 0.1, 7: 0.05, 8: 0.02, 9: 0.01}
        self.use_real_work = True  # Real work enabled by default
        self.spawner = DivisionSpawner()
        print("🔥 StressTestMode v13 ready - real work + aggressive auto scaling")

    def set_level(self, level: int):
        if 1 <= level <= 9:
            self.level = level
            print(f"Level {level} → max {self.max_workers[level]} workers, sleep {self.sleep_between[level]}s")

    def run_batch(self, start_level: int, end_level: int, task: str, division: str = "network"):
        print(f"\n=== Starting Auto Batch {start_level}-{end_level} ===")
        for level in range(start_level, end_level + 1):
            self.set_level(level)
            num_workers = min(self.max_workers.get(level, 30), 30)  # safety cap for now

            print(f"\nRunning Level {level} with {num_workers} workers...")

            start_time = datetime.now()
            workers = self.spawner.spawn_division(division, num_workers)
            results = []

            for i, w in enumerate(workers):
                print(f"   Worker {i+1}/{num_workers} starting...")
                result = w.perform_task(task + " [REAL FOREST TOOLS]")
                results.append(result)
                time.sleep(self.sleep_between[self.level])

            duration = (datetime.now() - start_time).total_seconds()
            final_cpu = psutil.cpu_percent()
            final_mem = psutil.virtual_memory().percent

            print(f"Level {level} completed in {duration:.1f}s | CPU: {final_cpu:.1f}% | RAM: {final_mem:.1f}%")

            # Safety pause if load is high
            if final_cpu > 85 or final_mem > 88:
                print("⚠️ High load detected - pausing 15s for cooling")
                time.sleep(15)

        print(f"=== Batch {start_level}-{end_level} complete ===")

if __name__ == "__main__":
    tester = StressTestModeV13()
    
    # Run first batch (0-9)
    tester.run_batch(0, 9, "Analyze latest network scan for suspicious devices", division="network")
    
    # Uncomment for heavier batches when ready
    # tester.run_batch(10, 19, "Analyze latest network scan for suspicious devices", division="network")
