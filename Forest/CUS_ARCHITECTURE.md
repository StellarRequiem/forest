# CUS_ARCHITECTURE.md — Single Source of Truth (Session Protocol v1.0)
Date: April 08 2026
Author: Graybeard (for Alex / StellarRequiem)
Version: Final Integrated v4.1

THE FOREST — Living Organism (Phase 0 + CUS fully merged)

BASE LAYER (Photosynthesis)
- forest_network_watcher.py + forest_network_reporter.py
  → Original multi-organ network sniffer (ARP scans, device classification, anomaly flagging)
  → Now exposed as native NetworkWatcher Lvl1Worker

CUS HIERARCHY (Caste Unity System)
- Headmaster → Supervisor → Lvl1 Workers (NetworkWatcher + TelemetryGuardian + log_anomaly_specialist)
- Enforcer v3.0 on every node (scan_swarm, human gate, constitution enforcement, tmux/process killing)
- Cryptex tamper-evident chained logging (SHA-256 hashes in ~/ForestVault/training_chain.json)

CORE INTEGRATED FILES (live right now)
- cus_langgraph.py v4.1 → LangGraph orchestration with native NetworkWatcher
- lvl1_worker.py v2.2 → Base + TelemetryGuardian + NetworkWatcher subclass
- enforcer.py v3.0 → Ruthless gatekeeper (full scan_swarm restored)
- forest_brain.py v2.0 → Credentialing, grading, reward ledger
- forest_auto_runner.py v1.0 → 24/7 background cycles (new)
- full_test_runner.py v1.1 → Measurable end-to-end testing
- forest_launcher.py + forest_supervisor.py → Persistent tmux sessions

SAFETY & LOGGING
- Every action gated by Enforcer + human veto (Supervisor)
- Every snapshot/activation logged with unique Cryptex hash
- DCP (Drift Contingency Protocol) still active

CURRENT STATE
The original Phase 0 multi-organ network sniffer is now a first-class native Lvl1 organ that runs automatically on every CUS cycle, feeds live telemetry into the brain, and is fully protected by Enforcer + Cryptex. The Forest is one complete, refusal-first, human-gated living organism.
