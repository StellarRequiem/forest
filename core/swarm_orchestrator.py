#!/usr/bin/env python3
"""
🌲 Forest Agent Swarm Orchestrator v1.0
Master controller coordinating blue-team agents with shared incident state machine.
- Manages agent lifecycle and credential distribution
- Tracks incident state across all agents
- Coordinates response actions
- Escalates threats based on severity
"""
import json
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import hashlib
import uuid

class IncidentSeverity(Enum):
    INFO = 1
    WARNING = 2
    CRITICAL = 3
    ATTACK = 4

class IncidentPhase(Enum):
    DETECT = "detect"
    ANALYZE = "analyze"
    RESPOND = "respond"
    LOG = "log"
    TRAIN = "train"

@dataclass
class Incident:
    """Unified incident tracking"""
    id: str
    timestamp: datetime
    severity: IncidentSeverity
    source: str  # agent that detected it
    threat_type: str  # arp_spoofing, docker_escape, port_scan, etc.
    details: dict
    phase: IncidentPhase
    active_agents: List[str]
    response_actions: List[str]
    blocked_ips: List[str]
    blocked_ports: List[int]
    ttl: int  # seconds until auto-close
    created_at: datetime
    
    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "severity": self.severity.name,
            "source": self.source,
            "threat_type": self.threat_type,
            "details": self.details,
            "phase": self.phase.value,
            "active_agents": self.active_agents,
            "response_actions": self.response_actions,
            "blocked_ips": self.blocked_ips,
            "blocked_ports": self.blocked_ports,
            "ttl": self.ttl,
            "created_at": self.created_at.isoformat(),
        }

class AgentSwarmOrchestrator:
    def __init__(self, vault_path: Optional[Path] = None):
        self.vault_path = vault_path or (Path.home() / "ForestVault")
        self.vault_path.mkdir(exist_ok=True)
        
        self.incident_log = self.vault_path / "incidents.jsonl"
        self.state_file = self.vault_path / "swarm_state.json"
        self.agents_registry = {}
        self.incidents: Dict[str, Incident] = {}
        self.lock = threading.RLock()
        
        self._load_state()
        self._start_state_cleaner()
        
    def _load_state(self):
        """Load persisted state from disk"""
        if self.state_file.exists():
            try:
                with open(self.state_file) as f:
                    data = json.load(f)
                    self.agents_registry = data.get("agents", {})
            except:
                pass
    
    def _save_state(self):
        """Persist state to disk"""
        with self.lock:
            with open(self.state_file, 'w') as f:
                json.dump({
                    "agents": self.agents_registry,
                    "timestamp": datetime.now().isoformat(),
                    "incident_count": len(self.incidents)
                }, f, indent=2)
    
    def register_agent(self, name: str, role: str, model: str = "phi4-mini") -> str:
        """Register a new blue-team agent and issue credential"""
        with self.lock:
            if name in self.agents_registry:
                return self.agents_registry[name]["credential"]
            
            timestamp = datetime.now().isoformat()
            agent_id = str(uuid.uuid4())[:8]
            credential = hashlib.sha256(f"{name}|{timestamp}".encode()).hexdigest()[:32]
            
            self.agents_registry[name] = {
                "id": agent_id,
                "credential": credential,
                "role": role,
                "model": model,
                "registered_at": timestamp,
                "status": "active",
                "last_heartbeat": timestamp
            }
            self._save_state()
            return credential
    
    def heartbeat(self, agent_name: str) -> bool:
        """Agent heartbeat - confirms agent is alive"""
        with self.lock:
            if agent_name in self.agents_registry:
                self.agents_registry[agent_name]["last_heartbeat"] = datetime.now().isoformat()
                self._save_state()
                return True
        return False
    
    def create_incident(self, source: str, threat_type: str, severity: IncidentSeverity, 
                       details: dict, ttl: int = 3600) -> str:
        """Create and track a new incident"""
        with self.lock:
            incident_id = str(uuid.uuid4())[:16]
            incident = Incident(
                id=incident_id,
                timestamp=datetime.now(),
                severity=severity,
                source=source,
                threat_type=threat_type,
                details=details,
                phase=IncidentPhase.DETECT,
                active_agents=[source],
                response_actions=[],
                blocked_ips=[],
                blocked_ports=[],
                ttl=ttl,
                created_at=datetime.now()
            )
            self.incidents[incident_id] = incident
            self._log_incident(incident)
            return incident_id
    
    def update_incident_phase(self, incident_id: str, phase: IncidentPhase):
        """Move incident through state machine phases"""
        with self.lock:
            if incident_id in self.incidents:
                self.incidents[incident_id].phase = phase
                self._log_incident(self.incidents[incident_id])
    
    def add_response_action(self, incident_id: str, action: str):
        """Record a blue-team response action"""
        with self.lock:
            if incident_id in self.incidents:
                self.incidents[incident_id].response_actions.append(action)
                self._log_incident(self.incidents[incident_id])
    
    def block_ip(self, incident_id: str, ip: str):
        """Add IP to incident's blocked list (triggers firewall rule)"""
        with self.lock:
            if incident_id in self.incidents:
                if ip not in self.incidents[incident_id].blocked_ips:
                    self.incidents[incident_id].blocked_ips.append(ip)
                    self._log_incident(self.incidents[incident_id])
    
    def block_port(self, incident_id: str, port: int):
        """Add port to incident's blocked list"""
        with self.lock:
            if incident_id in self.incidents:
                if port not in self.incidents[incident_id].blocked_ports:
                    self.incidents[incident_id].blocked_ports.append(port)
                    self._log_incident(self.incidents[incident_id])
    
    def engage_agent(self, incident_id: str, agent_name: str):
        """Assign an agent to handle an incident"""
        with self.lock:
            if incident_id in self.incidents:
                if agent_name not in self.incidents[incident_id].active_agents:
                    self.incidents[incident_id].active_agents.append(agent_name)
                    self._log_incident(self.incidents[incident_id])
    
    def close_incident(self, incident_id: str, reason: str = "resolved"):
        """Close and archive an incident"""
        with self.lock:
            if incident_id in self.incidents:
                incident = self.incidents[incident_id]
                incident.phase = IncidentPhase.TRAIN
                self.add_response_action(incident_id, f"CLOSED: {reason}")
                del self.incidents[incident_id]
                self._log_incident(incident)
    
    def get_incident(self, incident_id: str) -> Optional[dict]:
        """Retrieve incident details"""
        with self.lock:
            if incident_id in self.incidents:
                return self.incidents[incident_id].to_dict()
        return None
    
    def get_active_incidents(self) -> List[dict]:
        """List all active incidents"""
        with self.lock:
            return [i.to_dict() for i in self.incidents.values() if i.phase != IncidentPhase.TRAIN]
    
    def get_agent_status(self, agent_name: str) -> Optional[dict]:
        """Check if agent is alive and credentialed"""
        with self.lock:
            return self.agents_registry.get(agent_name)
    
    def _log_incident(self, incident: Incident):
        """Append incident to JSONL log"""
        try:
            with open(self.incident_log, 'a') as f:
                f.write(json.dumps(incident.to_dict()) + '\n')
        except:
            pass
    
    def _start_state_cleaner(self):
        """Daemon thread that closes expired incidents"""
        def cleaner():
            while True:
                time.sleep(60)
                with self.lock:
                    now = datetime.now()
                    expired = [
                        iid for iid, inc in self.incidents.items()
                        if (now - inc.created_at).total_seconds() > inc.ttl
                    ]
                    for iid in expired:
                        self.close_incident(iid, "ttl_expired")
        
        t = threading.Thread(target=cleaner, daemon=True)
        t.start()

if __name__ == "__main__":
    orch = AgentSwarmOrchestrator()
    
    # Register agents
    cred1 = orch.register_agent("ARPMonitorAgent", "Network Recon Defense")
    cred2 = orch.register_agent("FirewallHardenAgent", "Network Defense")
    cred3 = orch.register_agent("DockerGuardAgent", "Container Security")
    
    print(f"✅ Registered 3 agents")
    print(f"ARPMonitor credential: {cred1}")
    
    # Simulate an incident
    incident_id = orch.create_incident(
        source="ARPMonitorAgent",
        threat_type="arp_spoofing",
        severity=IncidentSeverity.CRITICAL,
        details={"suspicious_mac": "aa:bb:cc:dd:ee:ff", "target_ip": "192.168.1.100"}
    )
    print(f"Created incident: {incident_id}")
    
    # Engage FirewallAgent
    orch.engage_agent(incident_id, "FirewallHardenAgent")
    orch.update_incident_phase(incident_id, IncidentPhase.RESPOND)
    orch.block_ip(incident_id, "192.168.1.50")
    orch.add_response_action(incident_id, "Blocked source IP 192.168.1.50")
    
    print(f"Incident details: {orch.get_incident(incident_id)}")
    print(f"Active incidents: {len(orch.get_active_incidents())}")
