import time
import multiprocessing
from lvl1_worker import Lvl1Worker
from enforcer import EnforcerTeam
import psutil  # for basic CPU monitoring

class StressTestMode:
    def __init__(self):
        self.level = 1  # 1 = light, 5 = aggressive but safe
        self.max_workers = {1: 4, 2: 8, 3: 12, 4: 20, 5: 30}  # safe limits for Mac mini
        self.sleep_between_tasks = {1: 2.0, 2: 1.0, 3: 0.5, 4: 0.3, 5: 0.1}
        print("🔥 StressTestMode initialized - safe hardware limits active")

    def set_level(self, level: int):
        if 1 <= level <= 5:
            self.level = level
            print(f"StressTestMode set to Level {level} (max {self.max_workers[level]} workers)")
        else:
            print("Level must be 1-5")

    def run_parallel_task(self, task: str, num_workers: int = None):
        if num_workers is None:
            num_workers = self.max_workers[self.level]

        print(f"\n🔥 Running Stress Test Level {self.level} with {num_workers} Lvl 1 workers")
        print(f"   Task: {task}")
        print(f"   Sleep between tasks: {self.sleep_between_tasks[self.level]}s")

        # Safety check
        cpu_percent = psutil.cpu_percent(interval=0.5)
        if cpu_percent > 85 and self.level >= 4:
            print("⚠️ High CPU detected - reducing workers for safety")
            num_workers = min(num_workers, 8)

        workers = [Lvl1Worker(purpose="stress_test") for _ in range(num_workers)]
        results = []

        for i, worker in enumerate(workers):
            print(f"   Worker {i+1}/{num_workers} starting...")
            result = worker.perform_task(task)
            results.append(result)
            time.sleep(self.sleep_between_tasks[self.level])  # prevent thermal throttle

        print(f"✅ Stress Test Level {self.level} completed with {num_workers} workers")
        return results

# Quick test
if __name__ == "__main__":
    mode = StressTestMode()
    mode.set_level(2)
    mode.run_parallel_task("Analyze latest network scan for suspicious devices", num_workers=6)
