# Forest Master Project Bible
**Date:** April 03, 2026  
**Author:** Graybeard (30+ years IT/cyber/full-stack)  
**Owner:** Alex (StellarRequiem)  
**Hardware:** Mac Mini M4, 16GB RAM, local-only

## Current Real State (Verified April 03, 2026)

**Working Core**
- `forest_orchestrator.py` v1.9.6 – main CLI with privacy mode, ramp-down, psutil throttling, Seasons
- `telemetry_guardian.py` – real macOS process scanning (CloudTelemetryService, etc.)
- `quarantine_swarm/` – fully functional:
  - `scout.py` – safe public fetch
  - `warden.py` – `isolate_and_run()`
  - `dissector.py` – `dissect()` with danger pattern matching
  - `rebuilder.py` – `rebuild()` decision logic
- Resource controls (`--rampdown`, RAM warning, CPU nice priority)
- Cryptex logging
- Basic human-gated rebuild with scoring

**Directory Status**
- Cleaned: Legacy files moved to `archive/`
- Active: orchestrator, quarantine_swarm/, telemetry_guardian, cus_langgraph, cryptex, enforcer

**What Still Needs Work**
- Rebuilder currently returns status only — does not yet write full new .py tool files
- Full CUS hierarchy not wired into orchestrator
- No Hall Monitor / automatic cleanup
- No dynamic worker scaling beyond ramp-down

## Consolidated Development Roadmap (Realistic)

**Phase 0 – Foundation** (Completed)
- Stable orchestrator with ramp-down and resource controls
- Working Quarantine Swarm using real module methods

**Phase 1 – Adaptive Growth** (Next)
- Deepen Rebuilder to write full new `.py` class files to `generated/`
- Add basic performance scoring for future CUS tiers
- Clean duplicate init spam

**Phase 2 – Swarm Reliability** (1 week)
- Add Hall Monitor cleanup
- Improve Dissector patterns
- Dynamic worker count based on real RAM/CPU

**Phase 3 – CUS Activation** (2–3 weeks)
- Wire `cus_langgraph.py` as active routing layer
- Implement simple tiered identifiers and promotion logic

**Phase 4 – Hardware Scaling**
- Add second M4 Pro Mini (24GB) when ready
- Simple Tailscale setup

**Phase 5 – Public Path**
- GitHub repo + demo video showing Rebuilder creating real files
- Grant applications (AI Grant, NLnet, etc.)

## Safety Principles (Non-Negotiable)
- Human veto on every rebuild
- Ramp-down for memory safety
- Cryptex immutable log
- Refusal-first on dangerous patterns

This MASTER_NOTES.md will be updated as we ship new phases.

Last updated: April 03, 2026
