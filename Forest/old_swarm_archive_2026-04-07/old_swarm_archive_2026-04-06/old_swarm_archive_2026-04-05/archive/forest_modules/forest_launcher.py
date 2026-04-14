import subprocess
import time

print("=== Forest Multi-Box Launcher - Final Fixed Version ===")

organs = {
    "supervisor": "python forest_supervisor_heavy.py",
    "brain": "python forest_brain.py",
    "repl": "python forest_repl.py",
    "mouth": "python forest_mouth.py",
    "scout": "python forest_scout.py",
    "warden": "python forest_warden.py",
    "forge": "python forest_forge.py",
    "hallmonitor": "python forest_hallmonitor.py"
}

for name, cmd in organs.items():
    print(f"Starting {name}...")
    # Kill any existing session first
    subprocess.run(["tmux", "kill-session", "-t", name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(0.5)
    # Start fresh
    subprocess.run(["tmux", "new-session", "-d", "-s", name, f"source ~/Forest/venv/bin/activate && cd ~/Forest && {cmd}"])
    time.sleep(1)

print("\n=== All Forest organs restarted successfully ===")
print("Use these commands:")
print("  fs        = REPL (approve)")
print("  fforge    = Forge")
print("  fwarden   = Warden")
print("  fmouth    = Mouth")
print("  fhall     = Hall Monitor")
print("  fstatus   = List sessions")
print("  fkill     = Kill all")
