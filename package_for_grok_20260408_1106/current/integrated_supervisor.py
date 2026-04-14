from headmaster_controller import HeadmasterController
from core_identity import register_agent

class IntegratedSupervisor:
    def __init__(self):
        self.headmaster = HeadmasterController()
        self.identity = register_agent(tier=4, role="supervisor", purpose="coordinator")
        print(f"Integrated Supervisor initialized under Headmaster {self.headmaster.headmaster.identity}")

    def process_task(self, task_description: str):
        """Headmaster decides, then delegates to old supervisor logic"""
        print(f"\n[Headmaster] Received task: {task_description}")
        
        # Headmaster makes high-level decision
        decision = self.headmaster.delegate_to_supervisor(task_description)
        
        # For now we simulate delegation to existing supervisor behavior
        if "research" in task_description.lower() or "audit" in task_description.lower():
            print(f"[Supervisor] Delegating to Lvl 2/1 workers for {task_description}")
            # In real code we would spawn or call existing agents here
            return {"status": "delegated_to_workers", "task": task_description}
        
        return {"status": "processed", "decision": decision}

    def get_full_status(self):
        return self.headmaster.get_swarm_status()

if __name__ == "__main__":
    supervisor = IntegratedSupervisor()
    result = supervisor.process_task("Audit the latest network scan for anomalies")
    print("\nTask Result:", result)
    print("Swarm Status:", supervisor.get_full_status())
