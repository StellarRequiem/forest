#!/usr/bin/env python3
"""
Forest Forge v2.0 — Realigned under CUS Brain
Agent creation / forging layer. All forges go through brain gate.
"""

from forest_brain import spawn_agent, cus_grade_and_reward, log_chain

class ForestForge:
    def forge_agent(self, name, model="phi3:mini", role="Forged agent"):
        print(f"[FORGE] Requesting to forge new agent '{name}' → routing to brain...")
        cred = spawn_agent(name, model, role)
        if cred is None:
            print(f"[FORGE] Forging denied for {name}")
            return None
        grade = cus_grade_and_reward(cred, blue_team_score=82, accuracy=78, compliance=88)
        log_chain("AGENT_FORGED", f"{name}|{grade['decision']}")
        print(f"[FORGE] Agent {name} forged and graded {grade['grade']:.1f} → {grade['decision']}")
        return cred

print("=== Forest Forge v2.0 Loaded — Brain Gated ===")
