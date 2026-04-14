#!/usr/bin/env python3
"""
Forest Grading Engine v1.0 — Real, Weighted, Transparent Scoring
Base structure inspired by Gemini suggestion. Easy to extend.
"""

from datetime import datetime
import hashlib
from pathlib import Path

VAULT_DIR = Path.home() / "ForestVault"
CRYPTEX_FILE = VAULT_DIR / "training_chain.json"

def log_to_cryptex(event_type: str, details: str = ""):
    timestamp = datetime.now().isoformat()
    entry = f"{timestamp} | {event_type} | {details}"
    h = hashlib.sha256(entry.encode()).hexdigest()[:24]
    with open(CRYPTEX_FILE, "a") as f:
        f.write(f"{entry} | Hash: {h}\n")
    print(f"[GRADING] {event_type} | {details[:100]}...")

class GradingEngine:
    def __init__(self):
        # Default weights — Constitution/Safety is king
        self.weights = {
            "constitution_compliance": 0.45,   # Highest weight
            "usefulness_accuracy":     0.30,
            "efficiency":              0.15,
            "novelty_learning":        0.10
        }

    def grade_worker_output(self, worker_name: str, action_result: str, task: str = "") -> dict:
        """
        Real grading with weighted dimensions.
        Returns score, breakdown, and promotion decision.
        """
        # Simple rule-based scoring for v1.0 (easy to upgrade to LLM later)
        constitution_score = 95 if "no anomalies" in action_result.lower() or "safe" in action_result.lower() else 60
        usefulness_score   = 85 if len(action_result) > 20 else 50
        efficiency_score   = 90   # placeholder — can measure time/resources later
        novelty_score      = 70   # placeholder

        # Calculate weighted final score
        final_score = (
            constitution_score * self.weights["constitution_compliance"] +
            usefulness_score   * self.weights["usefulness_accuracy"] +
            efficiency_score   * self.weights["efficiency"] +
            novelty_score      * self.weights["novelty_learning"]
        )

        # Promotion logic
        if final_score >= 90:
            decision = "PROMOTE"
            points = 200
        elif final_score >= 75:
            decision = "MAINTAIN"
            points = 80
        else:
            decision = "REVIEW / DEMOTE"
            points = 20

        breakdown = {
            "constitution_compliance": round(constitution_score, 1),
            "usefulness_accuracy": round(usefulness_score, 1),
            "efficiency": round(efficiency_score, 1),
            "novelty_learning": round(novelty_score, 1),
            "final_score": round(final_score, 1),
            "decision": decision,
            "points_awarded": points
        }

        log_to_cryptex("GRADING_COMPLETED", 
                      f"{worker_name} | Score: {final_score:.1f} | Decision: {decision}")

        return breakdown

# Global instance
grading_engine = GradingEngine()

def cus_grade_and_reward(agent: dict, blue_team_score=0, accuracy=0, compliance=0, **kwargs):
    """Main grading entry point — called from cus_langgraph"""
    worker_name = agent.get("name", "unknown")
    action_result = kwargs.get("action_result", "No result provided")
    task = kwargs.get("task", "")

    breakdown = grading_engine.grade_worker_output(worker_name, action_result, task)

    return {
        "grade": breakdown["final_score"],
        "decision": breakdown["decision"],
        "points": breakdown["points_awarded"],
        "breakdown": breakdown
    }

# === v4.1 DESIGN SYSTEM GRADING BOOST - Added by Graybeard ===
# Gives extra points when the Worker actually uses the loaded DESIGN.md

def grade_with_design_system(self, proposal: str, action_result: str, design_brand: str = None) -> float:
    """Improved grading that rewards proper design system usage"""
    # Start with your existing base score (whatever you had before)
    base_score = getattr(self, '_basic_score', lambda x: 88.8)(action_result)
    
    consistency_bonus = 0.0
    
    if design_brand:
        brand_lower = design_brand.lower()
        result_lower = action_result.lower()
        
        # Check if the output actually mentions colors, spacing, or components from the design
        design_keywords = ["color", "spacing", "typography", "button", "card", "input", "hex", "#", "rem", "px", "hover", "active"]
        if any(kw in result_lower for kw in design_keywords):
            consistency_bonus = 18.0  # solid bonus for trying to be consistent
        
        # Extra bonus if it specifically mentions the brand
        if brand_lower in result_lower:
            consistency_bonus += 7.0
    
    final_score = min(100.0, base_score + consistency_bonus)
    return round(final_score, 1)

# Add this method to the main grading class if it exists
try:
    if hasattr(GradingEngine, 'grade_action'):
        original_grade = GradingEngine.grade_action
        def new_grade_action(self, proposal, action_result, **kwargs):
            design_brand = kwargs.get('design_brand') or getattr(self, 'active_design_brand', None)
            return grade_with_design_system(self, proposal, action_result, design_brand)
        GradingEngine.grade_action = new_grade_action
except:
    pass  # if the class doesn't exist yet, we'll handle it later
