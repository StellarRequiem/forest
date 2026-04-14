import uuid
from datetime import datetime
import hashlib

class AgentIdentity:
    def __init__(self, tier: int, role: str, purpose: str = "general", sequence: int = 0):
        self.spawn_date = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        self.tier = tier
        self.role = role.upper()
        self.purpose = purpose.upper()
        self.sequence = sequence
        self.agent_id = f"F-{self.spawn_date}-L{self.tier}-{self.role}-{self.purpose}-{self.sequence:03d}"
        
        # Simple credential (used for basic inter-agent authentication)
        self.credential = hashlib.sha256(f"{self.agent_id}-FOREST-KEY".encode()).hexdigest()[:16]

    def __str__(self):
        return self.agent_id

    def get_credential(self):
        return self.credential

    def to_dict(self):
        return {
            "agent_id": self.agent_id,
            "spawn_date": self.spawn_date,
            "tier": self.tier,
            "role": self.role,
            "purpose": self.purpose,
            "sequence": self.sequence,
            "credential": self.credential
        }

# Quick test
if __name__ == "__main__":
    id1 = AgentIdentity(tier=1, role="worker", purpose="audit", sequence=42)
    print(id1)
    print("Credential:", id1.get_credential())
