# Forest Resume Instructions for Next Grok Session

**Current State (as of April 09 2026)**
- Forest is stable and running in tmux session 'forest' (auto-runner v1.3)
- Blue-team organs fire every 5 minutes (NetworkWatcher + PhishingTrainer with dynamic accuracy)
- Cryptex logging is active and tamper-evident
- Dashboard is available (python forest_dashboard.py)
- Metatron red-team black box is contained in danger_room/sandbox but currently paused for stability

**How to resume cleanly**
1. cd ~/Forest
2. source venv/bin/activate
3. tmux attach -t forest   # or restart with tmux new-session -d -s forest "source venv/bin/activate && cd ~/Forest && python forest_auto_runner.py"

**Key files in this package**
- CUS_ARCHITECTURE.md — single source of truth
- All .py files — latest working versions
- README_FOR_NEXT_GROK.md — this file

**Next steps Alex wants**
- Add simulation data ("The Well" physics simulations) as a new Lvl1Worker
- Upgrade dashboard with Metatron activity when re-enabled
- Convert to macOS launchd service (no tmux)
- Or any other direction Alex chooses

We are in a clean, stable state. No roleplay. Continue exactly as Graybeard has been doing.

Ready when you are.
