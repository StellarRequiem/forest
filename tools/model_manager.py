#!/usr/bin/env python3
"""
🌲 Forest Model Manager v2.1-git — BlueAgent Powered
Manages local Ollama models with status and pull capabilities.
"""
import sys
import os
import subprocess
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.blue_agent import BlueAgent

class ModelManagerAgent(BlueAgent):
    def __init__(self):
        super().__init__(name="ModelManagerAgent", model="llama3.2:3b", role="Local Model Guardian")

    def run(self, action="status"):
        if not self.credential:
            self.activate()

        print(f"🌲 Forest Local Model Manager v2.1-git @ {datetime.now()}")

        try:
            if action == "--pull":
                print("Pulling recommended small models (this may take a few minutes)...")
                models_to_pull = ["gemma2:2b", "llama3.2:3b", "phi3:mini", "qwen2.5:3b"]
                for m in models_to_pull:
                    print(f"→ Pulling {m} ...")
                    subprocess.run(["ollama", "pull", m], check=True)
                print("✅ All recommended models pulled.")
                self.log_action("MODEL_PULL", f"Pulled {len(models_to_pull)} models")
            else:
                # Default: status
                result = subprocess.check_output(["ollama", "list"], text=True)
                print("=== Installed Models ===")
                print(result.strip())

                recommended = ["gemma2:2b", "llama3.2:3b", "phi3:mini", "qwen2.5:3b", "mistral:7b"]
                print("\n=== Recommended ===")
                for rec in recommended:
                    status = "✅" if any(rec in line for line in result.splitlines()) else "⏳ Missing"
                    print(f"{status} {rec}")

                self.log_action("MODEL_STATUS", "Listed installed models")
        except FileNotFoundError:
            print("❌ Ollama not found. Is it installed and in PATH?")
        except Exception as e:
            print(f"❌ Error: {e}")
            self.log_action("MODEL_ERROR", str(e))

if __name__ == "__main__":
    import sys
    action = sys.argv[1] if len(sys.argv) > 1 else "--status"
    agent = ModelManagerAgent()
    agent.run(action)
