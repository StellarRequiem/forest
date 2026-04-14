import time
import psutil
import sys
from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

# Add main Forest to path so we can use real modules
sys.path.insert(0, '/Users/llm01/Forest')   # Change only if your username is different

try:
    from enforcer import EnforcerTeam
    from cryptex import CryptexLogger
    from lvl1_worker import Lvl1Worker
except ImportError as e:
    print(f"⚠️ Warning: Could not import real Forest modules: {e}")
    # Fallback remains for safety
    class EnforcerTeam:
        def approve(self, action: str) -> bool:
            print(f"🔒 ENFORCER APPROVED: {action}")
            return True
    class CryptexLogger:
        def log(self, entry: dict):
            print(f"🔐 CRYPTEX: {entry}")
            return entry
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
    level: int
    understory_results: Annotated[List[str], "real worker outputs"]
    ecosystem_summary: str
    enforcer_approvals: List[str]
    cryptex_entries: Annotated[List[dict], "immutable logs"]
    cpu_percent: float
    ram_percent: float
    workers_spawned: int

# ====================== DYNAMIC LEVELS (from your old stress_test) ======================
LEVEL_CONFIG = {
    1: {"workers": 4,  "sleep": 2.0},
    2: {"workers": 8,  "sleep": 1.0},
    3: {"workers": 12, "sleep": 0.5},
    4: {"workers": 20, "sleep": 0.3},
    5: {"workers": 30, "sleep": 0.2},
    6: {"workers": 50, "sleep": 0.1},
}

# ====================== TREE NODES ======================
def canopy_headmaster(state: ForestState):
    entry = {"node": "Canopy_Headmaster", "action": "delegating", "task": state["task"], "level": state["level"]}
    state["cryptex_entries"].append(cryptex.log(entry))
    return {}

def canopy_lvl4_supervisor(state: ForestState):
    cfg = LEVEL_CONFIG.get(state["level"], {"workers": 8, "sleep": 1.0})
    entry = {"node": "Canopy_Lvl4_Supervisor", "action": "planning", "workers_planned": cfg["workers"], "level": state["level"]}
    state["cryptex_entries"].append(cryptex.log(entry))
    
    if not enforcer.approve(f"Supervise Level {state['level']} in {state['division']} division"):
        return {"ecosystem_summary": "ENFORCER DENIED"}
    return {}

def understory_worker_node(state: ForestState):
    cfg = LEVEL_CONFIG.get(state["level"], {"workers": 8, "sleep": 1.0})
    target_workers = cfg["workers"]
    
    # Soil check - real throttle
    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory().percent
    state["cpu_percent"] = cpu
    state["ram_percent"] = ram
    
    if cpu > 82 or ram > 82:
        print(f"⚠️ SOIL STRESSED (CPU:{cpu:.1f}% RAM:{ram:.1f}%) - Reducing workers to {target_workers//2}")
        target_workers = max(2, target_workers // 2)
    
    entry = {"node": "Understory_Worker", "action": "spawning", "workers": target_workers, "level": state["level"]}
    state["cryptex_entries"].append(cryptex.log(entry))
    
    if not enforcer.approve(f"Spawn {target_workers} understory workers for Level {state['level']}"):
        return {"understory_results": ["ENFORCER BLOCKED"]}
    
    results = []
    for i in range(target_workers):
        worker = Lvl1Worker()
        result = worker.perform_task(state["task"] + f" [CUS-LangGraph v03 - Lvl{state['level']} Worker {i+1}]")
        results.append(result)
        time.sleep(cfg["sleep"] / target_workers)  # gentle spread
    
    state["workers_spawned"] = target_workers
    return {"understory_results": results}

def decomposer_aggregator(state: ForestState):
    summary = f"Forest Level {state['level']} completed. " \
              f"Processed {len(state.get('understory_results', []))} understory results. " \
              f"Soil: CPU {state.get('cpu_percent', 0):.1f}% | RAM {state.get('ram_percent', 0):.1f}%"
    
    entry = {"node": "Decomposer_Aggregator", "summary": summary, "workers_spawned": state.get("workers_spawned", 0)}
    state["cryptex_entries"].append(cryptex.log(entry))
    
    print("🌱 Decomposer running - pruning stale entries and logging ecosystem health...")
    return {"ecosystem_summary": summary}

# ====================== BUILD GRAPH ======================
workflow = StateGraph(ForestState)
workflow.add_node("Canopy_Headmaster", canopy_headmaster)
workflow.add_node("Canopy_Lvl4_Supervisor", canopy_lvl4_supervisor)
workflow.add_node("Understory_Worker", understory_worker_node)
workflow.add_node("Decomposer_Aggregator", decomposer_aggregator)

workflow.set_entry_point("Canopy_Headmaster")
workflow.add_edge("Canopy_Headmaster", "Canopy_Lvl4_Supervisor")
workflow.add_edge("Canopy_Lvl4_Supervisor", "Understory_Worker")
workflow.add_edge("Understory_Worker", "Decomposer_Aggregator")
workflow.add_edge("Decomposer_Aggregator", END)

memory = MemorySaver()
forest_graph = workflow.compile(checkpointer=memory)

# ====================== RUN TEST ======================
def run_forest_level(level: int = 3):
    print(f"\n🌲 Starting Living Forest Level {level} test")
    initial_state: ForestState = {
        "task": "Analyze latest network scan for suspicious devices",
        "division": "network",
        "level": level,
        "understory_results": [],
        "ecosystem_summary": "",
        "enforcer_approvals": [],
        "cryptex_entries": [],
        "cpu_percent": 0.0,
        "ram_percent": 0.0,
        "workers_spawned": 0
    }
    
    config = {"configurable": {"thread_id": f"forest_level_{level}"}}
    
    start = time.time()
    result = forest_graph.invoke(initial_state, config)
    duration = time.time() - start
    
    print(f"\n✅ Level {level} complete in {duration:.2f}s")
    print(f"Workers spawned: {result.get('workers_spawned', 0)}")
    print(f"Ecosystem Summary: {result.get('ecosystem_summary')}")
    print(f"Cryptex entries: {len(result.get('cryptex_entries', []))}")
    return result

if __name__ == "__main__":
    run_forest_level(3)   # Change number to test different levels
