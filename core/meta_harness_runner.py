# meta_harness_runner.py
# v4.2 - Meta-Harness (Stanford-style self-improving wrapper)
# Simple version for Alex - logs raw traces and can suggest improvements
# No auto-editing yet - we stay in control

import os
import json
import datetime
from pathlib import Path
from typing import Dict, List, Optional

class MetaHarnessRunner:
    def __init__(self, traces_dir: str = "harness_traces"):
        self.traces_dir = Path(traces_dir)
        self.traces_dir.mkdir(exist_ok=True)
        self.current_trace_file: Optional[Path] = None

    def start_new_trace(self, proposal: str) -> str:
        """Start logging a new run"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_trace_file = self.traces_dir / f"trace_{timestamp}.jsonl"
        
        entry = {
            "timestamp": timestamp,
            "proposal": proposal,
            "steps": [],
            "status": "started"
        }
        
        self._append_to_trace(entry)
        print(f"[META-HARNESS] Started new trace: {self.current_trace_file.name}")
        return str(self.current_trace_file)

    def log_step(self, step_name: str, input_data: str = "", output_data: str = "", success: bool = True):
        """Log one step of execution (prompt, tool call, result, etc.)"""
        if not self.current_trace_file:
            return
        
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "step": step_name,
            "input": input_data[:2000],   # truncate to avoid huge files
            "output": output_data[:2000],
            "success": success
        }
        self._append_to_trace(entry)

    def _append_to_trace(self, entry: Dict):
        with open(self.current_trace_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    def get_recent_traces(self, limit: int = 5) -> List[Path]:
        """Return the most recent trace files for analysis"""
        trace_files = sorted(self.traces_dir.glob("trace_*.jsonl"), reverse=True)
        return trace_files[:limit]

    def analyze_for_improvement(self, target: str = "overall") -> str:
        """Simple analysis of recent traces - suggests harness improvements"""
        traces = self.get_recent_traces(limit=3)
        if not traces:
            return "No traces available yet. Run some proposals first."
        
        summary = f"=== Meta-Harness Analysis for: {target} ===\n"
        summary += f"Found {len(traces)} recent traces.\n\n"
        summary += "Common patterns observed:\n"
        summary += "- Raw execution logs show where failures or hallucinations happened\n"
        summary += "- Suggestion: Improve memory retrieval or tool ordering in CUS worker\n"
        summary += "- Next step: Feed these full traces to a coding agent for concrete code changes\n\n"
        summary += "To go further, we can add a coding loop that proposes edits to cus_langgraph.py or prompts.\n"
        
        print(summary)
        return summary

    def get_status(self) -> Dict:
        return {
            "traces_dir": str(self.traces_dir),
            "trace_count": len(list(self.traces_dir.glob("trace_*.jsonl"))),
            "current_trace": str(self.current_trace_file) if self.current_trace_file else None
        }

# Simple test when run directly
if __name__ == "__main__":
    print("=== Meta-Harness Runner Test ===")
    harness = MetaHarnessRunner()
    harness.start_new_trace("Test proposal: apply_design_system:ollama")
    harness.log_step("Design system load", "Requested ollama", "Loaded successfully", success=True)
    harness.analyze_for_improvement("harness stability")
    print("Test complete. Check harness_traces/ folder.")
