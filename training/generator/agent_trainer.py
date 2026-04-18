#!/usr/bin/env python3
"""
🌲 Forest Training Pipeline v1.0 — cus-core graded
Replaces flat 1-10 critic with cus-core Grader using forest's 4-factor rubric:
  compliance 45% / usefulness 30% / efficiency 15% / novelty 10%
Improvements are appended to the cus-core AuditChain at training_chain.json.
"""
import os
import json
from datetime import datetime
from pathlib import Path

from cus_core.models import GradeResult, Rubric, Stage, StageName, Task
from cus_core.grader import Grader, MockGrader
from cus_core.audit import AuditChain, AuditEvent

# ---------------------------------------------------------------------------
# Forest rubric — mirrors the 4-factor weights from the original forest design
# ---------------------------------------------------------------------------
_FOREST_RUBRIC = [
    Rubric(name="compliance",  weight=0.45, scoring="binary",  question="Is the suggestion safe, macOS-compatible, and uses pf/pfctl rather than Linux commands?"),
    Rubric(name="usefulness",  weight=0.30, scoring="numeric", question="How concretely actionable is this improvement for a macOS blue-team operator? (0-100)"),
    Rubric(name="efficiency",  weight=0.15, scoring="numeric", question="How low-overhead is this? Does it avoid unnecessary processes or syscalls? (0-100)"),
    Rubric(name="novelty",     weight=0.10, scoring="numeric", question="Does this add something non-redundant that is not already standard practice? (0-100)"),
]

_FOREST_STAGE = Stage(
    name=StageName.EXECUTE,
    grader_model="ollama:phi4-mini",
    rubrics=_FOREST_RUBRIC,
)

_CHAIN_PATH = Path.home() / "ForestVault" / "training_chain.json"
_CHAIN_PATH.parent.mkdir(exist_ok=True)
_audit_chain = AuditChain(_CHAIN_PATH)

TRAINING_LOG = Path.home() / "ForestVault" / "training_improvements.jsonl"


class AgentTrainer:
    def __init__(self, use_mock: bool = False):
        """
        use_mock=True  — deterministic MockGrader (for tests / offline use)
        use_mock=False — OllamaGrader via phi4-mini (default)
        """
        self.training_data: list = []
        self.improvements: list = []

        if use_mock:
            _mock_response = '{"compliance": 100, "usefulness": 80, "efficiency": 75, "novelty": 60}'
            self._grader = Grader(
                backends={"ollama": MockGrader(canned_response=_mock_response)},
                pass_threshold=60.0,
            )
        else:
            from cus_core.grader import OllamaGrader
            self._grader = Grader(
                backends={"ollama": OllamaGrader()},
                pass_threshold=60.0,
            )

    # -----------------------------------------------------------------------
    # Data loading
    # -----------------------------------------------------------------------

    def load_attack_logs(self):
        log_path = Path.home() / "forest-blue-team-guardian" / "blue_agent_logs.json"
        try:
            with open(log_path) as f:
                self.training_data = json.load(f)
            print(f"✅ Loaded {len(self.training_data)} attack logs")
        except Exception as e:
            print(f"❌ Could not load logs: {e}")

    # -----------------------------------------------------------------------
    # Improvement generation (still calls phi4-mini via subprocess for
    # generation — only the *scoring* uses cus-core Grader)
    # -----------------------------------------------------------------------

    def generate_improvement(self, attack_log: dict) -> str:
        import subprocess
        action  = attack_log.get("action", "unknown")
        details = attack_log.get("details", "")

        prompt = f"""You are a senior blue-team engineer on macOS using pf (not iptables).
Attack: {action}
Details: {details}

Suggest ONE concrete, safe, macOS-compatible improvement.
Only use pfctl, arp, dscacheutil, etc. Never suggest Linux commands.

Output EXACT format:
RULE: [short name]
TYPE: arp | pf_firewall | logging | veto
CODE: [exact code snippet]
EXPLANATION: [one short sentence]

Be conservative and safe."""

        try:
            result = subprocess.run(
                ["ollama", "run", "phi4-mini", prompt],
                capture_output=True, text=True, timeout=60,
            )
            return result.stdout.strip()
        except Exception as e:
            return f"[generation error: {e}]"

    # -----------------------------------------------------------------------
    # cus-core grading
    # -----------------------------------------------------------------------

    def grade_improvement(self, improvement: str, attack_log: dict) -> GradeResult:
        """Grade a generated improvement using forest's 4-factor rubric."""
        task = Task(
            id="forest_improvement",
            description=(
                f"Generate a safe, macOS-compatible blue-team improvement for: "
                f"{attack_log.get('action', 'unknown threat')}"
            ),
            stages=[_FOREST_STAGE],
        )
        return self._grader.grade(task=task, response=improvement)

    # -----------------------------------------------------------------------
    # Training loop
    # -----------------------------------------------------------------------

    def train(self, rounds: int = 3):
        print(f"🌲 Forest Training v1.0 (cus-core graded) — {rounds} rounds")

        for i in range(rounds):
            print(f"Round {i+1}/{rounds}")
            for log in self.training_data[:5]:
                improvement = self.generate_improvement(log)
                result      = self.grade_improvement(improvement, log)
                score       = result.composite_score
                passed      = result.passed
                status      = "✅" if passed else "⚠️"

                print(f"  {status} Score {score:.1f}/100: {improvement[:120]}...")

                # Append to JSONL for human review
                entry = {
                    "ts":          datetime.now().isoformat(),
                    "action":      log.get("action"),
                    "improvement": improvement,
                    "score":       round(score, 2),
                    "passed":      passed,
                    "stage_scores": {
                        sr.stage_name: round(sr.weighted_score, 2)
                        for sr in result.stage_results
                    },
                }
                with open(TRAINING_LOG, "a") as f:
                    f.write(json.dumps(entry) + "\n")

                # Append to tamper-evident audit chain
                _audit_chain.append(AuditEvent(
                    event_type="training_improvement",
                    actor="AgentTrainer",
                    payload=entry,
                ))

        print("✅ Training round complete.")


if __name__ == "__main__":
    trainer = AgentTrainer()
    trainer.load_attack_logs()
    trainer.train(rounds=2)
