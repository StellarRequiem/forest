#!/usr/bin/env python3
"""
🌲 Forest Incident Response State Machine v1.0
Coordinates blue-team response through incident phases:
1. DETECT - threat identified by watcher
2. ANALYZE - Ollama analyzes threat, severity assessed
3. RESPOND - firewall blocks, countermeasures activated
4. LOG - incident recorded, context preserved
5. TRAIN - improvement extracted for LLM fine-tuning

Also tracks response effectiveness and learning.
"""
import json
import threading
import time
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List
from enum import Enum
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.blue_agent import BlueAgent
from core.swarm_orchestrator import AgentSwarmOrchestrator, IncidentPhase, IncidentSeverity
from core.dynamic_firewall import DynamicFirewallAgent
from core.claude_analyzer import analyzer as _claude

class ResponseType(Enum):
    BLOCK_IP = "block_ip"
    BLOCK_PORT = "block_port"
    ISOLATE_CONTAINER = "isolate_container"
    ALERT_ADMIN = "alert_admin"
    COLLECT_EVIDENCE = "collect_evidence"
    ENGAGE_AGENT = "engage_agent"

class IncidentResponseEngine(BlueAgent):
    """State machine orchestrating response to incidents"""
    def __init__(self, orchestrator: AgentSwarmOrchestrator, firewall: Optional[DynamicFirewallAgent] = None):
        super().__init__(name="IncidentResponseEngine", model="phi4-mini", role="Incident Coordinator")
        self.orchestrator = orchestrator
        self.firewall = firewall or DynamicFirewallAgent(orchestrator)
        self.credential = orchestrator.register_agent(self.name, self.role)
        self.training_path = Path.home() / "ForestVault" / "training_improvements.jsonl"
    
    def process_incident(self, incident_id: str):
        """Drive incident through state machine"""
        incident = self.orchestrator.get_incident(incident_id)
        if not incident:
            return
        
        phase = IncidentPhase[incident.get("phase", "DETECT")]
        threat_type = incident.get("threat_type")
        severity = IncidentSeverity[incident.get("severity")]
        
        print(f"[IncidentResponseEngine] Processing {incident_id}: {threat_type} ({severity.name})")
        
        # Phase 1: DETECT -> ANALYZE
        if phase == IncidentPhase.DETECT:
            self._analyze_phase(incident_id, incident)
        
        # Phase 2: ANALYZE -> RESPOND
        elif phase == IncidentPhase.ANALYZE:
            self._respond_phase(incident_id, incident)
        
        # Phase 3: RESPOND -> LOG
        elif phase == IncidentPhase.RESPOND:
            self._log_phase(incident_id, incident)
        
        # Phase 4: LOG -> TRAIN
        elif phase == IncidentPhase.LOG:
            self._train_phase(incident_id, incident)
    
    def _analyze_phase(self, incident_id: str, incident: dict):
        """Use Ollama to analyze threat and assign severity"""
        threat_type = incident.get("threat_type")
        details = incident.get("details", {})
        
        prompt = f"""You are a senior blue-team security analyst on macOS.

Threat Type: {threat_type}
Details: {json.dumps(details, indent=2)}

Analyze this threat in 2-3 sentences. Rate severity: INFO (1), WARNING (2), CRITICAL (3), ATTACK (4).
Output format:
ANALYSIS: [your analysis]
SEVERITY: [number]
IMMEDIATE_ACTIONS: [comma-separated list of actions]

Only recommend macOS-compatible actions: block_ip, block_port, isolate_container, alert_admin, collect_evidence"""
        
        try:
            analysis = _claude.analyze_incident(
                threat_type=threat_type,
                details=details,
                severity_hint=IncidentSeverity[incident.get("severity", "WARNING")].value,
            )

            # Parse response
            severity_line = [l for l in analysis.split('\n') if 'SEVERITY:' in l]
            if severity_line:
                try:
                    sev_num = int(severity_line[0].split(':')[1].strip())
                    severity = IncidentSeverity(sev_num)
                    # Update incident with new severity
                    self.orchestrator.incidents[incident_id].severity = severity
                except:
                    pass
            
            self.orchestrator.update_incident_phase(incident_id, IncidentPhase.ANALYZE)
            self.orchestrator.add_response_action(incident_id, f"ANALYZED: {analysis[:200]}")
            self.log_action("INCIDENT_ANALYZED", f"{incident_id}: {analysis[:150]}")
        
        except Exception as e:
            self.log_action("ANALYSIS_FAILED", str(e))
    
    def _respond_phase(self, incident_id: str, incident: dict):
        """Execute active countermeasures"""
        threat_type = incident.get("threat_type")
        details = incident.get("details", {})
        
        # Route to appropriate response handler
        if threat_type == "arp_spoofing":
            self._respond_arp_spoofing(incident_id, incident)
        elif threat_type == "docker_escape" or threat_type == "unexpected_container":
            self._respond_docker_escape(incident_id, incident)
        elif threat_type == "port_scan":
            self._respond_port_scan(incident_id, incident)
        elif threat_type == "docker_arp_activity":
            self._respond_docker_arp(incident_id, incident)
        else:
            self._respond_generic(incident_id, incident)
        
        self.orchestrator.update_incident_phase(incident_id, IncidentPhase.RESPOND)
        self.orchestrator.add_response_action(incident_id, "RESPONDED")
    
    def _respond_arp_spoofing(self, incident_id: str, incident: dict):
        """Block source IP of ARP spoofing attack"""
        details = incident.get("details", {})
        source_ip = details.get("ip")
        
        if source_ip:
            self.firewall.block_ip(source_ip, f"arp_spoofing_incident_{incident_id[:8]}")
            self.orchestrator.block_ip(incident_id, source_ip)
            self.orchestrator.add_response_action(incident_id, f"BLOCKED_IP: {source_ip} (ARP spoofing)")
            self.log_action("ARP_SPOOFING_BLOCKED", source_ip)
    
    def _respond_docker_escape(self, incident_id: str, incident: dict):
        """Kill suspicious container and block its network"""
        details = incident.get("details", {})
        container_id = details.get("container_id")
        
        if container_id:
            try:
                subprocess.run(["docker", "kill", container_id], timeout=5)
                self.orchestrator.add_response_action(incident_id, f"KILLED_CONTAINER: {container_id}")
                self.log_action("ESCAPE_CONTAINER_KILLED", container_id)
            except:
                pass
    
    def _respond_port_scan(self, incident_id: str, incident: dict):
        """Block scanning IP"""
        details = incident.get("details", {})
        source_ip = details.get("source_ip")
        
        if source_ip:
            self.firewall.block_ip(source_ip, f"port_scan_incident_{incident_id[:8]}")
            self.orchestrator.block_ip(incident_id, source_ip)
            self.orchestrator.add_response_action(incident_id, f"BLOCKED_IP: {source_ip} (port scanner)")
            self.log_action("PORT_SCANNER_BLOCKED", source_ip)
    
    def _respond_docker_arp(self, incident_id: str, incident: dict):
        """Sandbox ARP activity - monitor but don't block (controlled red team)"""
        self.orchestrator.add_response_action(incident_id, "MONITORING: Decepticon sandbox activity logged")
        self.log_action("DOCKER_ARP_LOGGED", "Decepticon recon activity recorded")
    
    def _respond_generic(self, incident_id: str, incident: dict):
        """Generic response: log and escalate"""
        self.orchestrator.add_response_action(incident_id, "ESCALATED: Generic threat, requires manual review")
        self.log_action("INCIDENT_ESCALATED", f"{incident_id}")
    
    def _log_phase(self, incident_id: str, incident: dict):
        """Persist incident to training log"""
        incident_data = {
            "id": incident_id,
            "timestamp": datetime.now().isoformat(),
            "threat_type": incident.get("threat_type"),
            "severity": incident.get("severity"),
            "source": incident.get("source"),
            "details": incident.get("details"),
            "actions_taken": incident.get("response_actions"),
            "blocked_ips": incident.get("blocked_ips"),
        }
        
        try:
            with open(self.training_path, 'a') as f:
                f.write(json.dumps(incident_data) + '\n')
            self.orchestrator.update_incident_phase(incident_id, IncidentPhase.LOG)
            self.log_action("INCIDENT_LOGGED", incident_id)
        except Exception as e:
            self.log_action("LOG_FAILED", str(e))
    
    def _train_phase(self, incident_id: str, incident: dict):
        """Extract learnings for LLM training"""
        threat_type = incident.get("threat_type")
        actions = incident.get("response_actions", [])
        
        # Generate improvement suggestion
        improvement_prompt = f"""
Based on this incident response, suggest one concrete improvement for macOS blue-team defense.

Threat: {threat_type}
Actions Taken: {', '.join(actions[:3])}

Output format:
IMPROVEMENT: [specific rule or tool]
TYPE: [pf_rule | detection | isolation | logging]
REASON: [why this helps]
CONFIDENCE: [1-10]
"""
        
        try:
            improvement = _claude.suggest_improvement(
                threat_type=threat_type,
                actions_taken=actions[:5],
            )

            training_entry = {
                "incident_id": incident_id,
                "timestamp": datetime.now().isoformat(),
                "threat_type": threat_type,
                "improvement_suggested": improvement,
                "context": incident
            }
            
            with open(self.training_path, 'a') as f:
                f.write(json.dumps(training_entry) + '\n')
            
            self.log_action("INCIDENT_TRAINING_GENERATED", improvement[:150])
        
        except Exception as e:
            self.log_action("TRAINING_GENERATION_FAILED", str(e))
    
    def watch_and_process(self, interval: int = 10):
        """Continuously pull incidents through state machine"""
        if not self.credential:
            self.credential = self.orchestrator.register_agent(self.name, self.role)
        
        print("[IncidentResponseEngine] Started watching incidents")
        
        while True:
            try:
                self.orchestrator.heartbeat(self.name)
                
                # Get all active incidents
                active = self.orchestrator.get_active_incidents()
                
                for incident in active:
                    incident_id = incident.get("id")
                    phase = incident.get("phase")
                    
                    # Progress to next phase
                    if phase != "train":
                        self.process_incident(incident_id)
                
                time.sleep(interval)
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.log_action("PROCESSOR_ERROR", str(e))
                time.sleep(interval)

def start_incident_response_engine():
    """Launch the incident response state machine"""
    orchestrator = AgentSwarmOrchestrator()
    firewall = DynamicFirewallAgent(orchestrator)
    engine = IncidentResponseEngine(orchestrator, firewall)
    
    thread = threading.Thread(target=engine.watch_and_process, daemon=True)
    thread.start()
    
    print("✅ Incident Response Engine started")
    
    try:
        while True:
            time.sleep(60)
            active = orchestrator.get_active_incidents()
            print(f"[IncidentEngine] Active incidents: {len(active)}")
    except KeyboardInterrupt:
        print("\n🛑 Incident Response Engine shutting down...")

if __name__ == "__main__":
    start_incident_response_engine()
