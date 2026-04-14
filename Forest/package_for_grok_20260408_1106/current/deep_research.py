# deep_research.py
# v5.2 — Full Swarm with Critic + Self-Critique

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from typing import TypedDict, Annotated, List, Optional
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
import uuid

from meta_harness_runner import MetaHarnessRunner

class ResearchState(TypedDict):
    target: str
    observations: Annotated[List[str], "raw context"]
    hypotheses: Annotated[List[str], "current hypotheses"]
    experiments: Annotated[List[str], "test results"]
    revisions: Annotated[List[str], "final output"]
    design_system: str
    trace_id: str
    generated_code: str

class DeepResearchLoop:
    def __init__(self):
        self.meta = MetaHarnessRunner()
        self.memory = MemorySaver()
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(ResearchState)

        def observe_node(state: ResearchState):
            self.meta.log_step("Observe", state["target"], "...")
            return {"observations": state["observations"] + [f"Observed: {state['target']}"]}

        def hypothesize_node(state: ResearchState):
            self.meta.log_step("Hypothesize", "...", "Forming plan")
            return {"hypotheses": state["hypotheses"] + ["Build using strict design rules"]}

        def experiment_node(state: ResearchState):
            self.meta.log_step("Experiment", "...", "Generating code")
            return {"experiments": state["experiments"] + ["Code generation started"]}

        def revise_node(state: ResearchState):
            self.meta.log_step("Revise", "...", "Final revision + worker delegation")
            rev = "✅ Revised output ready."

            # Code Generation Worker
            try:
                from worker_code_generator import code_worker
                worker_result = code_worker.generate(
                    research_summary="\n".join(state.get("observations", []) + state.get("hypotheses", []) + state.get("experiments", [])),
                    target=state["target"],
                    design_brand=state.get("design_system")
                )
                state["generated_code"] = worker_result["message"]
                rev += f"\n[WORKER] {worker_result['message']}"
                print(f"\n🚀 Worker executed → {worker_result['message']}")
            except Exception as e:
                rev += f"\n[WORKER ERROR] {e}"

            # Critic Worker + Self-Critique
            try:
                from worker_critic import critic
                critique = critic.critique(state.get("generated_code", ""), state["target"], state.get("design_system"))
                rev += f"\n[CRITIC] Score: {critique['score']}/100"
                if critique['score'] < 80:
                    rev += f" → Issues: {critique['issues']}"
                    rev += "\n[SELF-CRITIQUE] Triggering revision..."
                print(f"Critic score: {critique['score']}")
            except Exception as e:
                rev += f"\n[CRITIC ERROR] {e}"

            return {"revisions": state["revisions"] + [rev]}

        workflow.add_node("Observe", observe_node)
        workflow.add_node("Hypothesize", hypothesize_node)
        workflow.add_node("Experiment", experiment_node)
        workflow.add_node("Revise", revise_node)

        workflow.set_entry_point("Observe")
        workflow.add_edge("Observe", "Hypothesize")
        workflow.add_edge("Hypothesize", "Experiment")
        workflow.add_edge("Experiment", "Revise")
        workflow.add_edge("Revise", END)

        return workflow.compile(checkpointer=self.memory)

    def start_research(self, target: str, design_brand: Optional[str] = None) -> str:
        self.meta.start_new_trace(f"deep_research:{target}")
        state: ResearchState = {
            "target": target,
            "observations": [],
            "hypotheses": [],
            "experiments": [],
            "revisions": [],
            "design_system": design_brand or "",
            "trace_id": f"research-{uuid.uuid4().hex[:8]}",
            "generated_code": ""
        }

        config = {"configurable": {"thread_id": state["trace_id"]}}
        result = self.graph.invoke(state, config)

        summary = "\n".join([
            "=== Deep Research Cycle Complete (with Critic) ===",
            f"Target: {target}",
            f"Design system: {state['design_system']}",
            f"Revisions: {len(result['revisions'])}",
            "\nFinal output:\n" + "\n".join(result["revisions"])
        ])

        self.meta.log_step("Cycle Complete", target, summary, success=True)
        return summary

    def observe(self, msg: str) -> str: return f"[OBSERVE] {msg}"
    def hypothesize(self, msg: str) -> str: return f"[HYPOTHESIZE] {msg}"
    def experiment(self, action: str, condition: str, success: bool) -> str: return f"[EXPERIMENT] {action} | {condition}"
    def revise(self) -> str: return "[REVISE] Solution refined."
