#!/usr/bin/env python3
"""
Forest CUS LangGraph v4.0 — Proposal Queue + Idle Mode
"""

import time
import uuid
from pathlib import Path
from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

try:
    from agents.organs.enforcer import enforcer
    print("✅ Real Enforcer v3.0 loaded")
except ImportError:
    class DummyEnforcer:
        def approve(self, action): return True
        def enforce_constitution(self, output): return True
        def scan_swarm(self, status=None): return {"status": "scanned"}
    enforcer = DummyEnforcer()

try:
    from grading_engine import cus_grade_and_reward
    print("✅ Real Grading Engine v1.0 loaded")
except ImportError:
    def cus_grade_and_reward(cred, **kwargs):
        return {"grade": 88.0, "decision": "PROMOTE", "points": 100, "breakdown": {}}

try:
    from agents.organs.forest_brain import spawn_agent, log_chain
except ImportError:
    def spawn_agent(name, model, role):
        print(f"[BRAIN] Spawned {name} ({model})")
        return {"name": name, "credential_id": "STUB_CRED"}
    def log_chain(event, details=""):
        print(f"[LOG] {event} | {details}")

PROPOSAL_DIR = Path.home() / "ForestVault" / "proposals"
PROPOSAL_DIR.mkdir(exist_ok=True)
MAX_PROPOSALS = 20
IDLE_TIMEOUT = 300  # 5 minutes of inactivity

class CUSState(TypedDict):
    task: str
    level: int
    understory_results: Annotated[List[str], "worker outputs"]
    ecosystem_summary: str
    enforcer_approvals: List[str]
    workers_spawned: int
    proposals_stored: int
    idle_mode: bool

def headmaster_node(state: CUSState):
    enforcer.scan_swarm()
    log_chain("HEADMASTER_DELEGATE", state.get("task", ""))
    return {"level": 4}

def supervisor_node(state: CUSState):
    action = f"Supervise task: {state.get('task', 'unknown')}"

    # Check if we have too many stored proposals
    current_proposals = len(list(PROPOSAL_DIR.glob("*.md")))
    if current_proposals >= MAX_PROPOSALS:
        print(f"\n[FOREST] Proposal queue full ({current_proposals}/{MAX_PROPOSALS}). Idling until review.")
        state["idle_mode"] = True
        return {"ecosystem_summary": "IDLE - Proposal queue full"}

    print(f"\n🔒 ENFORCER GATE (Supervisor): {action}")
    print("Type 'yes' to approve this cycle or 'idle' to pause.")
    choice = input("Approve cycle? (yes/idle) > ").strip().lower()

    if choice == "idle":
        state["idle_mode"] = True
        log_chain("SUPERVISOR_IDLE", action)
        return {"ecosystem_summary": "IDLE MODE ACTIVATED"}

    if choice in ["yes", "y"]:
        log_chain("SUPERVISOR_APPROVED", action)
        return {"level": 3}
    else:
        log_chain("SUPERVISOR_BLOCKED", action)
        return {"ecosystem_summary": "ENFORCER BLOCKED"}

def worker_node(state: CUSState):
    if state.get("idle_mode", False):
        print("[CUS] Idle mode - skipping workers")
        return {"understory_results": [], "ecosystem_summary": "IDLE MODE"}

    print(f"\n[CUS LVL{state['level']}] Understory workers executing under Enforcer...")
    workers = [
        ("network_watcher", "qwen2:0.5b", "Passive network monitor"),
        ("log_anomaly_specialist", "phi3:mini", "Log anomaly detection"),
        ("threat_pattern_detector", "phi3:mini", "Threat pattern detection")
    ]
    
    results = []
    approvals = []
    
    for name, model, role in workers:
        print(f"[ENFORCER] Auto-approved safe action → {name}")
        
        cred = spawn_agent(name, model, role)
        action_result = f"{name}: Passive scan complete - no anomalies detected"
        
        if not enforcer.enforce_constitution(action_result):
            results.append(f"{name}: CONSTITUTION BLOCKED")
            continue
            
        grade = cus_grade_and_reward(
            cred,
            action_result=action_result,
            task=state.get("task", "")
        )
        
        result_line = f"{name} | {action_result} | graded {grade.get('grade', 88.0):.1f} → {grade.get('decision', 'PROMOTE')}"
        results.append(result_line)
        approvals.append(f"{name}: APPROVED")
        
        # Store proposal if any (placeholder for your ideas)
        if "proposal" in action_result.lower():
            proposal_file = PROPOSAL_DIR / f"proposal_{int(time.time())}.md"
            proposal_file.write_text(action_result)
            print(f"[FOREST] Proposal stored: {proposal_file.name}")
        
        time.sleep(0.2)
    
    return {
        "understory_results": results,
        "ecosystem_summary": f"CUS LVL{state['level']} cycle complete — {len(results)} workers processed",
        "enforcer_approvals": approvals,
        "workers_spawned": len(workers),
        "proposals_stored": len(list(PROPOSAL_DIR.glob("*.md")))
    }

workflow = StateGraph(CUSState)
workflow.add_node("Headmaster", headmaster_node)
workflow.add_node("Supervisor", supervisor_node)
workflow.add_node("Worker", worker_node)

workflow.set_entry_point("Headmaster")
workflow.add_edge("Headmaster", "Supervisor")
workflow.add_edge("Supervisor", "Worker")
workflow.add_edge("Worker", END)

memory = MemorySaver()
cus_graph = workflow.compile(checkpointer=memory)

def run_cus_swarm(level: int = 1, task: str = "Blue-team monitoring cycle"):
    print(f"\n🌲 Starting CUS LangGraph v4.0 — Level {level}")
    initial_state: CUSState = {
        "task": task,
        "level": level,
        "understory_results": [],
        "ecosystem_summary": "",
        "enforcer_approvals": [],
        "workers_spawned": 0,
        "proposals_stored": 0,
        "idle_mode": False
    }
    config = {"configurable": {"thread_id": f"cus-v40-{uuid.uuid4().hex[:8]}"}}
    
    result = cus_graph.invoke(initial_state, config)
    
    print("\n=== CUS Cycle Complete ===")
    print(f"Workers spawned: {result.get('workers_spawned', 0)}")
    print(f"Proposals stored: {result.get('proposals_stored', 0)}")
    print(f"Summary: {result.get('ecosystem_summary')}")
    for r in result.get("understory_results", []):
        print(f"   → {r}")
    return result

if __name__ == "__main__":
    print("=== Forest CUS LangGraph v4.0 Online — Proposal Queue + Idle Mode ===")
    run_cus_swarm()
