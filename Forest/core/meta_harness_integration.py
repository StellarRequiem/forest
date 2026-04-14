# meta_harness_integration.py
# v4.2 - Simple bridge between CUS/Supervisor and MetaHarnessRunner
# Keeps things safe and easy to understand

from meta_harness_runner import MetaHarnessRunner

# Global instance so the whole Forest can use it
meta_harness = MetaHarnessRunner()

def start_trace_for_proposal(proposal: str):
    """Called when a new proposal starts — begins raw logging"""
    trace_path = meta_harness.start_new_trace(proposal)
    print(f"[META-HARNESS] Raw trace started for: {proposal}")
    return trace_path

def log_cus_step(step_name: str, input_data: str = "", output_data: str = "", success: bool = True):
    """Log what happened during a CUS step (prompt, tool, result, etc.)"""
    meta_harness.log_step(step_name, input_data, output_data, success)

def analyze_harness(target: str = "overall"):
    """Run analysis on recent raw traces and get improvement suggestions"""
    print(f"[META-HARNESS] Analyzing traces for target: {target}")
    result = meta_harness.analyze_for_improvement(target)
    return result

def get_harness_status():
    """Show how many traces we have"""
    return meta_harness.get_status()

# Quick test when run directly
if __name__ == "__main__":
    print("=== Meta-Harness Integration Test ===")
    start_trace_for_proposal("Test meta harness integration")
    log_cus_step("Test step", "Some input", "Good output", success=True)
    analyze_harness("memory")
    print("Integration test complete.")
