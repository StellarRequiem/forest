from headmaster import Headmaster
from core_identity import register_agent, get_agent_identity
from datetime import datetime

class HeadmasterController:
    def __init__(self):
        self.headmaster = Headmaster()
        self.supervisor = None  # Will be linked to existing Supervisor later
        print(f"HeadmasterController initialized under {self.headmaster.identity}")

    def initialize_swarm(self):
        """Headmaster spawns initial key agents"""
        print("\n=== Initializing Swarm ===")
        
        # Spawn core agents with proper tiers
        self.headmaster.spawn_agent(tier=4, role="supervisor", purpose="coordinator", count=1)
        self.headmaster.spawn_agent(tier=3, role="warden", purpose="security", count=5)
        self.headmaster.spawn_agent(tier=2, role="auditor", purpose="review", count=10)
        self.headmaster.spawn_agent(tier=1, role="worker", purpose="research", count=20)
        
        print(f"Total active agents: {len(self.headmaster.active_swarm)}")
        return self.headmaster.report_status()

    def delegate_to_supervisor(self, task: str):
        """Headmaster delegates to existing Supervisor logic"""
        if not self.supervisor:
            print("Headmaster: Supervisor not yet linked. Task queued.")
            return {"status": "queued", "task": task}
        
        print(f"Headmaster delegating to Supervisor: {task}")
        # Here we will later call the real Supervisor
        return {"status": "delegated", "task": task}

    def get_swarm_status(self):
        return self.headmaster.report_status()

if __name__ == "__main__":
    controller = HeadmasterController()
    status = controller.initialize_swarm()
    print("\nSwarm Status:", status)
