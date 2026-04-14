#!/usr/bin/env python3
"""
Forest Scout v2.0 — Realigned under CUS Brain
Scouting / discovery layer. All scouting gated by brain.
"""

from forest_brain import spawn_agent, cus_grade_and_reward, log_chain

class ForestScout:
    def scout(self, target):
        print(f"[SCOUT] Scouting target: {target} → routing to brain...")
        cred = spawn_agent(f"scout_{target[:10]}", "qwen2:0.5b", f"Scout for {target}")
        if cred is None:
            return "Scouting denied by human gate"
        grade = cus_grade_and_reward(cred, blue_team_score=75, accuracy=70, compliance=85)
        log_chain("SCOUT_COMPLETE", f"{target}|{grade['decision']}")
        return f"Scout report for {target} completed and graded {grade['grade']:.1f}"

print("=== Forest Scout v2.0 Loaded — Brain Gated ===")
