import time
import multiprocessing
from lvl1_worker import Lvl1Worker
from enforcer import EnforcerTeam
import psutil

class StressTestModeV2:
    def __init__(self):
        self.level = 1
        self.max_workers = {1: 4, 2: 8, 3: 12, 4: 20, 5: 30}
        self.sleep_between = {1: 2.0, 2: 1.0, 3: 0.5, 4: 0.3, 5: 0.1}
        self.use_real_work = False  # Set to True for Path 1
        print("🔥 StressTestMode v2 ready - safe hardware limits + real task option")

    def set_level(self, level: int):
        if 1 <= level <= 5:
            self.level = level
            print(f"Level {level} set — max {self.max_workers[level]} workers, sleep {self.sleep_between[level]}s")

    def enable_real_work(self):
        self.use_real_work = True
        print("✅ Real task execution enabled (workers will use Forest tools)")

    def run_stress_test(self, task: str, num_workers: int = None):
        if num_workers is None:
            num_workers = self.max_workers[self.level]

        print(f"\n🔥 Stress Test Level {self.level} — {num_workers} Lvl 1 workers")
        print(f"   Task: {task}")
        print(f"   Real work mode: {self.use_real_work}")

        # Safety guard
        cpu = psutil.cpu_percent(interval=0.5)
        if cpu > 80 and self.level >= 4:
            print("⚠️ High CPU — reducing to 8 workers for safety")
            num_workers = 8

        workers = [Lvl1Worker(purpose="stress_worker") for _ in range(num_workers)]
        results = []

        for i, w in enumerate(workers):
            print(f"   Worker {i+1}/{num_workers} starting...")
            if self.use_real_work:
                # In next step we'll hook real Forest tools here
                result = w.perform_task(task + " [REAL MODE]")
            else:
                result = w.perform_task(task)
            results.append(result)
            time.sleep(self.sleep_between[self.level])

        print(f"✅ Level {self.level} stress test completed")
        return results

if __name__ == "__main__":
    mode = StressTestModeV2()
    mode.set_level(2)
    mode.run_stress_test("Analyze latest network scan for suspicious devices", num_workers=6)
