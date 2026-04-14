from swarm_controller import SwarmController
from datetime import datetime

class ForestSwarm:
    def __init__(self):
        self.controller = SwarmController()
        self.bootstrapped = False
        print("🌲 Forest Swarm System Online - Caste Unity Active")

    def bootstrap(self):
        if not self.bootstrapped:
            self.controller.bootstrap_swarm()
            self.bootstrapped = True
            print("✅ Full swarm bootstrapped and monitored by Enforcers")
        return self.controller.get_full_status()

    def execute_task(self, task: str):
        """Main entry point for any task"""
        print(f"\n[Forest Swarm] Executive Command Received: {task}")
        result = self.controller.run_task(task)
        
        # In future versions, this will automatically spawn appropriate Lvl 1 workers
        if "network" in task.lower() or "scan" in task.lower():
            print("[Swarm] Routing to Lvl 1 Worker swarm for network analysis...")
        
        return result

    def status(self):
        return self.controller.get_full_status()

if __name__ == "__main__":
    forest = ForestSwarm()
    forest.bootstrap()
    
    # Test a real Forest-style task
    result = forest.execute_task("Perform a deep audit on the latest network scan and flag any suspicious devices")
    print("\nFinal Task Result:", result)
