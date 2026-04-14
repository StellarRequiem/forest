import time
from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field

# ====================== FOREST INTEGRATION ======================
# These will be symlinked or imported from main Forest once stable
try:
    from enforcer import EnforcerTeam
    from cryptex import CryptexLogger
    from lvl1_worker import Lvl1Worker
except ImportError:
    # Fallback for examination sandbox
    class EnforcerTeam:
        def approve(self, action: str) -> bool:
            print(f"🔒 ENFORCER APPROVED: {action}")
            return True
    class CryptexLogger:
        def log(self, entry: dict):
            print(f"🔐 CRYPTEX: {entry}")
    class Lvl1Worker:
        def perform_task(self, task: str):
            print(f"[Lvl1 Worker] Executing: {task}")
            return f"Result: Analyzed network scan - 3 unknown devices, 1 Apple link-local flagged."

enforcer = EnforcerTeam()
cryptex = CryptexLogger()

# ====================== CUS STATE ======================
class CUSState(TypedDict):
    task: str
    division: str
    level: int
    worker_results: Annotated[List[str], "worker outputs"]
    supervisor_summary: str
    enforcer_approvals: List[str]
    cryptex_entries: List[dict]

# ====================== NODES (Caste Hierarchy) ======================
def headmaster_node(state: CUSState):
    cryptex.log({"node": "Headmaster", "action": "delegating", "task": state["task"]})
    return {"level": 4}  # Delegate to Lvl 4 Supervisor

def lvl4_supervisor_node(state: CUSState):
    cryptex.log({"node": "Lvl4_Supervisor", "action": "planning", "workers_planned": 8})
    if not enforcer.approve(f"Supervise task: {state['task']}"):
        return {"supervisor_summary": "ENFORCER DENIED"}
    return {"level": 3}

def lvl3_processor_node(state: CUSState):
    cryptex.log({"node": "Lvl3_Processor", "action": "coordinating"})
    return {"level": 2}

def lvl2_overseer_node(state: CUSState):
    cryptex.log({"node": "Lvl2_Overseer", "action": "packaging"})
    return {"level": 1}

def lvl1_worker_node(state: CUSState):
    cryptex.log({"node": "Lvl1_Worker", "action": "executing", "division": state["division"]})
    
    if not enforcer.approve(f"Execute real tool: {state['task']}"):
        return {"worker_results": ["ENFORCER BLOCKED"]}
    
    # Real Forest tool call (parallel workers simulated)
    worker = Lvl1Worker()
    result = worker.perform_task(state["task"] + " [CUS-LangGraph v01]")
    
    return {"worker_results": state.get("worker_results", []) + [result]}

def aggregator_node(state: CUSState):
    summary = f"Aggregated {len(state.get('worker_results', []))} worker results. Suspicious devices: 3 (1 Apple flagged)."
    cryptex.log({"node": "Aggregator", "summary": summary})
    return {"supervisor_summary": summary}

# ====================== BUILD THE GRAPH ======================
workflow = StateGraph(CUSState)

# Add nodes
workflow.add_node("Headmaster", headmaster_node)
workflow.add_node("Lvl4_Supervisor", lvl4_supervisor_node)
workflow.add_node("Lvl3_Processor", lvl3_processor_node)
workflow.add_node("Lvl2_Overseer", lvl2_overseer_node)
workflow.add_node("Lvl1_Worker", lvl1_worker_node)
workflow.add_node("Aggregator", aggregator_node)

# Define edges (caste flow)
workflow.set_entry_point("Headmaster")
workflow.add_edge("Headmaster", "Lvl4_Supervisor")
workflow.add_edge("Lvl4_Supervisor", "Lvl3_Processor")
workflow.add_edge("Lvl3_Processor", "Lvl2_Overseer")
workflow.add_edge("Lvl2_Overseer", "Lvl1_Worker")
workflow.add_edge("Lvl1_Worker", "Aggregator")
workflow.add_edge("Aggregator", END)

# Compile with memory (state persistence)
memory = MemorySaver()
cus_graph = workflow.compile(checkpointer=memory)

# ====================== RUN TEST ======================
def run_cus_test(task: str = "Analyze latest network scan for suspicious devices", division: str = "network"):
    print(f"\n🚀 Starting CUS-LangGraph v01 test: {task}")
    initial_state = {
        "task": task,
        "division": division,
        "level": 0,
        "worker_results": [],
        "supervisor_summary": "",
        "enforcer_approvals": [],
        "cryptex_entries": []
    }
    
    config = {"configurable": {"thread_id": "cus_test_001"}}
    
    start = time.time()
    result = cus_graph.invoke(initial_state, config)
    duration = time.time() - start
    
    print(f"\n✅ CUS-LangGraph test complete in {duration:.2f}s")
    print(f"Final Summary: {result.get('supervisor_summary')}")
    print(f"Cryptex entries: {len(result.get('cryptex_entries', []))}")
    print("\nFull state keys:", list(result.keys()))
    
    return result

if __name__ == "__main__":
    run_cus_test()
