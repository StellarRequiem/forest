#!/usr/bin/env python3
"""
Forest Supervisor v2.0 — CUS Brain is now the default
Full hierarchy synced under CUS LangGraph + Enforcer
"""

import subprocess
import sys

print("=== Forest Supervisor v2.0 — Starting Full Synced Hierarchy ===")

def start_cus_ecosystem():
    print("Launching CUS Brain + coordinated organs...")
    
    # Kill any old sessions
    subprocess.run(["tmux", "kill-session", "-t", "forest"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Start the CUS brain as the main session
    subprocess.run(["tmux", "new-session", "-d", "-s", "forest", 
                    "source venv/bin/activate && cd ~/Forest && python forest_cus_launcher.py"])
    
    # Start supporting organs in parallel (they can call into CUS via shared state/cryptex)
    subprocess.run(["tmux", "new-session", "-d", "-s", "mouth", 
                    "source venv/bin/activate && cd ~/Forest && python forest_mouth.py"])
    subprocess.run(["tmux", "new-session", "-d", "-s", "warden", 
                    "source venv/bin/activate && cd ~/Forest && python forest_warden.py"])
    
    print("✅ Full synced Forest ecosystem started")
    print("   Main brain: tmux attach -t forest")
    print("   Mouth:      tmux attach -t mouth")
    print("   Warden:     tmux attach -t warden")
    print("Stop everything: tmux kill-session -t forest && tmux kill-session -t mouth && tmux kill-session -t warden")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--legacy":
        print("Legacy mode requested — old swarm only")
        subprocess.run(["tmux", "new-session", "-d", "-s", "forest", "source venv/bin/activate && cd ~/Forest && python forest_launcher.py"])
    else:
        start_cus_ecosystem()

# === v4.2 META-HARNESS BRIDGE - Added by Graybeard ===
# Tiny safe connection so proposals can reach the Meta-Harness

try:
    from meta_harness_integration import start_trace_for_proposal, log_cus_step, analyze_harness, get_harness_status
    META_HARNESS_AVAILABLE = True
    print("[SUPERVISOR] Meta-Harness integration loaded successfully")
except ImportError as e:
    META_HARNESS_AVAILABLE = False
    print(f"[SUPERVISOR] Warning: Meta-Harness not loaded yet - {e}")

# Helper that Supervisor can call when it sees a meta-harness proposal
def trigger_meta_harness_optimization(target: str = "overall"):
    if not META_HARNESS_AVAILABLE:
        return "Meta-Harness not available. Run setup first."
    
    # Start logging this optimization run
    start_trace_for_proposal(f"meta_harness_optimize:{target}")
    
    # Run the analysis on raw traces
    result = analyze_harness(target)
    
    log_cus_step("Meta-Harness Analysis", f"Target: {target}", result, success=True)
    
    return f"[META-HARNESS] Analysis complete for '{target}'.\n{result}\n\nRaw traces saved in harness_traces/ folder."
