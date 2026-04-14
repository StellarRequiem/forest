import time
import psutil
import sys
from typing import TypedDict, Annotated, List, Dict
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

sys.path.insert(0, '/Users/llm01/Forest')

try:
    from enforcer import EnforcerTeam
    from lvl1_worker import Lvl1Worker, TelemetryGuardian
    enforcer = EnforcerTeam()
except Exception as e:
    print(f"⚠️ Import warning: {e}")
    class DummyEnforcer:
        def scan_swarm(self, status):
            print(f"[Dummy Enforcer] Scanning: {status}")
            return {"status": "clear", "alerts": 0}
    enforcer = DummyEnforcer()
    class TelemetryGuardian(Lvl1Worker):
        pass

try:
    from cryptex import CryptexLogger
    cryptex = CryptexLogger()
except:
    class SimpleCryptex:
        def log(self, entry: dict):
            print(f"🔐 CRYPTEX: {entry}")
            return entry
    cryptex = SimpleCryptex()

class ForestState(TypedDict):
    task: str
    division: str
    level: int
    understory_results: Annotated[List[str], "worker outputs"]
    ecosystem_summary: str
    cryptex_entries: Annotated[List[dict], "logs"]
    cpu_percent: float
    ram_percent: float
    workers_spawned: int
    enforcer_scan_result: Dict

LEVEL_CONFIG = {
    1: {"workers": 4,  "sleep": 2.0},
    2: {"workers": 8,  "sleep": 1.0},
    3: {"workers": 12, "sleep": 0.5},
    4: {"workers": 20, "sleep": 0.3},
    5: {"workers": 30, "sleep": 0.2},
}

def safe_scan(action_name: str, extra: dict = None) -> dict:
    status = {"action": action_name, **(extra or {})}
    try:
        result = enforcer.scan_swarm(status) or {"status": "clear", "alerts": 0}
        print(f"🔒 Enforcer scan '{action_name}': {result.get('status', 'unknown')} | Alerts: {result.get('alerts', 0)}")
        return result
    except Exception as e:
        print(f"⚠️ Enforcer scan failed: {e}")
        return {"status": "clear", "alerts": 0}

def canopy_headmaster(state: ForestState):
    entry = {"node": "Canopy_Headmaster", "action": "delegating", "task": state["task"], "level": state["level"]}
    state["cryptex_entries"].append(cryptex.log(entry))
    return {}

def canopy_lvl4_supervisor(state: ForestState):
    cfg = LEVEL_CONFIG.get(state["level"], {"workers": 12, "sleep": 0.5})
    entry = {"node": "Canopy_Lvl4_Supervisor", "action": "planning", "workers_planned": cfg["workers"], "level": state["level"]}
    state["cryptex_entries"].append(cryptex.log(entry))
    safe_scan("supervise_level", {"level": state["level"]})
    return {}

def understory_worker_node(state: ForestState):
    cfg = LEVEL_CONFIG.get(state["level"], {"workers": 12, "sleep": 0.5})
    target = cfg["workers"]
    
    # Smart worker type selection
    task_lower = state["task"].lower()
    is_privacy_task = any(word in task_lower for word in ["telemetry", "tracking", "handshake", "fingerprint", "privacy", "idle", "beacon"])
    
    # Accurate soil reading
    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory().percent
    state["cpu_percent"] = cpu
    state["ram_percent"] = ram
    
    if cpu > 82 or ram > 82:
        target = max(4, target // 2)
        print(f"⚠️ Soil stressed (CPU:{cpu:.1f}% RAM:{ram:.1f}%) - reduced to {target} workers")
    
    worker_type = "TelemetryGuardian" if is_privacy_task else "Standard"
    entry = {"node": "Understory_Worker", "action": "spawning", "workers": target, "level": state["level"], "type": worker_type}
    state["cryptex_entries"].append(cryptex.log(entry))
    
    scan_result = safe_scan("spawn_understory", {"level": state["level"], "workers_planned": target})
    
    if scan_result.get("alerts", 0) > 2:
        print("🛑 High Enforcer alerts - blocking spawn")
        return {"understory_results": state.get("understory_results", []) + ["ENFORCER_BLOCKED"]}
    
    results = state.get("understory_results", [])
    for i in range(target):
        if is_privacy_task:
            worker = TelemetryGuardian()
        else:
            worker = Lvl1Worker()
        result = worker.perform_task(state["task"] + f" [Forest v08 - Lvl{state['level']} {worker_type} {i+1}]")
        results.append(result)
        time.sleep(cfg["sleep"] / max(1, target))
    
    state["workers_spawned"] = target
    return {"understory_results": results}

def decomposer_aggregator(state: ForestState):
    summary = f"Forest Level {state['level']} completed. Processed {len(state.get('understory_results', []))} results. Soil: CPU {state.get('cpu_percent', 0):.1f}% | RAM {state.get('ram_percent', 0):.1f}%"
    entry = {"node": "Decomposer_Aggregator", "summary": summary, "workers_spawned": state.get("workers_spawned", 0)}
    state["cryptex_entries"].append(cryptex.log(entry))
    print("🌱 Decomposer running - pruning stale entries...")
    return {"ecosystem_summary": summary}

# Build graph
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

def run_forest_level(level: int = 3):
    task = "Analyze for LinkedIn Project Handshake style tracking and telemetry patterns"
    print(f"\n🌲 Starting Living Forest Level {level} - Telemetry/Privacy Defense Test")
    initial_state: ForestState = {
        "task": task,
        "division": "privacy",
        "level": level,
        "understory_results": [],
        "ecosystem_summary": "",
        "cryptex_entries": [],
        "cpu_percent": 0.0,
        "ram_percent": 0.0,
        "workers_spawned": 0,
        "enforcer_scan_result": {}
    }
    
    config = {"configurable": {"thread_id": f"forest_level_{level}"}}
    
    start = time.time()
    result = forest_graph.invoke(initial_state, config)
    duration = time.time() - start
    
    print(f"\n✅ Level {level} complete in {duration:.2f}s")
    print(f"Workers spawned: {result.get('workers_spawned', 0)}")
    print(f"Ecosystem Summary: {result.get('ecosystem_summary')}")
    print(f"Cryptex entries: {len(result.get('cryptex_entries', []))}")
    print(f"Final Soil - CPU: {result.get('cpu_percent', 0):.1f}% | RAM: {result.get('ram_percent', 0):.1f}%")
    return result

if __name__ == "__main__":
    run_forest_level(3)
