from swarm_controller import SwarmController
from datetime import datetime

class ForestSwarmV2:
    def __init__(self):
        self.controller = SwarmController()
        print("🌲 Forest Swarm v2 Online - Full Caste Unity Active")

    def bootstrap(self):
        print("\n=== Bootstrapping Complete Swarm ===")
        status = self.controller.bootstrap_swarm()
        print("✅ Swarm ready for real tasks")
        return status

    def execute(self, task: str):
        """Main entry point - Headmaster routes the task through the swarm"""
        print(f"\n[Forest Swarm] Executive Order: {task}")
        
        # Headmaster decides how to handle it
        result = self.controller.run_task(task)
        
        # Simulate routing to appropriate level
        if "audit" in task.lower() or "scan" in task.lower():
            print("[Swarm] Routing to Lvl 1 Worker swarm for parallel processing...")
            # In the next step we will actually spawn workers to do the work
            print("   → 30 L1 workers would now analyze network logs in parallel")
        
        return result

if __name__ == "__main__":
    swarm = ForestSwarmV2()
    swarm.bootstrap()
    
    # Real Forest-style task
    result = swarm.execute("Perform a deep audit on the latest network scan and flag any suspicious devices")
    print("\nFinal Result:", result)
