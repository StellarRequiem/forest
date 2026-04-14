# core/cus_core.py
# v5.0 - Full Clean CUS Core with Gauntlet Sandbox

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

class CUSCore:
    def __init__(self):
        print("✅ Full v5.0 CUS Core initialized with Gauntlet")
        self.knowledge_base_path = Path("../knowledge_base")

    def process_proposal(self, proposal: str) -> str:
        print(f"[CUS] Processing proposal: {proposal[:100]}...")

        if proposal.startswith("start_gauntlet"):
            try:
                from gauntlet_sandbox import GauntletSandbox
                print("Launching Gauntlet Sandbox...")
                sandbox = GauntletSandbox()
                sandbox.daily_research_update()
                sandbox.run_sandbox_cycle(num_battles=3)
                return "Gauntlet sandbox completed successfully."
            except Exception as e:
                return f"Gauntlet error: {e}"

        elif proposal.startswith("deep_research:"):
            target = proposal.split(":", 1)[1].strip()
            return f"Deep Research started on target: {target}"

        elif proposal.startswith("use_rag:"):
            query = proposal.split(":", 1)[1].strip()
            return f"Local RAG query: {query}"

        elif proposal.startswith("apply_design_system:"):
            brand = proposal.split(":", 1)[1].strip()
            return f"Design system '{brand}' loaded"

        return f"Proposal accepted: {proposal[:100]}..."

    def get_status(self):
        return {
            "status": "full core active",
            "knowledge_base": self.knowledge_base_path.exists()
        }

if __name__ == "__main__":
    core = CUSCore()
    print("\n=== v5.0 CUS Core Ready ===")
    print("Available commands:")
    print("  start_gauntlet")
    print("  deep_research:<target>")
    print("  use_rag:<query>")
    print("  apply_design_system:ollama")
    print("  status")
