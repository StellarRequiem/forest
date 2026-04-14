# ISOLATED_SWARM.py — Forces ONLY the clean v5.0 core
import sys
from pathlib import Path

# Force only the clean core path
sys.path = [str(Path("core"))] + [p for p in sys.path if "Forest" not in str(p)]

from cus_core import CUSCore
import time

class IsolatedSwarm:
    def __init__(self):
        self.cus = CUSCore()
        self.queue = [
            "design a modern SaaS dashboard using Ollama design system",
            "build a clean agent training report UI with proper spacing",
            "create a clean agent submission form following Ollama design rules"
        ]
        self.running = False

    def run_cycle(self):
        if not self.queue:
            print("✅ Queue empty. Swarm finished.")
            self.running = False
            return

        task = self.queue.pop(0)
        print(f"\n🚀 Isolated swarm → {task}")

        # Force deep_research through clean core
        result = self.cus.process_proposal(f"deep_research:{task}")
        print(result)
        print("=" * 80)

    def start(self):
        self.running = True
        print("🌲 Isolated v5.0 Swarm started — Using ONLY clean core\n")

        while self.running:
            self.run_cycle()
            if self.running:
                print("Waiting 60 seconds before next task...")
                time.sleep(60)

if __name__ == "__main__":
    swarm = IsolatedSwarm()
    try:
        swarm.start()
    except KeyboardInterrupt:
        print("\n🛑 Isolated swarm stopped.")
