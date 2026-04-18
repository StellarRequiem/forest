#!/usr/bin/env python3
"""
🌲 Forest BlueAgent Base Class v1.2
Credentialed, Ollama-powered, human-gated blue-team agent.
Audit chain backed by cus-core AuditChain (SHA-256 hash chain).
"""
import subprocess
import hashlib
from datetime import datetime
from pathlib import Path

from cus_core.audit import AuditChain, AuditEvent

_CHAIN_PATH = Path.home() / "ForestVault" / "training_chain.json"
_CHAIN_PATH.parent.mkdir(exist_ok=True)
_audit_chain = AuditChain(_CHAIN_PATH)

class BlueAgent:
    def __init__(self, name: str, model: str = "phi4-mini", role: str = "Generic Blue Agent"):
        self.name = name
        self.model = model
        self.role = role
        self.credential = None
        self.log_file = _CHAIN_PATH

    def activate(self):
        """Simple credential activation with signature"""
        timestamp = datetime.now().isoformat()
        signature = hashlib.sha256(f"{self.name}|{timestamp}".encode()).hexdigest()[:16]
        self.credential = f"{self.name}-{signature}"
        print(f"✅ {self.name} activated | Credential: {self.credential}")
        return self.credential

    def analyze_with_ollama(self, data: str, prompt_template: str) -> str:
        """Send data to local Ollama for smart analysis"""
        if not self.credential:
            return "Agent not activated"

        full_prompt = f"{prompt_template}\n\nData:\n{data}\n\nReply with short, actionable blue-team analysis only."
        
        try:
            result = subprocess.run(
                ["ollama", "run", self.model, full_prompt],
                capture_output=True, text=True, timeout=30
            )
            return result.stdout.strip() or "No analysis returned"
        except Exception as e:
            return f"Ollama analysis failed: {e}"

    def log_action(self, action: str, result: str):
        """Append a tamper-evident entry to the cus-core AuditChain."""
        payload = {
            "agent": self.name,
            "action": action,
            "result": result[:500],
            "ts": datetime.now().isoformat(),
        }
        _audit_chain.append(AuditEvent(event_type=action, actor=self.name, payload=payload))
        print(f"[LOG] {self.name} | {action} | {result[:200]}")

if __name__ == "__main__":
    print("BlueAgent base class loaded. Ready for inheritance.")
