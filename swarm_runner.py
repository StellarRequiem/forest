# swarm_runner.py — High-gear scheduled swarm with telemetry (fixed)

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import time
import schedule
import psutil
import json
from training.generator.agent_trainer import trainer
from deep_research import DeepResearchLoop

class SwarmRunner:
    def __init__(self):
        self.research_loop = DeepResearchLoop()
        self.queue_file = Path("swarm_queue.json")
        self.max_cpu = 75
        self.max_ram = 80
        self.running = False
        self.current_scale = 1
        self.load_queue()

    def load_queue(self):
        if not self.queue_file.exists():
            self.queue = [
                "design a modern SaaS dashboard using Ollama design system",
                "build a clean agent training report UI",
                "create a clean agent submission form",
                "improve the critic worker prompt for better JSON output",
                "generate a full agent bootcamp progress dashboard"
            ]
            self.save_queue()
        else:
            self.queue = json.loads(self.queue_file.read_text())

    def save_queue(self):
        self.queue_file.write_text(json.dumps(self.queue, indent=2))

    def telemetry_ok(self):
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        print(f"[TELEMETRY] CPU: {cpu:.1f}% | RAM: {ram:.1f}% | Scale: {self.current_scale}")
        if cpu > self.max_cpu or ram > self.max_ram:
            print("⚠️ HIGH LOAD — pausing swarm")
            return False
        return True

    def run_one_cycle(self, subject):
        if not self.telemetry_ok():
            return False
        print(f"\n🚀 Running cycle on: {subject}")
        try:
            result = self.research_loop.start_research(target=subject, design_brand="ollama")
            print(f"✅ Cycle complete")
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    def scheduled_run(self):
        if not self.queue or not self.running:
            return
        for _ in range(self.current_scale):
            if not self.queue or not self.telemetry_ok():
                break
            subject = self.queue.pop(0)
            self.save_queue()
            self.run_one_cycle(subject)

    def start(self, scale: int = 1, interval_seconds: int = 180):
        self.running = True
        self.current_scale = max(1, min(scale, 3))
        print(f"\n🌲 SWARM RUNNER STARTED — Scale {self.current_scale} | Every {interval_seconds}s")
        schedule.every(interval_seconds).seconds.do(self.scheduled_run)
        while self.running:
            schedule.run_pending()
            time.sleep(5)

    def stop(self):
        self.running = False
        print("🛑 Swarm Runner stopped.")

runner = SwarmRunner()
