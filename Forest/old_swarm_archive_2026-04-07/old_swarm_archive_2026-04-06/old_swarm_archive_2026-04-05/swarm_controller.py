from headmaster_controller import HeadmasterController
from enforcer import EnforcerTeam
from core_identity import register_agent
from datetime import datetime

class SwarmController:
    def __init__(self):
        self.headmaster = HeadmasterController()
        self.enforcers = EnforcerTeam(count=5)
        self.identity = register_agent(tier=5, role="swarm_controller", purpose="orchestrator")
        print(f"🎛️ SwarmController initialized under Headmaster {self.headmaster.headmaster.identity.agent_id}")

    def bootstrap_swarm(self):
        """Full bootstrap: Headmaster spawns, Enforcers monitor"""
        print("\n=== Bootstrapping Full Swarm ===")
        
        self.headmaster.headmaster.spawn_agent(tier=4, role="supervisor", purpose="coordinator", count=1)
        self.headmaster.headmaster.spawn_agent(tier=3, role="warden", purpose="security", count=3)
        self.headmaster.headmaster.spawn_agent(tier=2, role="auditor", purpose="review", count=8)
        self.headmaster.headmaster.spawn_agent(tier=1, role="worker", purpose="research", count=30)

        status = self.headmaster.get_swarm_status()
        self.enforcers.scan_swarm(status)

        print("✅ Full swarm bootstrapped and monitored by Enforcers")
        return status

    def get_full_status(self):
        """Expose Headmaster status"""
        return self.headmaster.get_swarm_status()

    def run_task(self, task: str):
        """Main entry point for any task"""
        print(f"\n[SwarmController] Received executive task: {task}")
        result = self.headmaster.delegate_to_supervisor(task)
        return result

if __name__ == "__main__":
    controller = SwarmController()
    status = controller.bootstrap_swarm()
    print("\nFinal Swarm Status:", status)
    
    # Test a real Forest-style task
    task_result = controller.run_task("Perform a deep audit on the latest network scan and flag any suspicious devices")
    print("\nFinal Task Result:", task_result)
