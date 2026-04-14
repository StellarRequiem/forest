# CUS_ARCHITECTURE.md — Single Source of Truth (Session Protocol v1.0)
Date: April 09 2026
Author: Graybeard (for Alex / StellarRequiem)
Version: v4.6 Stable Blue-Team

THE FOREST — Living Organism (stable, running at 100+ cycles)

BASE LAYER
- Original multi-organ network sniffer (forest_network_watcher.py) as native Lvl1Worker

ACTIVE ORGANS (running every 5 minutes)
- NetworkWatcher (live ARP snapshots)
- TelemetryGuardian
- PhishingTrainerWorker v2.2 (dynamic emails, real LLM decisions, varying accuracy/hard negatives)

PAUSED ORGANS
- MetatronWorker (contained red-team black box in danger_room/sandbox — ready when needed)

CORE FILES (current stable versions)
- cus_langgraph.py v4.6 (stable blue-team only)
- forest_auto_runner.py v1.3 (5-minute cycle + configurable Metatron timer)
- forest_dashboard.py v2.0 (live Rich dashboard)
- lvl1_worker.py v2.2
- phishing_trainer_worker.py v2.2 (dynamic)
- forest_brain.py v2.2 (varied grading)
- enforcer.py v3.0

SAFETY LAYERS
- Enforcer v3.0 on every action
- Cryptex tamper-evident logging
- All red-team tools confined to danger_room/sandbox

CURRENT STATE
Stable, refusal-first, local-only blue-team organism running 24/7. Generates real training data with variation. Ready for next steps (simulation data, launchd, etc.).
