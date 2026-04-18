#!/usr/bin/env python3
"""
🌲 Forest Real-Time Threat Watchers v1.0
Background daemon processes monitoring for attacks:
- ARP spoofing detection
- Unexpected Docker container spawns
- Port scan patterns
- Network anomalies
- Rate-limits on suspicious activity
"""
import subprocess
import json
import threading
import time
import re
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
from typing import Dict, Set, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.blue_agent import BlueAgent
from core.swarm_orchestrator import AgentSwarmOrchestrator, IncidentSeverity

ALLOWED_CONTAINERS = [
    "ollama", "forest", "postgres", "redis",
    "open-webui", "dify", "dify-web", "dify-api", "dify-worker",
    "dify-db", "dify-redis", "dify-sandbox", "dify-weaviate", "dify-llm-proxy"
]

class ARPWatcher(BlueAgent):
    """Continuously monitor ARP table for spoofing/recon"""
    def __init__(self, orchestrator: AgentSwarmOrchestrator):
        super().__init__(name="ARPWatcherDaemon", role="ARP Anomaly Detection")
        self.orchestrator = orchestrator
        self.credential = orchestrator.register_agent(self.name, self.role)
        self.arp_history = {}  # Track ARP entries over time
        self.rate_limiter = defaultdict(list)  # IP -> [timestamps]
    
    def run_forever(self, interval: int = 30):
        """Continuously monitor ARP table"""
        if not self.credential:
            self.credential = self.orchestrator.register_agent(self.name, self.role)
        
        print(f"[ARPWatcher] Started monitoring ARP table every {interval}s")
        
        while True:
            try:
                self.orchestrator.heartbeat(self.name)
                self._scan_arp()
                time.sleep(interval)
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.log_action("ARP_WATCHER_ERROR", str(e))
                time.sleep(interval)
    
    def _scan_arp(self):
        """Parse ARP table and detect anomalies"""
        try:
            result = subprocess.check_output(["arp", "-a"], text=True)
            current_entries = {}
            
            for line in result.strip().split('\n'):
                if not line or '?' in line:
                    continue
                
                # Parse: hostname (ip) at mac on iface
                match = re.search(r'\(([0-9.]+)\)\s+at\s+([a-f0-9:]+)', line)
                if match:
                    ip = match.group(1)
                    mac = match.group(2)
                    current_entries[ip] = mac
            
            # Check for anomalies
            for ip, mac in current_entries.items():
                # Track rate of ARP requests from same IP
                self.rate_limiter[ip].append(datetime.now())
                self.rate_limiter[ip] = [
                    t for t in self.rate_limiter[ip] 
                    if (datetime.now() - t).total_seconds() < 60
                ]
                
                # Flag if more than 10 ARP changes in 60s
                if len(self.rate_limiter[ip]) > 10:
                    incident_id = self.orchestrator.create_incident(
                        source=self.name,
                        threat_type="arp_rate_anomaly",
                        severity=IncidentSeverity.WARNING,
                        details={"ip": ip, "rate": len(self.rate_limiter[ip]), "mac": mac},
                        ttl=600
                    )
                    self.log_action("ARP_RATE_ANOMALY", f"IP {ip}: {len(self.rate_limiter[ip])} changes in 60s")
                
                # Check for MAC change (potential spoofing)
                if ip in self.arp_history and self.arp_history[ip] != mac:
                    incident_id = self.orchestrator.create_incident(
                        source=self.name,
                        threat_type="arp_spoofing",
                        severity=IncidentSeverity.CRITICAL,
                        details={
                            "ip": ip,
                            "old_mac": self.arp_history[ip],
                            "new_mac": mac
                        },
                        ttl=3600
                    )
                    self.log_action("ARP_SPOOFING_DETECTED", f"{ip} MAC changed: {self.arp_history[ip]} → {mac}")
                
                # Track Decepticon/sandbox ARP activity
                if '172.17' in ip or '172.18' in ip or 'decepticon' in line.lower():
                    incident_id = self.orchestrator.create_incident(
                        source=self.name,
                        threat_type="docker_arp_activity",
                        severity=IncidentSeverity.WARNING,
                        details={"ip": ip, "mac": mac},
                        ttl=1800
                    )
                    self.log_action("DOCKER_ARP_ACTIVITY", f"Sandbox ARP: {ip} → {mac}")
                
                self.arp_history[ip] = mac
        
        except Exception as e:
            self.log_action("ARP_SCAN_FAILED", str(e))

class DockerWatcher(BlueAgent):
    """Monitor Docker for unexpected containers or escape attempts"""
    def __init__(self, orchestrator: AgentSwarmOrchestrator):
        super().__init__(name="DockerWatcherDaemon", role="Container Escape Detection")
        self.orchestrator = orchestrator
        self.credential = orchestrator.register_agent(self.name, self.role)
        self.seen_containers = set()
    
    def run_forever(self, interval: int = 20):
        """Continuously monitor Docker containers"""
        if not self.credential:
            self.credential = self.orchestrator.register_agent(self.name, self.role)
        
        print(f"[DockerWatcher] Started monitoring Docker every {interval}s")
        
        while True:
            try:
                self.orchestrator.heartbeat(self.name)
                self._scan_docker()
                time.sleep(interval)
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.log_action("DOCKER_WATCHER_ERROR", str(e))
                time.sleep(interval)
    
    def _scan_docker(self):
        """Check for unexpected containers"""
        try:
            result = subprocess.check_output(
                ["docker", "ps", "--format", "{{.Names}}|{{.Status}}|{{.ID}}|{{.Image}}"],
                text=True
            )
            
            for line in result.strip().split('\n'):
                if not line:
                    continue
                
                name, status, cid, image = line.split('|')
                name_lower = name.lower()
                
                # Check if container is allowed
                is_allowed = any(allowed in name_lower for allowed in ALLOWED_CONTAINERS)
                
                if not is_allowed:
                    if name not in self.seen_containers:
                        incident_id = self.orchestrator.create_incident(
                            source=self.name,
                            threat_type="unexpected_container",
                            severity=IncidentSeverity.CRITICAL,
                            details={
                                "container_name": name,
                                "container_id": cid,
                                "image": image,
                                "status": status
                            },
                            ttl=3600
                        )
                        self.log_action("UNEXPECTED_CONTAINER_SPAWNED", f"{name} ({image})")
                        self.seen_containers.add(name)
                
                # Track exited containers
                if 'exited' in status.lower():
                    if name not in self.seen_containers:
                        self.log_action("EXITED_CONTAINER", f"{name} exited: {status}")
        
        except FileNotFoundError:
            pass  # Docker not available
        except Exception as e:
            self.log_action("DOCKER_SCAN_FAILED", str(e))

class NetworkWatcher(BlueAgent):
    """Monitor for port scans and network anomalies"""
    def __init__(self, orchestrator: AgentSwarmOrchestrator):
        super().__init__(name="NetworkWatcherDaemon", role="Port Scan Detection")
        self.orchestrator = orchestrator
        self.credential = orchestrator.register_agent(self.name, self.role)
        self.connection_history = {}
        self.syn_attempts = defaultdict(list)
    
    def run_forever(self, interval: int = 45):
        """Monitor netstat for scanning patterns"""
        if not self.credential:
            self.credential = self.orchestrator.register_agent(self.name, self.role)
        
        print(f"[NetworkWatcher] Started monitoring network every {interval}s")
        
        while True:
            try:
                self.orchestrator.heartbeat(self.name)
                self._scan_netstat()
                time.sleep(interval)
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.log_action("NETWORK_WATCHER_ERROR", str(e))
                time.sleep(interval)
    
    def _scan_netstat(self):
        """Check for suspicious connection patterns"""
        try:
            result = subprocess.check_output(["netstat", "-an"], text=True)
            
            for line in result.strip().split('\n'):
                if 'LISTEN' not in line and 'ESTABLISHED' not in line and 'SYN_RECV' not in line:
                    continue
                
                # Extract remote IP and state
                parts = line.split()
                if len(parts) >= 6:
                    local = parts[3]
                    remote = parts[4]
                    state = parts[5] if len(parts) > 5 else ""
                    
                    # Detect SYN_RECV (possible scan)
                    if state == 'SYN_RECV':
                        remote_ip = remote.split(':')[0] if ':' in remote else remote
                        self.syn_attempts[remote_ip].append(datetime.now())
                        
                        # Clean old entries
                        self.syn_attempts[remote_ip] = [
                            t for t in self.syn_attempts[remote_ip]
                            if (datetime.now() - t).total_seconds() < 10
                        ]
                        
                        # Flag if >5 SYN attempts in 10s
                        if len(self.syn_attempts[remote_ip]) > 5:
                            incident_id = self.orchestrator.create_incident(
                                source=self.name,
                                threat_type="port_scan",
                                severity=IncidentSeverity.WARNING,
                                details={
                                    "source_ip": remote_ip,
                                    "syn_attempts": len(self.syn_attempts[remote_ip])
                                },
                                ttl=600
                            )
                            self.log_action("PORT_SCAN_DETECTED", f"From {remote_ip}: {len(self.syn_attempts[remote_ip])} SYN attempts")
        
        except Exception as e:
            self.log_action("NETSTAT_SCAN_FAILED", str(e))

def start_all_watchers():
    """Launch all three watchers as background threads"""
    orchestrator = AgentSwarmOrchestrator()
    
    arp_watcher = ARPWatcher(orchestrator)
    docker_watcher = DockerWatcher(orchestrator)
    network_watcher = NetworkWatcher(orchestrator)
    
    arp_thread = threading.Thread(target=arp_watcher.run_forever, daemon=True)
    docker_thread = threading.Thread(target=docker_watcher.run_forever, daemon=True)
    network_thread = threading.Thread(target=network_watcher.run_forever, daemon=True)
    
    arp_thread.start()
    docker_thread.start()
    network_thread.start()
    
    print("✅ All watchers started (daemon threads)")
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(60)
            print(f"[Watchers] Heartbeat @ {datetime.now().strftime('%H:%M:%S')}")
    except KeyboardInterrupt:
        print("\n🛑 Watchers shutting down...")

if __name__ == "__main__":
    start_all_watchers()
