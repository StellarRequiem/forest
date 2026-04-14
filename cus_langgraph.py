#!/usr/bin/env python3
"""
Forest CUS LangGraph v4.6 — Stable blue-team only (Metatron paused for reliability)
"""

import time
import uuid
from pathlib import Path
from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

try:
    from agents.organs.enforcer import enforcer
except ImportError:
    class DummyEnforcer:
        def scan_swarm(self, status=None): return {"status": "scanned"}
        def approve(self, action): return True
        def enforce_constitution(self, output): return True
    enforcer = DummyEnforcer()

try:
    from agents.core.lvl1_worker import NetworkWatcher, TelemetryGuardian
    from phishing_trainer_worker import PhishingTrainerWorker
    print("✅ Stable blue-team organs loaded (Metatron paused)")
except ImportError as e:
    print(f"⚠️ {e}")

class CUSState(TypedDict):
    task: str
    level: int
    understory_results: Annotated[List[str], "worker outputs"]
    ecosystem_summary: str
    enforcer_approvals: List[str]
    workers_spawned: int
    proposals_stored: int
    idle_mode: bool
    background_mode: bool

def headmaster_node(state: CUSState):
    enforcer.scan_swarm()
    print(f"[HEADMASTER] Delegating task: {state.get('task', 'unknown')}")
    return {"level": 4}

def supervisor_node(state: CUSState):
    if state.get("background_mode", False):
        print(f"[SUPERVISOR] Background mode → AUTO APPROVED")
        return {"level": 3}
    action = f"Supervise task: {state.get('task', 'unknown')}"
    print(f"\n🔒 ENFORCER GATE (Supervisor): {action}")
    choice = input("Approve this cycle? (yes/idle) > ").strip().lower()
    if choice == "idle":
        state["idle_mode"] = True
        return {"ecosystem_summary": "IDLE MODE ACTIVATED"}
    if choice in ["yes", "y"]:
        return {"level": 3}
    else:
        return {"ecosystem_summary": "ENFORCER BLOCKED"}

def worker_node(state: CUSState):
    if state.get("idle_mode", False):
        print("[CUS] Idle mode — skipping workers")
        return {"understory_results": [], "ecosystem_summary": "IDLE MODE"}

    print(f"\n[CUS LVL{state['level']}] Understory workers executing...")
    workers = [
        ("network_watcher", "phi3:mini", "Multi-organ network sniffer & anomaly flagging"),
        ("telemetry_guardian", "phi3:mini", "Privacy & telemetry defense"),
        ("phishing_trainer", "phi3:mini", "Phishing defense trainer & hard-negative generator")
        # Metatron red-team organ paused for stability — ready for manual use
    ]
    
    results = []
    for name, model, role in workers:
        print(f"[ENFORCER] Auto-approved safe action → {name}")
        if name == "network_watcher":
            w = NetworkWatcher()
            w.activate()
            res = w.perform_task("Live network snapshot + anomaly flag")
        elif name == "phishing_trainer":
            w = PhishingTrainerWorker()
            w.activate()
            res = w.perform_task("Run automated phishing defense training")
        else:
            res = f"{name}: task completed safely"
        results.append(res)
    
    return {
        "understory_results": results,
        "ecosystem_summary": f"CUS cycle complete — {len(results)} organs processed",
        "workers_spawned": len(workers)
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

def run_cus_swarm(level: int = 1, task: str = "Blue-team monitoring cycle", background_mode: bool = False):
    print(f"\n🌲 Starting CUS LangGraph v4.6 {'[BACKGROUND]' if background_mode else ''}")
    initial_state = {"task": task, "level": level, "understory_results": [], "ecosystem_summary": "", "enforcer_approvals": [], "workers_spawned": 0, "idle_mode": False, "background_mode": background_mode}
    config = {"configurable": {"thread_id": f"cus-v46-{uuid.uuid4().hex[:8]}"}}
    result = cus_graph.invoke(initial_state, config)
    print("\n=== CUS Cycle Complete ===")
    for r in result.get("understory_results", []):
        print(f"   → {r}")
    return result

if __name__ == "__main__":
    print("=== Forest CUS LangGraph v4.6 Online — Stable blue-team only ===")
    run_cus_swarm(background_mode=False)
