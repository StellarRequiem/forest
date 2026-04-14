from datetime import datetime

class AgentIdentity:
    def __init__(self, tier=1, role="worker", purpose="general"):
        self.tier = tier
        self.role = role
        self.purpose = purpose
        self.spawn_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        self.id = f"F-{self.spawn_time}-L{tier}-{role.upper()}-000"

    def __str__(self):
        return self.id
