from agent_identity import AgentIdentity
from datetime import datetime

class Headmaster:
    def __init__(self):
        self.identity = AgentIdentity(tier=5, role="headmaster", purpose="executive", sequence=1)
        self.enforcers = []  # Will hold Enforcer references later
        self.active_swarm = {}  # agent_id -> status
        print(f"🚀 Headmaster initialized: {self.identity}")
        print(f"   Credential: {self.identity.get_credential()}")

    def spawn_agent(self, tier: int, role: str, purpose: str, count: int = 1):
        """Headmaster can spawn lower-tier agents"""
        spawned = []
        for i in range(count):
            agent = AgentIdentity(tier=tier, role=role, purpose=purpose, sequence=len(self.active_swarm))
            self.active_swarm[agent.agent_id] = "active"
            spawned.append(agent.agent_id)
        print(f"Headmaster spawned {count} L{tier} {role} agents")
        return spawned

    def report_status(self):
        """Headmaster's executive summary"""
        return {
            "headmaster_id": self.identity.agent_id,
            "spawn_date": self.identity.spawn_date,
            "total_active_agents": len(self.active_swarm),
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    hm = Headmaster()
    hm.spawn_agent(tier=1, role="worker", purpose="audit", count=3)
    print(hm.report_status())
