import time
import psutil
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
            "general": "GENERAL"
        }

    def spawn_division(self, division: str, count: int = 5):
        division = division.lower()
        purpose = self.divisions.get(division, "GENERAL")
        print(f"Spawning {count} Lvl 1 workers in {division.upper()} division...")
        return [Lvl1Worker(purpose=purpose) for _ in range(count)]

class StressTestModeV10:
    def __init__(self):
        self.level = 1
        self.max_workers = {1: 4, 2: 8, 3: 12, 4: 20, 5: 30}
        self.sleep_between = {1: 2.0, 2: 1.0, 3: 0.5, 4: 0.3, 5: 0.1}
        self.use_real_work = False
        self.spawner = DivisionSpawner()
        print("🔥 StressTestMode v10 ready - real work + specialized divisions")

    def set_level(self, level: int):
        if 1 <= level <= 5:
            self.level = level
            print(f"Level {level} → max {self.max_workers[level]} workers, sleep {self.sleep_between[level]}s")

    def enable_real_work(self):
        self.use_real_work = True
        print("✅ Real work mode ENABLED - Lvl 1 workers will use actual Forest tools")

    def run_stress_test(self, task: str, division: str = "general", num_workers: int = None):
        if num_workers is None:
            num_workers = self.max_workers[self.level]

        print(f"\n🔥 Stress Test Level {self.level} — {num_workers} Lvl 1 workers in {division.upper()} division")
        print(f"   Task: {task}")
        print(f"   Real work: {self.use_real_work}")

        # Hardware safety
        cpu = psutil.cpu_percent(interval=0.5)
        mem = psutil.virtual_memory().percent
        if (cpu > 80 or mem > 85) and self.level >= 4:
            print(f"⚠️ High load (CPU {cpu:.1f}%, RAM {mem:.1f}%) — reducing to 8 workers")
            num_workers = min(num_workers, 8)

        workers = self.spawner.spawn_division(division, num_workers)
        results = []

        start_time = datetime.now()

        for i, w in enumerate(workers):
            print(f"   Worker {i+1}/{num_workers} starting...")
            if self.use_real_work:
                result = w.perform_task(task + " [REAL FOREST TOOLS]")
            else:
                result = w.perform_task(task)
            results.append(result)
            time.sleep(self.sleep_between[self.level])

        duration = (datetime.now() - start_time).total_seconds()
        final_cpu = psutil.cpu_percent()
        final_mem = psutil.virtual_memory().percent

        print(f"✅ Level {self.level} completed in {duration:.1f}s with {num_workers} workers")
        print(f"   Final CPU: {final_cpu:.1f}%, RAM: {final_mem:.1f}%")
        return results

if __name__ == "__main__":
    mode = StressTestModeV10()
    mode.set_level(2)
    mode.run_stress_test("Analyze latest network scan for suspicious devices", division="network", num_workers=6)
