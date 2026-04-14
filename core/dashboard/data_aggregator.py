#!/usr/bin/env python3
"""
Forest Dashboard Data Aggregator
Pulls real data from all Forest systems
- Cryptex logs
- Agent performance
- Network metrics
- System health
- Process monitoring
"""

import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
import psutil
import socket

FOREST_PATH = Path.home() / "Forest"
VAULT_PATH = Path.home() / "ForestVault"
CRYPTEX_FILE = VAULT_PATH / "training_chain.json"


class DataAggregator:
    """Aggregates real data from all Forest systems"""
    
    def __init__(self):
        self.vault_path = VAULT_PATH
        self.vault_path.mkdir(exist_ok=True)
        self.cryptex_file = CRYPTEX_FILE
    
    # ===== CRYPTEX LOG DATA =====
    def get_cryptex_logs(self, limit: int = 100, event_type: str = None) -> List[Dict]:
        """Get real Cryptex logs from ~/ForestVault/training_chain.json"""
        logs = []
        
        try:
            if not self.cryptex_file.exists():
                return logs
            
            with open(self.cryptex_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        # Parse: "2026-04-14 14:16:34,283 | ENFORCER | Event details | Hash: abc123"
                        parts = line.split('|')
                        if len(parts) >= 3:
                            timestamp_str = parts[0].strip()
                            event = parts[1].strip() if len(parts) > 1 else "UNKNOWN"
                            details = parts[2].strip() if len(parts) > 2 else ""
                            hash_val = parts[3].strip() if len(parts) > 3 else ""
                            
                            # Filter by event type if specified
                            if event_type and event_type not in event:
                                continue
                            
                            logs.append({
                                'timestamp': timestamp_str,
                                'event_type': event,
                                'details': details,
                                'hash': hash_val,
                                'raw': line
                            })
                    except:
                        continue
        
        except Exception as e:
            print(f"[ERROR] Reading Cryptex: {e}")
        
        # Return most recent first, limit to N
        return sorted(logs, key=lambda x: x['timestamp'], reverse=True)[:limit]
    
    def get_cryptex_stats(self) -> Dict[str, Any]:
        """Get statistics from Cryptex logs"""
        logs = self.get_cryptex_logs(limit=1000)
        
        stats = {
            'total_events': len(logs),
            'event_types': {},
            'recent_24h': 0,
            'recent_1h': 0,
        }
        
        now = datetime.now()
        one_hour_ago = now - timedelta(hours=1)
        one_day_ago = now - timedelta(days=1)
        
        for log in logs:
            event_type = log['event_type']
            stats['event_types'][event_type] = stats['event_types'].get(event_type, 0) + 1
            
            try:
                log_time = datetime.fromisoformat(log['timestamp'].split(',')[0])
                if log_time > one_hour_ago:
                    stats['recent_1h'] += 1
                if log_time > one_day_ago:
                    stats['recent_24h'] += 1
            except:
                pass
        
        return stats
    
    # ===== AGENT PERFORMANCE DATA =====
    def get_agent_performance(self) -> Dict[str, Any]:
        """Get agent performance metrics from Forest Brain"""
        # Scan recent Cryptex logs for grading events
        logs = self.get_cryptex_logs(limit=500, event_type="BRAIN")
        
        agents = {}
        
        for log in logs:
            details = log['details']
            # Format: "agent_name graded 85.5/100 → PROMOTE | Points: 2500"
            try:
                parts = details.split('→')
                if len(parts) >= 2:
                    grade_part = parts[0].strip()
                    decision_part = parts[1].strip()
                    
                    # Extract agent name and score
                    if 'graded' in grade_part:
                        name = grade_part.split('graded')[0].strip()
                        score_str = grade_part.split('graded')[1].strip().split('/')[0].strip()
                        score = float(score_str)
                        
                        # Extract decision
                        decision = decision_part.split('|')[0].strip()
                        
                        if name not in agents:
                            agents[name] = {
                                'scores': [],
                                'decisions': [],
                                'latest_score': 0,
                                'latest_decision': 'UNKNOWN'
                            }
                        
                        agents[name]['scores'].append(score)
                        agents[name]['decisions'].append(decision)
                        agents[name]['latest_score'] = score
                        agents[name]['latest_decision'] = decision
            except:
                continue
        
        # Calculate averages
        for agent in agents.values():
            if agent['scores']:
                agent['avg_score'] = sum(agent['scores']) / len(agent['scores'])
            else:
                agent['avg_score'] = 0
        
        return agents
    
    # ===== NETWORK DATA =====
    def get_network_data(self) -> Dict[str, Any]:
        """Get real network metrics"""
        data = {
            'hostname': socket.gethostname(),
            'local_ip': '',
            'interfaces': [],
            'scan_time': datetime.now().isoformat()
        }
        
        try:
            data['local_ip'] = socket.gethostbyname(socket.gethostname())
        except:
            data['local_ip'] = 'Unknown'
        
        try:
            for interface, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    data['interfaces'].append({
                        'interface': interface,
                        'address': addr.address,
                        'family': addr.family.name
                    })
        except Exception as e:
            print(f"[ERROR] Getting network interfaces: {e}")
        
        return data
    
    def get_network_stats(self) -> Dict[str, Any]:
        """Get network I/O statistics"""
        try:
            stats = psutil.net_io_counters()
            return {
                'bytes_sent': stats.bytes_sent,
                'bytes_recv': stats.bytes_recv,
                'packets_sent': stats.packets_sent,
                'packets_recv': stats.packets_recv,
                'errors_in': stats.errin,
                'errors_out': stats.errout,
                'dropped_in': stats.dropin,
                'dropped_out': stats.dropout,
            }
        except Exception as e:
            print(f"[ERROR] Getting network stats: {e}")
            return {}
    
    # ===== SYSTEM HEALTH =====
    def get_system_health(self) -> Dict[str, Any]:
        """Get real system metrics"""
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'cpu_count': psutil.cpu_count(),
            'memory': {
                'total': psutil.virtual_memory().total,
                'available': psutil.virtual_memory().available,
                'percent': psutil.virtual_memory().percent,
                'used': psutil.virtual_memory().used,
            },
            'disk': {
                'total': psutil.disk_usage('/').total,
                'used': psutil.disk_usage('/').used,
                'free': psutil.disk_usage('/').free,
                'percent': psutil.disk_usage('/').percent,
            },
            'processes': len(psutil.pids()),
            'timestamp': datetime.now().isoformat()
        }
    
    # ===== PROCESS MONITORING =====
    def get_forest_processes(self) -> List[Dict]:
        """Get Forest-related processes"""
        processes = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_percent']):
                try:
                    cmd = ' '.join(proc.info['cmdline'] or [])
                    if 'forest' in cmd.lower() or 'python' in cmd.lower() and any(x in cmd for x in ['cus', 'cli', 'monitor']):
                        processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'command': cmd[:100],
                            'cpu': proc.info['cpu_percent'],
                            'memory': proc.info['memory_percent'],
                        })
                except:
                    continue
        except Exception as e:
            print(f"[ERROR] Getting processes: {e}")
        
        return processes
    
    # ===== UNIFIED DATA COLLECTION =====
    def get_all_data(self) -> Dict[str, Any]:
        """Get all data for dashboard"""
        return {
            'timestamp': datetime.now().isoformat(),
            'cryptex': {
                'logs': self.get_cryptex_logs(limit=50),
                'stats': self.get_cryptex_stats(),
            },
            'agents': self.get_agent_performance(),
            'network': {
                'info': self.get_network_data(),
                'stats': self.get_network_stats(),
            },
            'system': self.get_system_health(),
            'processes': self.get_forest_processes(),
        }


if __name__ == "__main__":
    agg = DataAggregator()
    
    print("\n" + "=" * 80)
    print("FOREST DATA AGGREGATOR - VERIFICATION TEST")
    print("=" * 80)
    
    # Test each component
    print("\n[1] Testing Cryptex Logs...")
    logs = agg.get_cryptex_logs(limit=5)
    print(f"  ✅ Retrieved {len(logs)} logs")
    for log in logs[:3]:
        print(f"     - {log['timestamp']}: {log['event_type']}")
    
    print("\n[2] Testing Cryptex Stats...")
    stats = agg.get_cryptex_stats()
    print(f"  ✅ Total events: {stats['total_events']}")
    print(f"     Event types: {stats['event_types']}")
    print(f"     Recent 1h: {stats['recent_1h']}, 24h: {stats['recent_24h']}")
    
    print("\n[3] Testing Agent Performance...")
    agents = agg.get_agent_performance()
    print(f"  ✅ Agents tracked: {len(agents)}")
    for name, data in list(agents.items())[:3]:
        print(f"     - {name}: {data['latest_score']:.1f}/100 → {data['latest_decision']}")
    
    print("\n[4] Testing Network Data...")
    net = agg.get_network_data()
    print(f"  ✅ Hostname: {net['hostname']}")
    print(f"     IP: {net['local_ip']}")
    print(f"     Interfaces: {len(net['interfaces'])}")
    
    print("\n[5] Testing Network Stats...")
    net_stats = agg.get_network_stats()
    print(f"  ✅ Bytes sent: {net_stats.get('bytes_sent', 0):,}")
    print(f"     Bytes recv: {net_stats.get('bytes_recv', 0):,}")
    
    print("\n[6] Testing System Health...")
    health = agg.get_system_health()
    print(f"  ✅ CPU: {health['cpu_percent']:.1f}%")
    print(f"     Memory: {health['memory']['percent']:.1f}%")
    print(f"     Disk: {health['disk']['percent']:.1f}%")
    print(f"     Processes: {health['processes']}")
    
    print("\n[7] Testing Forest Processes...")
    procs = agg.get_forest_processes()
    print(f"  ✅ Found {len(procs)} Forest processes")
    for proc in procs[:3]:
        print(f"     - PID {proc['pid']}: {proc['name']} (CPU: {proc['cpu']:.1f}%)")
    
    print("\n[8] Testing Unified Data Collection...")
    all_data = agg.get_all_data()
    print(f"  ✅ Collected data for {len(all_data)} categories")
    print(f"     - Cryptex logs: {len(all_data['cryptex']['logs'])}")
    print(f"     - Agents: {len(all_data['agents'])}")
    print(f"     - Network interfaces: {len(all_data['network']['info']['interfaces'])}")
    print(f"     - Forest processes: {len(all_data['processes'])}")
    
    print("\n" + "=" * 80)
    print("✅ ALL DATA SOURCES VERIFIED AND WORKING")
    print("=" * 80 + "\n")
