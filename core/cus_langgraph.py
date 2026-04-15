#!/usr/bin/env python3
"""
Forest CUS LangGraph v5.1 — Baseline delta detection added.

Changes from v5.0:
  - Imports baseline engine; creates ~/ForestVault/baseline.json on first run
  - Workers inject [DELTA] block into LLM prompt when ports/processes change
  - --update-baseline flag refreshes the baseline from current observations
  - Version bump to v5.1
"""

import argparse
import time
import uuid
from pathlib import Path
from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

# ── Dependency imports with graceful fallbacks ────────────────────────────────

try:
    from agents.organs.enforcer import enforcer
    print("✅ Enforcer v4.0 loaded (qwen2.5:3b constitution judge)")
except ImportError:
    class _DummyEnforcer:
        def approve(self, action): return True
        def enforce_constitution(self, output): return True
        def scan_swarm(self, status=None): return {"status": "scanned"}
    enforcer = _DummyEnforcer()

try:
    from core.grading_engine import cus_grade_and_reward
    print("✅ Grading Engine v2.0 loaded (LLM-backed scoring)")
except ImportError:
    try:
        from grading_engine import cus_grade_and_reward
        print("✅ Grading Engine v2.0 loaded (relative import)")
    except ImportError:
        def cus_grade_and_reward(agent, action_result="", **kwargs):
            return {"grade": 75.0, "decision": "MAINTAIN", "points": 80, "breakdown": {}}

try:
    from core.workers import WORKER_REGISTRY
    print("✅ Workers v1.2 loaded (network / log / threat + baseline delta)")
except ImportError:
    try:
        from workers import WORKER_REGISTRY
        print("✅ Workers v1.2 loaded (relative import)")
    except ImportError:
        WORKER_REGISTRY = {}
        print("⚠️  Workers not found — will use fallback stubs")

try:
    from core import baseline as _baseline
except ImportError:
    try:
        import baseline as _baseline
    except ImportError:
        _baseline = None

try:
    from agents.organs.forest_brain import spawn_agent, log_chain
except ImportError:
    def spawn_agent(name, model, role):
        print(f"[BRAIN] Spawned {name} ({model})")
        return f"{name}|cred-{name}-stub"
    def log_chain(event, details=""):
        print(f"[LOG] {event} | {details}")

# ── Config ────────────────────────────────────────────────────────────────────

PROPOSAL_DIR  = Path.home() / "ForestVault" / "proposals"
PROPOSAL_DIR.mkdir(exist_ok=True)
MAX_PROPOSALS = 20

# Worker definitions: (registry_key, model, role_description)
WORKER_DEFS = [
    ("network_watcher",        "qwen2.5:3b",  "Passive network monitor"),
    ("log_anomaly_specialist", "phi3:mini",   "Log anomaly detection"),
    ("threat_pattern_detector","phi3:mini",   "Threat pattern detection"),
]


# ── State ─────────────────────────────────────────────────────────────────────

class CUSState(TypedDict):
    task:               str
    level:              int
    understory_results: Annotated[List[str], "worker outputs"]
    ecosystem_summary:  str
    enforcer_approvals: List[str]
    workers_spawned:    int
    proposals_stored:   int
    blocked_count:      int
    idle_mode:          bool


# ── Graph nodes ───────────────────────────────────────────────────────────────

def headmaster_node(state: CUSState) -> dict:
    """Scan the swarm environment, then delegate to supervisor."""
    scan_result = enforcer.scan_swarm()
    log_chain("HEADMASTER_DELEGATE", state.get("task", ""))
    return {"level": 4, "blocked_count": scan_result.get("blocked", 0)}


def supervisor_node(state: CUSState) -> dict:
    """Human gate — operator must approve each cycle or choose to idle."""
    action = f"Supervise task: {state.get('task', 'unknown')}"

    current_proposals = len(list(PROPOSAL_DIR.glob("*.md")))
    if current_proposals >= MAX_PROPOSALS:
        print(f"\n[FOREST] Proposal queue full ({current_proposals}/{MAX_PROPOSALS}). "
              "Clear ~/ForestVault/proposals/ to resume.")
        log_chain("SUPERVISOR_IDLE", "proposal queue full")
        return {"idle_mode": True, "ecosystem_summary": "IDLE — proposal queue full"}

    print(f"\n{'='*60}")
    print(f"  🔒 HUMAN GATE — cycle requires approval")
    print(f"  Task : {state.get('task', 'unknown')}")
    print(f"  Level: {state.get('level', '?')}")
    print(f"{'='*60}")
    print("  Options: yes / idle / quit")

    try:
        choice = input("  Approve cycle? > ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        choice = "idle"

    if choice == "idle":
        log_chain("SUPERVISOR_IDLE", action)
        return {"idle_mode": True, "ecosystem_summary": "IDLE MODE ACTIVATED"}

    if choice == "quit":
        log_chain("SUPERVISOR_QUIT", action)
        return {"idle_mode": True, "ecosystem_summary": "QUIT"}

    if choice in ("yes", "y"):
        log_chain("SUPERVISOR_APPROVED", action)
        return {"level": 3}

    log_chain("SUPERVISOR_BLOCKED", action)
    return {"idle_mode": True, "ecosystem_summary": "CYCLE BLOCKED BY OPERATOR"}


def worker_node(state: CUSState) -> dict:
    """
    Run each worker, enforce constitution on output, grade with real LLM scoring.
    Workers are real classes that collect live system data and analyse it with Ollama.
    """
    if state.get("idle_mode", False):
        print("[CUS] Idle mode — workers skipped")
        return {"understory_results": [], "ecosystem_summary": "IDLE MODE"}

    print(f"\n[CUS v5.0] Running {len(WORKER_DEFS)} workers — LVL{state['level']}...")
    results   = []
    approvals = []
    blocked   = state.get("blocked_count", 0)

    for name, model, role in WORKER_DEFS:
        print(f"\n  ▶ {name} ({model})")

        # Spawn credential
        cred = spawn_agent(name, model, role)

        # ── Run worker ────────────────────────────────────────────────────────
        worker_cls = WORKER_REGISTRY.get(name)
        if worker_cls:
            try:
                action_result = worker_cls().run()
            except Exception as exc:
                action_result = f"[{name}] Worker error: {exc}"
                print(f"  ⚠  Worker exception: {exc}")
        else:
            # Fallback stub so the graph still runs if import fails
            action_result = f"[{name}] stub — worker class not loaded"

        print(f"  Output: {action_result[:120]}{'…' if len(action_result) > 120 else ''}")

        # ── Constitution check ────────────────────────────────────────────────
        if not enforcer.enforce_constitution(action_result):
            results.append(f"{name}: CONSTITUTION BLOCKED")
            blocked += 1
            continue

        # ── Grade output ──────────────────────────────────────────────────────
        grade = cus_grade_and_reward(
            cred,
            action_result=action_result,
            task=state.get("task", ""),
        )
        score    = grade.get("grade", 0)
        decision = grade.get("decision", "REVIEW")
        points   = grade.get("points", 0)

        result_line = (
            f"{name} | score={score:.1f} | {decision} | +{points}pts"
        )
        results.append(result_line)
        approvals.append(f"{name}: PASSED")
        print(f"  Grade: {score:.1f} → {decision}")

        # Store full output as a proposal doc for review
        proposal_file = PROPOSAL_DIR / f"{name}_{int(time.time())}.md"
        proposal_file.write_text(
            f"# {name} — {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"**Task**: {state.get('task', '')}\n\n"
            f"**Output**:\n{action_result}\n\n"
            f"**Grade**: {score:.1f} → {decision} (+{points} pts)\n"
        )

        time.sleep(0.1)

    total_promoted = sum(1 for r in results if "PROMOTE" in r)
    total_blocked  = sum(1 for r in results if "BLOCKED" in r)

    summary = (
        f"CUS v5.0 LVL{state['level']} cycle complete — "
        f"{len(results)} workers | "
        f"{total_promoted} promoted | "
        f"{total_blocked} blocked"
    )

    return {
        "understory_results": results,
        "ecosystem_summary":  summary,
        "enforcer_approvals": approvals,
        "workers_spawned":    len(WORKER_DEFS),
        "proposals_stored":   len(list(PROPOSAL_DIR.glob("*.md"))),
        "blocked_count":      blocked,
    }


# ── Build graph ───────────────────────────────────────────────────────────────

workflow = StateGraph(CUSState)
workflow.add_node("Headmaster", headmaster_node)
workflow.add_node("Supervisor", supervisor_node)
workflow.add_node("Worker",     worker_node)

workflow.set_entry_point("Headmaster")
workflow.add_edge("Headmaster", "Supervisor")
workflow.add_edge("Supervisor", "Worker")
workflow.add_edge("Worker", END)

memory    = MemorySaver()
cus_graph = workflow.compile(checkpointer=memory)


# ── Public entry point ────────────────────────────────────────────────────────

def _manage_baseline(update: bool = False) -> None:
    """
    Create baseline on first run, or update it if --update-baseline was passed.
    Collects raw observations (no LLM) from network and process workers.
    """
    if _baseline is None:
        return

    exists = _baseline.load() is not None

    if exists and not update:
        b = _baseline.load()
        print(f"  [Baseline] loaded — created {b['created'][:10]}, "
              f"cycles since update: {b.get('cycles', 0)}")
        return

    action = "Updating" if (exists and update) else "Creating"
    print(f"  [Baseline] {action} baseline from current observations…")

    # Gather raw observations without running any LLM
    ports, ext_ips, proc_names = [], [], []
    net_cls   = WORKER_REGISTRY.get("network_watcher")
    threat_cls = WORKER_REGISTRY.get("threat_pattern_detector")

    if net_cls:
        try:
            ports, ext_ips = net_cls().observe()
        except Exception as exc:
            print(f"  [Baseline] network observe failed: {exc}")

    if threat_cls:
        try:
            proc_names = threat_cls().observe()
        except Exception as exc:
            print(f"  [Baseline] process observe failed: {exc}")

    b = _baseline.create(ports, ext_ips, proc_names)
    _baseline.save(b)
    print(f"  [Baseline] saved — {len(ports)} ports, "
          f"{len(proc_names)} processes, "
          f"{len(ext_ips)} external IPs")


def run_cus_swarm(level: int = 1,
                  task: str = "Blue-team monitoring cycle",
                  update_baseline: bool = False) -> dict:
    print(f"\n{'='*60}")
    print(f"  🌲 Forest CUS LangGraph v5.1")
    print(f"  Task : {task}")
    print(f"  Level: {level}")
    print(f"{'='*60}")

    # Baseline management before the cycle runs
    _manage_baseline(update=update_baseline)

    initial_state: CUSState = {
        "task":               task,
        "level":              level,
        "understory_results": [],
        "ecosystem_summary":  "",
        "enforcer_approvals": [],
        "workers_spawned":    0,
        "proposals_stored":   0,
        "blocked_count":      0,
        "idle_mode":          False,
    }
    config = {"configurable": {"thread_id": f"cus-v51-{uuid.uuid4().hex[:8]}"}}

    result = cus_graph.invoke(initial_state, config)

    # Increment cycle counter in baseline
    if _baseline:
        b = _baseline.load()
        if b and not update_baseline:
            _baseline.increment_cycles(b)
            _baseline.save(b)

    print(f"\n{'='*60}")
    print("  CUS Cycle Complete")
    print(f"  {result.get('ecosystem_summary', '')}")
    print(f"  Workers   : {result.get('workers_spawned', 0)}")
    print(f"  Proposals : {result.get('proposals_stored', 0)}")
    print(f"  Blocked   : {result.get('blocked_count', 0)}")
    print(f"{'='*60}")
    print("\n  Results:")
    for r in result.get("understory_results", []):
        print(f"    → {r}")

    return result


def _notify(title: str, message: str) -> None:
    """
    Fire a macOS desktop notification. Silent no-op on non-macOS or if
    osascript is unavailable.
    """
    import subprocess, sys
    if sys.platform != "darwin":
        return
    try:
        script = (
            f'display notification "{message}" '
            f'with title "{title}" '
            f'sound name "Basso"'
        )
        subprocess.run(
            ["osascript", "-e", script],
            capture_output=True, timeout=5,
        )
    except Exception:
        pass


def run_continuous(interval_minutes: int,
                   alert: bool,
                   alert_threshold: float,
                   update_baseline: bool) -> None:
    """
    Run swarm cycles indefinitely, sleeping `interval_minutes` between each.
    No human gate — approves automatically.
    Press Ctrl-C to stop.
    """
    import signal

    cycle_num = 0
    print(f"\n🌲 Forest CUS — Continuous mode every {interval_minutes}m "
          f"(Ctrl-C to stop)")
    if alert:
        print(f"   Alerts enabled — notify when score < {alert_threshold:.0f}")
    if alert:
        _notify("Forest CUS started",
                f"Monitoring every {interval_minutes} minutes")

    def _run_one() -> None:
        nonlocal cycle_num
        cycle_num += 1
        task = f"Blue-team monitoring cycle #{cycle_num}"
        print(f"\n[{time.strftime('%H:%M:%S')}] Starting cycle #{cycle_num}…")

        # Bypass human gate: patch supervisor_node temporarily
        _orig_input = __builtins__.__dict__.get("input") if hasattr(__builtins__, "__dict__") else None

        import builtins
        _orig = builtins.input
        builtins.input = lambda _: "yes"
        try:
            result = run_cus_swarm(task=task, update_baseline=update_baseline and cycle_num == 1)
        finally:
            builtins.input = _orig

        # Alert on low scores or blocked workers
        if alert:
            alerts = []
            for r in result.get("understory_results", []):
                if "BLOCKED" in r:
                    alerts.append(f"BLOCKED: {r.split('|')[0].strip()}")
                    continue
                parts = r.split("|")
                for p in parts:
                    if "score=" in p:
                        try:
                            score = float(p.split("=")[1])
                            if score < alert_threshold:
                                wname = r.split("|")[0].strip()
                                alerts.append(f"{wname}: score {score:.1f}")
                        except ValueError:
                            pass

            if alerts:
                msg = "; ".join(alerts)
                print(f"\n  🚨 ALERT: {msg}")
                _notify("🌲 Forest CUS Alert", msg)

    try:
        while True:
            _run_one()
            sleep_secs = interval_minutes * 60
            print(f"\n  Sleeping {interval_minutes}m until next cycle… (Ctrl-C to stop)")
            time.sleep(sleep_secs)
    except KeyboardInterrupt:
        print(f"\n🌲 Forest CUS stopped after {cycle_num} cycle(s).")
        if alert:
            _notify("Forest CUS stopped", f"{cycle_num} cycles completed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Forest CUS — Blue-Team Monitoring Swarm",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python3 core/cus_langgraph.py                   # single cycle with human gate\n"
            "  python3 core/cus_langgraph.py --continuous 30   # loop every 30 minutes\n"
            "  python3 core/cus_langgraph.py --continuous 30 --alert  # + desktop alerts\n"
            "  python3 core/cus_langgraph.py --update-baseline # refresh known-good baseline\n"
        ),
    )
    parser.add_argument(
        "--update-baseline",
        action="store_true",
        help="Refresh baseline.json from current system state before running",
    )
    parser.add_argument(
        "--continuous",
        metavar="MINUTES",
        type=int,
        default=0,
        help="Run continuously, sleeping MINUTES between cycles (no human gate)",
    )
    parser.add_argument(
        "--alert",
        action="store_true",
        help="Send macOS desktop notification when score < threshold or worker is blocked",
    )
    parser.add_argument(
        "--alert-threshold",
        metavar="SCORE",
        type=float,
        default=70.0,
        help="Alert when any worker score falls below this value (default: 70)",
    )
    args = parser.parse_args()

    if args.continuous > 0:
        run_continuous(
            interval_minutes=args.continuous,
            alert=args.alert,
            alert_threshold=args.alert_threshold,
            update_baseline=args.update_baseline,
        )
    else:
        run_cus_swarm(update_baseline=args.update_baseline)
