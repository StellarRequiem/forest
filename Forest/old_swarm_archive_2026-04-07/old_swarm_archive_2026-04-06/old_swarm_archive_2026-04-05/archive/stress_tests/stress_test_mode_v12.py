import time
import psutil
from lvl1_worker import Lvl1Worker
from enforcer import EnforcerTeam
from datetime import datetime
from stress_test_mode_v11 import StressTestModeV11  # reuse the spawner

class AutoLevelTester:
    def __init__(self):
        self.mode = StressTestModeV11()
        self.mode.enable_real_work()  # Start with real work enabled
        print("🔥 AutoLevelTester v12 ready - batch testing 0-9, 10-19, 20-29...")

    def run_batch(self, start_level: int, end_level: int, task: str, division: str = "network"):
        print(f"\n=== Starting Auto Batch {start_level}-{end_level} ===")
        for level in range(start_level, end_level + 1):
            self.mode.set_level(level)
            num_workers = min(self.mode.max_workers.get(level, 30), 30)  # cap for safety
            print(f"\nRunning Level {level} with {num_workers} workers...")
            
            start_time = datetime.now()
            results = self.mode.run_stress_test(task, division=division, num_workers=num_workers)
            duration = (datetime.now() - start_time).total_seconds()
            
            cpu = psutil.cpu_percent()
            mem = psutil.virtual_memory().percent
            print(f"Level {level} finished in {duration:.1f}s | CPU: {cpu:.1f}% | RAM: {mem:.1f}%")
            
            # Safety pause if load is high
            if cpu > 85 or mem > 88:
                print("⚠️ High load detected - pausing 10s for cooling")
                time.sleep(10)

        print(f"=== Batch {start_level}-{end_level} complete ===")

if __name__ == "__main__":
    tester = AutoLevelTester()
    
    # Run first batch (0-9) - light testing
    tester.run_batch(0, 9, "Analyze latest network scan for suspicious devices", division="network")
    
    # Run second batch (10-19) - medium testing
    # tester.run_batch(10, 19, "Analyze latest network scan for suspicious devices", division="network")
    
    # Run third batch (20-29) - heavy testing (uncomment when ready)
    # tester.run_batch(20, 29, "Analyze latest network scan for suspicious devices", division="network")
