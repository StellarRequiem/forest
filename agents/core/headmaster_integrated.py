#!/usr/bin/env python3
"""
Headmaster (Integrated with Decision Middleware)
Top-tier orchestration engine with full decision logging
"""

import sys
from pathlib import Path
from typing import List, Dict, Any
import uuid
from datetime import datetime

FOREST_PATH = Path.home() / "Forest"
sys.path.insert(0, str(FOREST_PATH))

from core.decision_middleware import get_middleware, DecisionType


class Headmaster:
    """
    CUS Tier 4 - Headmaster Orchestrator
    Spawns agents, routes tasks, makes strategic decisions
    All decisions logged via middleware
    """
    
    def __init__(self):
        self.middleware = get_middleware()
        self.id = f"headmaster-{uuid.uuid4().hex[:8]}"
        self.spawned_agents = []
        self.routed_tasks = []
        print(f"[HEADMASTER] Initialized: {self.id}")
    
    def spawn_agent(self, tier: int, role: str, purpose: str = "", count: int = 1) -> List[str]:
        """
        Spawn new agents at specified tier
        Logs SPAWN decision for each agent
        """
        agents = []
        
        for i in range(count):
            agent_id = f"{role}-tier{tier}-{uuid.uuid4().hex[:8]}"
            
            # Log spawn decision
            decision = self.middleware.record_spawn_decision(
                agent_id=agent_id,
                tier=tier,
                role=role
            )
            
            # Store metadata
            decision.metadata = {
                'purpose': purpose,
                'tier': tier,
                'role': role,
                'spawned_by': self.id,
                'count': count
            }
            
            agents.append(agent_id)
            self.spawned_agents.append(agent_id)
            
            print(f"[HEADMASTER] ✅ Spawned {agent_id} (tier {tier}) for {purpose}")
        
        return agents
    
    def route_task(self, task_name: str, target_tier: int = 2, target_agent: str = None) -> Dict[str, Any]:
        """
        Route task to appropriate tier level
        Logs ROUTE decision
        """
        
        if target_agent is None:
            # Pick first available agent at target tier
            matching = [a for a in self.spawned_agents if f"tier{target_tier}" in a]
            if not matching:
                print(f"[HEADMASTER] ❌ No agents at tier {target_tier}")
                return {'success': False, 'error': 'no_agents_at_tier'}
            target_agent = matching[0]
        
        # Log routing decision
        decision = self.middleware.record_cus_route(
            agent_id=self.id,
            tier=target_tier,
            target_agent=target_agent
        )
        
        # Store metadata
        decision.metadata = {
            'task_name': task_name,
            'target_tier': target_tier,
            'target_agent': target_agent,
            'routed_at': datetime.now().isoformat()
        }
        
        self.routed_tasks.append((task_name, target_agent))
        
        print(f"[HEADMASTER] ✅ Routed '{task_name}' → {target_agent}")
        
        return {
            'success': True,
            'task_name': task_name,
            'target_agent': target_agent,
            'decision_id': decision.id
        }
    
    def request_human_approval(self, action: str, agent_id: str) -> bool:
        """
        Request human approval for sensitive actions
        Logs GATE decision
        """
        
        print(f"\n🔒 HEADMASTER GATE REQUEST")
        print(f"   Agent: {agent_id}")
        print(f"   Action: {action}")
        
        choice = input("   Approve? (yes/no) > ").strip().lower()
        approved = choice in ['yes', 'y']
        
        # Log human gate decision
        decision = self.middleware.record_human_gate(
            agent_id=agent_id,
            action=action,
            approved=approved
        )
        
        decision.metadata = {
            'action_type': action,
            'human_operator': 'interactive'
        }
        
        return approved
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all spawned agents"""
        return {
            'headmaster_id': self.id,
            'total_agents_spawned': len(self.spawned_agents),
            'agents': self.spawned_agents,
            'total_tasks_routed': len(self.routed_tasks),
            'recent_tasks': self.routed_tasks[-5:]
        }
    
    def get_decision_history(self) -> List[Dict]:
        """Get all decisions made by this headmaster"""
        decisions = self.middleware.get_decisions_by_agent(self.id, limit=50)
        return [d.to_dict() for d in decisions]


# Global instance
_headmaster = None

def get_headmaster() -> Headmaster:
    """Get or create global Headmaster instance"""
    global _headmaster
    if _headmaster is None:
        _headmaster = Headmaster()
    return _headmaster


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("HEADMASTER (INTEGRATED) - VERIFICATION TEST")
    print("=" * 80)
    
    headmaster = get_headmaster()
    
    # Test 1: Spawn agents
    print("\n[TEST 1] Spawning agents...")
    agents = headmaster.spawn_agent(tier=2, role="scanner", purpose="security scanning", count=3)
    print(f"  ✅ Spawned {len(agents)} agents")
    
    # Test 2: Route tasks
    print("\n[TEST 2] Routing tasks...")
    result = headmaster.route_task("network_scan", target_tier=2)
    print(f"  ✅ Routed task: {result['success']}")
    
    # Test 3: Get status
    print("\n[TEST 3] Status check...")
    status = headmaster.get_agent_status()
    print(f"  ✅ Agents spawned: {status['total_agents_spawned']}")
    print(f"  ✅ Tasks routed: {status['total_tasks_routed']}")
    
    # Test 4: Decision history
    print("\n[TEST 4] Decision history...")
    history = headmaster.get_decision_history()
    print(f"  ✅ Total decisions: {len(history)}")
    for h in history[:3]:
        print(f"     - {h['decision_type']}: {h['action'][:40]}")
    
    print("\n" + "=" * 80)
    print("✅ HEADMASTER (INTEGRATED) READY")
    print("=" * 80 + "\n")
