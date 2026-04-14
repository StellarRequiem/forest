#!/usr/bin/env python3
"""
Final Clean Swarm Runner for v5.0
Uses ONLY the clean core files. No old code.
"""

import sys
from pathlib import Path
import time

# Force clean path - only core folder
core_path = str(Path("core").absolute())
sys.path.insert(0, core_path)
print(f"Using core path: {core_path}")

# Import directly from core
from cus_core import CUSCore

class FinalSwarm:
    def __init__(self):
        print("Initializing clean CUS core...")
        self.cus = CUSCore()
        self.queue = [
            "design a modern SaaS dashboard using Ollama design system",
            "build a clean agent training report UI with proper spacing",
            "create a clean agent submission form following Ollama design rules"
        ]
        self.running = False

    def run_cycle(self):
        if not self.queue:
            print("✅ Queue empty. Swarm complete.")
            self.running = False
            return

        task = self.queue.pop(0)
        print(f"\n🚀 Final swarm cycle → {task}")

        # Use deep_research through the clean core
        proposal = f"deep_research:{task}"
        result = self.cus.process_proposal(proposal)
        print(result)
        print("=" * 90)

    def start(self):
        self.running = True
        print("\n🌲 Final v5.0 Clean Swarm started")
        print("Only using: Local RAG + Deep Research + Design System\n")

        while self.running:
            self.run_cycle()
            if self.running:
                print("Waiting 60 seconds before next task...\n")
                time.sleep(60)

    def stop(self):
        self.running = False
        print("🛑 Swarm stopped.")

if __name__ == "__main__":
    swarm = FinalSwarm()
    try:
        swarm.start()
    except KeyboardInterrupt:
        swarm.stop()
    except Exception as e:
        print(f"Error: {e}")
