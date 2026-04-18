#!/usr/bin/env python3
"""
🌲 Forest Dynamic Firewall Response v1.0
Automatically block/unblock IPs and ports in response to detected incidents.
Uses macOS pf (packet filter) for runtime rules.
Integrates with incident state machine for coordinated response.
"""
import subprocess
import json
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Set, List, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.blue_agent import BlueAgent
from core.swarm_orchestrator import AgentSwarmOrchestrator, IncidentSeverity

class DynamicFirewallAgent(BlueAgent):
    """Dynamically manage pf rules based on incidents"""
    def __init__(self, orchestrator: AgentSwarmOrchestrator):
        super().__init__(name="DynamicFirewallAgent", model="phi4-mini", role="Dynamic Firewall Control")
        self.orchestrator = orchestrator
        self.credential = orchestrator.register_agent(self.name, self.role)
        self.blocked_ips: Set[str] = set()
        self.blocked_ports: Set[int] = set()
        self.rule_file = Path("/tmp/forest_dynamic_rules.conf")
        self.anchor_name = "forest/dynamic"
        self._load_existing_rules()
    
    def _load_existing_rules(self):
        """Load any persisted rules from disk"""
        try:
            if self.rule_file.exists():
                with open(self.rule_file) as f:
                    content = f.read()
                    # Extract IPs from comments
                    for line in content.split('\n'):
                        if 'block drop in' in line and 'from' in line:
                            parts = line.split()
                            if 'from' in parts:
                                idx = parts.index('from')
                                if idx + 1 < len(parts):
                                    ip = parts[idx + 1]
                                    if '.' in ip:  # Basic IP validation
                                        self.blocked_ips.add(ip)
        except:
            pass
    
    def block_ip(self, ip: str, reason: str = "threat_detected", permanent: bool = False):
        """Add IP to block list"""
        if ip not in self.blocked_ips:
            self.blocked_ips.add(ip)
            self._apply_rules()
            ttl = 3600 if not permanent else 86400
            self.log_action("IP_BLOCKED", f"{ip} - {reason}")
            return True
        return False
    
    def unblock_ip(self, ip: str):
        """Remove IP from block list"""
        if ip in self.blocked_ips:
            self.blocked_ips.discard(ip)
            self._apply_rules()
            self.log_action("IP_UNBLOCKED", f"{ip}")
            return True
        return False
    
    def block_port(self, port: int, reason: str = "threat_detected"):
        """Block inbound traffic on port"""
        if port not in self.blocked_ports:
            self.blocked_ports.add(port)
            self._apply_rules()
            self.log_action("PORT_BLOCKED", f"{port} - {reason}")
            return True
        return False
    
    def unblock_port(self, port: int):
        """Unblock port"""
        if port in self.blocked_ports:
            self.blocked_ports.discard(port)
            self._apply_rules()
            self.log_action("PORT_UNBLOCKED", f"{port}")
            return True
        return False
    
    def _generate_ruleset(self) -> str:
        """Generate pf ruleset for current blocked IPs/ports"""
        rules = """# Forest Dynamic Firewall Rules
# Auto-generated @ {timestamp}
# IPs: {ip_count} | Ports: {port_count}

# Block spoofed/sandboxed Docker ranges
block drop out quick on en1 inet from 172.17.0.0/16 to any
block drop out quick on en1 inet from 172.18.0.0/16 to any

""".format(
            timestamp=datetime.now().isoformat(),
            ip_count=len(self.blocked_ips),
            port_count=len(self.blocked_ports)
        )
        
        # Add dynamic IP blocks
        for ip in sorted(self.blocked_ips):
            rules += f"# Blocked: {ip}\n"
            rules += f"block drop in quick from {ip}\n"
            rules += f"block drop out quick to {ip}\n"
        
        rules += "\n"
        
        # Add dynamic port blocks
        for port in sorted(self.blocked_ports):
            rules += f"# Block port {port}\n"
            rules += f"block drop in quick on * inet proto tcp to any port {port}\n"
            rules += f"block drop in quick on * inet proto udp to any port {port}\n"
        
        rules += "\npass out all flags S/SA keep state\n"
        
        return rules
    
    def _apply_rules(self):
        """Write and load rules into pf (macOS)"""
        try:
            ruleset = self._generate_ruleset()
            
            # Write to temp file
            with open(self.rule_file, 'w') as f:
                f.write(ruleset)
            
            # Load into pf
            # Note: This requires sudo; in real deployment, use passwordless sudo for pfctl
            try:
                result = subprocess.run(
                    ["sudo", "pfctl", "-a", self.anchor_name, "-f", str(self.rule_file)],
                    capture_output=True, text=True, timeout=10
                )
                if result.returncode != 0:
                    self.log_action("FIREWALL_LOAD_FAILED", result.stderr[:200])
                else:
                    self.log_action("FIREWALL_RULES_APPLIED", f"IPs: {len(self.blocked_ips)}, Ports: {len(self.blocked_ports)}")
            except subprocess.TimeoutExpired:
                self.log_action("FIREWALL_TIMEOUT", "pfctl did not respond")
        except Exception as e:
            self.log_action("FIREWALL_ERROR", str(e))
    
    def watch_incidents(self, interval: int = 15):
        """Continuously sync firewall rules with incident state"""
        if not self.credential:
            self.credential = self.orchestrator.register_agent(self.name, self.role)
        
        print(f"[DynamicFirewall] Started monitoring incidents every {interval}s")
        
        while True:
            try:
                self.orchestrator.heartbeat(self.name)
                
                # Get all active incidents
                active = self.orchestrator.get_active_incidents()
                
                for incident in active:
                    # Block all IPs from incident
                    for ip in incident.get("blocked_ips", []):
                        self.block_ip(ip, f"incident_{incident['id'][:8]}")
                    
                    # Block all ports from incident
                    for port in incident.get("blocked_ports", []):
                        self.block_port(port, f"incident_{incident['id'][:8]}")
                
                # Cleanup: unblock IPs that aren't in any active incident
                all_incident_ips = set()
                for incident in active:
                    all_incident_ips.update(incident.get("blocked_ips", []))
                
                for ip in list(self.blocked_ips):
                    if ip not in all_incident_ips and '172.17' not in ip and '172.18' not in ip:
                        self.unblock_ip(ip)
                
                time.sleep(interval)
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.log_action("INCIDENT_SYNC_ERROR", str(e))
                time.sleep(interval)
    
    def get_status(self) -> dict:
        """Return current firewall state"""
        return {
            "timestamp": datetime.now().isoformat(),
            "blocked_ips": sorted(self.blocked_ips),
            "blocked_ports": sorted(self.blocked_ports),
            "rule_file": str(self.rule_file),
            "anchor": self.anchor_name
        }

def start_dynamic_firewall():
    """Launch the dynamic firewall agent"""
    orchestrator = AgentSwarmOrchestrator()
    firewall = DynamicFirewallAgent(orchestrator)
    
    thread = threading.Thread(target=firewall.watch_incidents, daemon=True)
    thread.start()
    
    print("✅ Dynamic Firewall Agent started")
    
    try:
        while True:
            time.sleep(60)
            status = firewall.get_status()
            print(f"[Firewall] {len(status['blocked_ips'])} IPs blocked, {len(status['blocked_ports'])} ports blocked")
    except KeyboardInterrupt:
        print("\n🛑 Dynamic Firewall shutting down...")

if __name__ == "__main__":
    start_dynamic_firewall()
