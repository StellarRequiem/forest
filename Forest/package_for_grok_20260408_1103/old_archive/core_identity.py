from agent_identity import AgentIdentity
from datetime import datetime

# Global registry so all organs can share identities
AGENT_REGISTRY = {}

def register_agent(tier: int, role: str, purpose: str = "general", count: int = 1):
    """Register or get an agent's identity"""
    key = f"{role}-{purpose}"
    if key not in AGENT_REGISTRY:
        AGENT_REGISTRY[key] = []
    
    agents = []
    for i in range(count):
        agent = AgentIdentity(tier=tier, role=role, purpose=purpose, sequence=len(AGENT_REGISTRY[key]))
        AGENT_REGISTRY[key].append(agent)
        agents.append(agent)
    
    return agents[0] if count == 1 else agents

def get_agent_identity(role: str, purpose: str = "general"):
    key = f"{role}-{purpose}"
    if key in AGENT_REGISTRY and AGENT_REGISTRY[key]:
        return AGENT_REGISTRY[key][0]
    return None

# Example registration for existing organs
if __name__ == "__main__":
    # Register some core agents
    headmaster = register_agent(tier=5, role="headmaster", purpose="executive")
    supervisor = register_agent(tier=4, role="supervisor", purpose="coordinator")
    warden = register_agent(tier=3, role="warden", purpose="security")
    mouth = register_agent(tier=2, role="mouth", purpose="communication")
    
    print("Registered agents:")
    for agents in AGENT_REGISTRY.values():
        for a in agents:
            print(f"  {a}")
