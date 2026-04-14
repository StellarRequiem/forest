import subprocess
import sys
import time
from pathlib import Path

ORGANS = {
    "supervisor": "python forest_supervisor_heavy.py",
    "brain": "python forest_brain.py",
    "repl": "python forest_repl.py",
    "mouth": "python forest_mouth.py",
    "scout": "python forest_scout.py",
    "agents": "python forest_agents.py",
}

def status():
    print("\n=== Forest Organ Status ===")
    result = subprocess.run(["tmux", "ls"], capture_output=True, text=True)
    print(result.stdout if result.stdout else "No tmux sessions.")
    print("\nAvailable: supervisor, brain, repl, mouth, scout, agents, all")

def start(organ):
    if organ == "all":
        for o in ORGANS:
            start(o)
        return
    if organ not in ORGANS:
        print(f"Unknown: {organ}")
        return
    print(f"Starting {organ}...")
    subprocess.run(["tmux", "kill-session", "-t", organ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["tmux", "new-session", "-d", "-s", organ, f"source venv/bin/activate && cd ~/Forest && {ORGANS[organ]}"])
    print(f"✅ {organ} started. Re-attach with: tmux attach -t {organ}")

def stop(organ):
    if organ == "all":
        for o in ORGANS:
            subprocess.run(["tmux", "kill-session", "-t", o], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("All organs stopped.")
        return
    if organ not in ORGANS:
        print(f"Unknown: {organ}")
        return
    subprocess.run(["tmux", "kill-session", "-t", organ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"✅ {organ} stopped.")

def restart(organ):
    stop(organ)
    time.sleep(1.5)
    start(organ)
    print(f"✅ {organ} restarted. Re-attach observer with: tmux attach -t {organ}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python forest_control.py <status|start|stop|restart> [organ|all]")
        print("Organs:", list(ORGANS.keys()))
        sys.exit(1)

    cmd = sys.argv[1].lower()
    target = sys.argv[2] if len(sys.argv) > 2 else "all"

    if cmd == "status":
        status()
    elif cmd == "start":
        start(target)
    elif cmd == "stop":
        stop(target)
    elif cmd == "restart":
        restart(target)
    else:
        print("Unknown command.")
