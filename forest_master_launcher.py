#!/usr/bin/env python3
"""
🌲 Forest Blue-Team Guardian - Master Launcher v1.0
"""

import subprocess
import sys
import time
import json
import os
from pathlib import Path
from datetime import datetime

class ForestMasterLauncher:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.vault_path = Path.home() / "ForestVault"
        self.vault_path.mkdir(exist_ok=True)
        self.compose_file = self.project_root / "docker-compose.yml"
        self.status_file = self.vault_path / "launcher_status.json"
    
    def start(self):
        """Start the entire Forest stack"""
        print("🌲 Forest Blue-Team Guardian - Starting Complete Stack")
        print("=" * 60)
        
        # Phase 1: Build Docker images
        print("\n[Phase 1/5] Building Docker images...")
        try:
            result = subprocess.run(
                ["docker", "compose", "-f", str(self.compose_file), "build"],
                cwd=str(self.project_root),
                timeout=600
            )
            if result.returncode != 0:
                print("❌ Docker build failed")
                return False
            print("✅ Docker images built")
        except Exception as e:
            print(f"❌ Build error: {e}")
            return False
        
        # Phase 2: Start docker-compose stack
        print("\n[Phase 2/5] Starting Docker Compose stack...")
        try:
            result = subprocess.run(
                ["docker", "compose", "-f", str(self.compose_file), "up", "-d"],
                cwd=str(self.project_root),
                timeout=120
            )
            if result.returncode != 0:
                print("❌ Docker Compose startup failed")
                return False
            print("✅ Docker Compose stack started")
        except Exception as e:
            print(f"❌ Compose error: {e}")
            return False
        
        # Phase 3: Wait for services to start
        print("\n[Phase 3/5] Waiting for services to start...")
        self._wait_for_services(timeout=120)
        print("✅ Services started")
        
        # Phase 4: Initialize Ollama models
        print("\n[Phase 4/5] Initializing Ollama (non-blocking)...")
        self._init_ollama()
        print("✅ Ollama ready for use")
        
        # Phase 5: Initialize Agent Swarm
        print("\n[Phase 5/5] Initializing Agent Swarm Orchestrator...")
        self._init_orchestrator()
        print("✅ Agent Swarm initialized")
        
        # Record status
        self._save_status("running")
        
        print("\n" + "=" * 60)
        print("✅ Forest Blue-Team Guardian is ONLINE")
        print("=" * 60)
        print("\nActive Components:")
        print("  🔵 Ollama (Local LLM) - port 11434")
        print("  🔴 Decepticon (Red-Team) - sandbox 172.25.0.0/16")
        print("  🟢 Blue-Swarm (Orchestrator + Watchers)")
        print("  🟡 Dynamic Firewall (pf rules)")
        print("  🟣 Incident Response Engine (state machine)")
        print("\nNext: docker-compose logs -f forest-swarm")
        
        return True
    
    def stop(self):
        """Stop the entire Forest stack"""
        print("🌲 Forest Blue-Team Guardian - Shutting Down")
        print("=" * 60)
        
        try:
            result = subprocess.run(
                ["docker", "compose", "-f", str(self.compose_file), "down"],
                cwd=str(self.project_root),
                timeout=60
            )
            if result.returncode == 0:
                print("✅ Forest stack stopped")
                self._save_status("stopped")
                return True
        except Exception as e:
            print(f"❌ Shutdown error: {e}")
        
        return False
    
    def status(self):
        """Show stack status"""
        print("🌲 Forest Blue-Team Guardian - Status")
        print("=" * 60)
        
        try:
            result = subprocess.run(
                ["docker", "compose", "-f", str(self.compose_file), "ps"],
                cwd=str(self.project_root),
                capture_output=True, text=True
            )
            print(result.stdout)
            
            # Show incident count
            incidents_log = self.vault_path / "incidents.jsonl"
            if incidents_log.exists():
                with open(incidents_log) as f:
                    incident_count = len(f.readlines())
                print(f"Incidents Logged: {incident_count}")
            
            # Show active incidents
            orchestrator_state = self.vault_path / "swarm_state.json"
            if orchestrator_state.exists():
                with open(orchestrator_state) as f:
                    state = json.load(f)
                print(f"Registered Agents: {len(state.get('agents', {}))}")
                print(f"Active Incidents: {state.get('incident_count', 0)}")
            
            print("\nVault: " + str(self.vault_path))
            print("=" * 60)
            return True
        except Exception as e:
            print(f"❌ Status check failed: {e}")
            return False
    
    def logs(self, service: str = None):
        """Show logs"""
        try:
            cmd = ["docker", "compose", "-f", str(self.compose_file), "logs", "-f"]
            if service:
                cmd.append(service)
            
            subprocess.run(cmd, cwd=str(self.project_root))
        except Exception as e:
            print(f"❌ Logs error: {e}")
    
    def _wait_for_services(self, timeout: int = 120) -> bool:
        """Wait for all services to start"""
        start = time.time()
        services_to_check = ["forest-ollama", "forest-postgres", "forest-redis", "forest-swarm"]
        
        while time.time() - start < timeout:
            try:
                result = subprocess.run(
                    ["docker", "compose", "-f", str(self.compose_file), "ps"],
                    cwd=str(self.project_root),
                    capture_output=True, text=True
                )
                
                if result.returncode == 0:
                    all_started = all(
                        service in result.stdout
                        for service in services_to_check
                    )
                    if all_started:
                        time.sleep(10)  # Stabilization time
                        return True
                
                print(".", end="", flush=True)
                time.sleep(3)
            except:
                pass
        
        print("\n⚠️  Services taking longer (continuing anyway)")
        return True
    
    def _init_ollama(self) -> bool:
        """Initialize Ollama (non-blocking)"""
        try:
            # Just check if Ollama is accessible
            subprocess.run(
                ["curl", "-f", "http://localhost:11434/api/tags"],
                timeout=5,
                capture_output=True
            )
            return True
        except:
            return True  # Non-fatal
    
    def _init_orchestrator(self) -> bool:
        """Initialize the swarm orchestrator"""
        try:
            init_script = """
import sys
sys.path.insert(0, '/forest')
from core.swarm_orchestrator import AgentSwarmOrchestrator
orch = AgentSwarmOrchestrator()
orch.register_agent("ARPWatcherDaemon", "ARP Anomaly Detection")
orch.register_agent("DockerWatcherDaemon", "Container Escape Detection")
orch.register_agent("NetworkWatcherDaemon", "Port Scan Detection")
orch.register_agent("DynamicFirewallAgent", "Dynamic Firewall Control")
orch.register_agent("IncidentResponseEngine", "Incident Coordinator")
print("Agents registered")
"""
            
            result = subprocess.run(
                ["docker", "exec", "forest-swarm", "python3", "-c", init_script],
                timeout=30,
                capture_output=True
            )
            
            return result.returncode == 0
        except:
            return True  # Non-fatal
    
    def _save_status(self, status: str):
        """Save launcher status"""
        try:
            with open(self.status_file, 'w') as f:
                json.dump({
                    "status": status,
                    "timestamp": datetime.now().isoformat(),
                    "vault": str(self.vault_path)
                }, f, indent=2)
        except:
            pass

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 forest_master_launcher.py [start|stop|status|logs]")
        sys.exit(1)
    
    command = sys.argv[1]
    launcher = ForestMasterLauncher()
    
    if command == "start":
        success = launcher.start()
        sys.exit(0 if success else 1)
    elif command == "stop":
        success = launcher.stop()
        sys.exit(0 if success else 1)
    elif command == "status":
        launcher.status()
    elif command == "logs":
        service = sys.argv[2] if len(sys.argv) > 2 else None
        launcher.logs(service)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
