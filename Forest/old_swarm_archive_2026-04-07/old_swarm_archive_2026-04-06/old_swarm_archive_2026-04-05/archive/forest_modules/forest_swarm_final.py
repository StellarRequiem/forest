from swarm_controller import SwarmController
from lvl1_worker import Lvl1Worker
from datetime import datetime

class ForestSwarmFinal:
    def __init__(self):
        self.controller = SwarmController()
        self.workers = []  # Will hold active Lvl 1 workers
        print("🌲 Forest Swarm Final - Full Caste Unity Active")

    def bootstrap(self):
        print("\n=== Bootstrapping Full Swarm ===")
        status = self.controller.bootstrap_swarm()
        print("✅ Swarm ready")
        return status

    def execute_task(self, task: str, num_workers: int = 5):
        """Headmaster delegates task to Lvl 1 workers"""
        print(f"\n[Forest Swarm] Executive Order: {task}")
        
        # Headmaster decision
        result = self.controller.run_task(task)
        
        # Spawn and assign Lvl 1 workers
        print(f"[Swarm] Spawning {num_workers} Lvl 1 workers for parallel execution...")
        self.workers = [Lvl1Worker(purpose="task_executor") for _ in range(num_workers)]
        
        # Simulate parallel work
        worker_results = []
        for i, worker in enumerate(self.workers):
            print(f"   Worker {i+1}/{num_workers} executing...")
            res = worker.perform_task(task)
            worker_results.append(res)
        
        print(f"\n[Swarm] {num_workers} workers completed task")
        return {"status": "completed", "worker_count": num_workers, "results": worker_results}

if __name__ == "__main__":
    swarm = ForestSwarmFinal()
    swarm.bootstrap()
    
    # Real test task
    final_result = swarm.execute_task("Perform a deep audit on the latest network scan and flag any suspicious devices", num_workers=5)
    print("\n=== Final Swarm Execution Result ===")
    print(final_result)
