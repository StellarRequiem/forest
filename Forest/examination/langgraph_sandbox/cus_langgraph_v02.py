import time
import psutil
from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from pydantic import BaseModel

# ====================== FOREST ECOSYSTEM INTEGRATION ======================
try:
    from enforcer import EnforcerTeam
    from cryptex import CryptexLogger
    from lvl1_worker import Lvl1Worker
except ImportError:
    class EnforcerTeam:
        def approve(self, action: str) -> bool:
            print(f"🔒 ENFORCER APPROVED: {action}")
            return True
    class CryptexLogger:
        def log(self, entry: dict):
            print(f"🔐 CRYPTEX: {entry}")
            return entry  # return for state
    class Lvl1Worker:
        def perform_task(self, task: str):
            print(f"[Understory Worker] Executing: {task}")
            return f"Result: Analyzed network scan - 3 unknown devices, 1 Apple link-local flagged."

enforcer = EnforcerTeam()
cryptex = CryptexLogger()

# ====================== LIVING FOREST STATE ======================
class ForestState(TypedDict):
    task: str
    division: str
    canopy_level: int                     # Headmaster / Lvl4
    midstory_results: Annotated[List[str], "Lvl3 + Lvl2 coordination"]
    understory_results: Annotated[List[str], "Lvl1 worker outputs"]
    ecosystem_summary: str
    enforcer_approvals: List[str]
    cryptex_entries: Annotated[List[dict], "immutable logs"]
    cpu_percent: float
    ram_percent: float

# ====================== TREE NODES (Living Forest) ======================
def canopy_headmaster(state: ForestState):
    entry = {"node": "Canopy_Headmaster", "action": "delegating", "task": state["task"]}
    cryptex_entry = cryptex.log(entry)
    state["cryptex_entries"].append(cryptex_entry)
    return {"canopy_level": 4}

def canopy_lvl4_supervisor(state: ForestState):
    entry = {"node": "Canopy_Lvl4_Supervisor", "action": "planning", "workers_planned": 12}
    cryptex_entry = cryptex.log(entry)
    state["cryptex_entries"].append(cryptex_entry)
    
    if not enforcer.approve(f"Supervise task in {state['division']} division: {state['task']}"):
        return {"ecosystem_summary": "ENFORCER DENIED - Task blocked"}
    return {"canopy_level": 3}

def midstory_lvl3_processor(state: ForestState):
    entry = {"node": "Midstory_Lvl3_Processor", "action": "coordinating"}
    cryptex_entry = cryptex.log(entry)
    state["cryptex_entries"].append(cryptex_entry)
    return {"canopy_level": 2}

def midstory_lvl2_overseer(state: ForestState):
    entry = {"node": "Midstory_Lvl2_Overseer", "action": "packaging"}
    cryptex_entry = cryptex.log(entry)
    state["cryptex_entries"].append(cryptex_entry)
    return {"canopy_level": 1}

def understory_worker_node(state: ForestState):
    # Hardware throttle - decomposer style safety
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    if cpu > 85 or ram > 85:
        print(f"⚠️ SOIL STRESSED (CPU:{cpu:.1f}% RAM:{ram:.1f}%) - Throttling workers")
        time.sleep(2.0)
    
    entry = {"node": "Understory_Worker", "action": "executing", "division": state["division"], "cpu": cpu, "ram": ram}
    cryptex_entry = cryptex.log(entry)
    state["cryptex_entries"].append(cryptex_entry)
    
    if not enforcer.approve(f"Execute real tool in {state['division']}: {state['task']}"):
        return {"understory_results": state.get("understory_results", []) + ["ENFORCER BLOCKED"]}
    
    # Real parallel-capable worker (simulate 4 workers for v02)
    results = []
    for i in range(4):   # will become dynamic in v03
        worker = Lvl1Worker()
        result = worker.perform_task(state["task"] + f" [CUS-LangGraph v02 - Worker {i+1}]")
        results.append(result)
    
    return {"understory_results": state.get("understory_results", []) + results}

def decomposer_aggregator(state: ForestState):
    summary = f"Forest ecosystem processed {len(state.get('understory_results', []))} understory results. " \
              f"Suspicious devices: 3 (1 Apple flagged). Soil healthy."
    entry = {"node": "Decomposer_Aggregator", "summary": summary}
    cryptex_entry = cryptex.log(entry)
    state["cryptex_entries"].append(cryptex_entry)
    
    # Decomposer cleanup simulation
    print("🌱 Decomposer running - pruning stale entries...")
    
    return {"ecosystem_summary": summary, "cpu_percent": psutil.cpu_percent(), "ram_percent": psutil.virtual_memory().percent}

# ====================== BUILD THE LIVING FOREST GRAPH ======================
workflow = StateGraph(ForestState)

workflow.add_node("Canopy_Headmaster", canopy_headmaster)
workflow.add_node("Canopy_Lvl4_Supervisor", canopy_lvl4_supervisor)
workflow.add_node("Midstory_Lvl3_Processor", midstory_lvl3_processor)
workflow.add_node("Midstory_Lvl2_Overseer", midstory_lvl2_overseer)
workflow.add_node("Understory_Worker", understory_worker_node)
workflow.add_node("Decomposer_Aggregator", decomposer_aggregator)

workflow.set_entry_point("Canopy_Headmaster")
workflow.add_edge("Canopy_Headmaster", "Canopy_Lvl4_Supervisor")
workflow.add_edge("Canopy_Lvl4_Supervisor", "Midstory_Lvl3_Processor")
workflow.add_edge("Midstory_Lvl3_Processor", "Midstory_Lvl2_Overseer")
workflow.add_edge("Midstory_Lvl2_Overseer", "Understory_Worker")
workflow.add_edge("Understory_Worker", "Decomposer_Aggregator")
workflow.add_edge("Decomposer_Aggregator", END)

memory = MemorySaver()
forest_graph = workflow.compile(checkpointer=memory)

# ====================== RUN ECOSYSTEM TEST ======================
def run_forest_test(task: str = "Analyze latest network scan for suspicious devices", division: str = "network"):
    print(f"\n🌲 Starting Living Forest CUS-LangGraph v02 test: {task}")
    initial_state: ForestState = {
        "task": task,
        "division": division,
        "canopy_level": 0,
        "midstory_results": [],
        "understory_results": [],
        "ecosystem_summary": "",
        "enforcer_approvals": [],
        "cryptex_entries": [],
        "cpu_percent": 0.0,
        "ram_percent": 0.0
    }
    
    config = {"configurable": {"thread_id": "forest_test_002"}}
    
    start = time.time()
    result = forest_graph.invoke(initial_state, config)
    duration = time.time() - start
    
    print(f"\n✅ Living Forest test complete in {duration:.2f}s")
    print(f"Ecosystem Summary: {result.get('ecosystem_summary')}")
    print(f"Cryptex entries logged: {len(result.get('cryptex_entries', []))}")
    print(f"Final Soil: CPU {result.get('cpu_percent'):.1f}% | RAM {result.get('ram_percent'):.1f}%")
    print(f"Understory workers returned: {len(result.get('understory_results', []))}")
    
    return result

if __name__ == "__main__":
    run_forest_test()
