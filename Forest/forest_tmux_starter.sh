#!/bin/bash
cd ~/Forest
source venv/bin/activate
tmux new-session -d -s forest "python forest_workday_runner.py" 2>/dev/null || tmux new-session -d -s forest "echo 'Forest supervisor started'; python forest_workday_runner.py"
echo "✅ Forest tmux session 'forest' started cleanly"
tmux ls
