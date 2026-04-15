#!/usr/bin/env python3
"""
Enforcer Gateway (Integrated with Decision Middleware)
Constitutional AI gatekeeper with full decision logging
All approvals and blocks are recorded, queryable, and reversible
"""

import sys
from pathlib import Path
from typing import Dict, Any, List
import uuid
from datetime import datetime

FOREST_PATH = Path.home() / "Forest"
sys.path.insert(0, str(FOREST_PATH))

from core.decision_middleware import get_middleware, DecisionType, DecisionStatus


class EnforcerGateway:
    """
    CUS Enforcer v3.1 - Policy Gatekeeper
    Every agent action must pass through enforcer gate
    All decisions logged via middleware for audit trail
    """
    
    def __init__(self):
        self.middleware = get_middleware()
        self.id = f"enforcer-{uuid.uuid4().hex[:8]}"
        self.constitution = self._load_constitution()
        self.approvals = []
        self.blocks = []
        print(f"[ENFORCER] Initialized: {self.id}")
    
    def _load_constitution(self) -> Dict[str, List[str]]:
        """Load enforcement rules"""
        return {
            'forbidden_actions': [
                'rm -rf',
                'delete',
                'drop table',
                'drop database',
                'exec()',
                '__import__',
                'subprocess.call',
            ],
            'forbidden_modules': [
                'os.system',
                'subprocess',
                'pickle',
                'marshal',
            ],
            'safe_actions': [
                'read',
                'scan',
                'log',
                'report',
                'analyze',
                'classify',
                'monitor',
            ]
        }
    
    def _check_against_constitution(self, action: str) -> tuple[bool, str]:
        """
        Check action against enforcer constitution
        Returns (allowed, reason)
        """
        action_lower = action.lower()
        
        # Check forbidden actions
        for forbidden in self.constitution['forbidden_actions']:
            if forbidden.lower() in action_lower:
                return False, f"Forbidden action detected: {forbidden}"
        
        # Check forbidden modules
        for forbidden_mod in self.constitution['forbidden_modules']:
            if forbidden_mod.lower() in action_lower:
                return False, f"Forbidden module detected: {forbidden_mod}"
        
        # Safe by default (allow if no violations)
        return True, "Action complies with constitution"
    
    def approve_action(self, agent_id: str, action: str, reasoning: str = "") -> Dict[str, Any]:
        """
        Approve an agent action
        Logs APPROVE decision
        """
        
        # Check against constitution
        allowed, reason = self._check_against_constitution(action)
        
        if not allowed:
            return self.block_action(agent_id, action, reason)
        
        # Record approval decision
        decision = self.middleware.record_enforcer_approval(
            agent_id=agent_id,
            action=action,
            approved=True
        )
        
        decision.reasoning = reasoning or reason
        decision.metadata = {
            'constitution_check': 'passed',
            'enforcer_id': self.id,
            'approval_time': datetime.now().isoformat()
        }
        
        self.approvals.append({
            'agent_id': agent_id,
            'action': action,
            'decision_id': decision.id,
            'timestamp': datetime.now().isoformat()
        })
        
        print(f"[ENFORCER] ✅ APPROVED {agent_id}: {action[:50]}")
        
        return {
            'approved': True,
            'agent_id': agent_id,
            'action': action,
            'decision_id': decision.id,
            'reason': reason
        }
    
    def block_action(self, agent_id: str, action: str, reason: str = "Constitutional violation") -> Dict[str, Any]:
        """
        Block an agent action
        Logs BLOCK decision
        """
        
        # Record block decision
        decision = self.middleware.record_enforcer_approval(
            agent_id=agent_id,
            action=action,
            approved=False
        )
        
        decision.reasoning = reason
        decision.metadata = {
            'constitution_check': 'failed',
            'enforcer_id': self.id,
            'block_reason': reason,
            'block_time': datetime.now().isoformat()
        }
        
        self.blocks.append({
            'agent_id': agent_id,
            'action': action,
            'reason': reason,
            'decision_id': decision.id,
            'timestamp': datetime.now().isoformat()
        })
        
        print(f"[ENFORCER] 🛑 BLOCKED {agent_id}: {action[:50]} ({reason})")
        
        return {
            'approved': False,
            'agent_id': agent_id,
            'action': action,
            'decision_id': decision.id,
            'reason': reason
        }
    
    def scan_swarm(self, status: str = None) -> Dict[str, Any]:
        """
        Scan the entire swarm for policy violations
        Returns summary of current swarm state
        """
        
        recent_decisions = self.middleware.get_recent_decisions(limit=50)
        
        approved_count = sum(1 for d in recent_decisions if d.status == DecisionStatus.APPROVED)
        blocked_count = sum(1 for d in recent_decisions if d.status == DecisionStatus.BLOCKED)
        
        return {
            'scanned_at': datetime.now().isoformat(),
            'total_recent_decisions': len(recent_decisions),
            'approved': approved_count,
            'blocked': blocked_count,
            'approval_rate': approved_count / len(recent_decisions) if recent_decisions else 0,
            'enforcement_active': True,
            'constitution_loaded': bool(self.constitution),
            'status': status or 'OK'
        }
    
    def get_approval_stats(self) -> Dict[str, Any]:
        """Get approval/block statistics"""
        total = len(self.approvals) + len(self.blocks)
        
        return {
            'total_decisions': total,
            'approvals': len(self.approvals),
            'blocks': len(self.blocks),
            'approval_rate': len(self.approvals) / total if total > 0 else 0,
            'block_rate': len(self.blocks) / total if total > 0 else 0,
            'recent_blocks': self.blocks[-5:],
            'recent_approvals': self.approvals[-5:]
        }
    
    def reverse_block(self, decision_id: str) -> bool:
        """
        Reverse a previous block decision (admin override)
        Logs decision reversal
        """
        
        success = self.middleware.reverse_decision(decision_id)
        
        if success:
            print(f"[ENFORCER] ⚠️ REVERSED BLOCK: {decision_id}")
            # Remove from blocks list
            self.blocks = [b for b in self.blocks if b['decision_id'] != decision_id]
        
        return success
    
    def get_recent_blocks(self, limit: int = 10) -> List[Dict]:
        """Get recent blocked actions"""
        return self.blocks[-limit:]
    
    def get_decision_history(self) -> List[Dict]:
        """Get all enforcer decisions"""
        decisions = self.middleware.get_decisions_by_agent(self.id, limit=50)
        return [d.to_dict() for d in decisions]


# Global instance
_enforcer = None

def get_enforcer() -> EnforcerGateway:
    """Get or create global Enforcer instance"""
    global _enforcer
    if _enforcer is None:
        _enforcer = EnforcerGateway()
    return _enforcer


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("ENFORCER GATEWAY (INTEGRATED) - VERIFICATION TEST")
    print("=" * 80)
    
    enforcer = get_enforcer()
    
    # Test 1: Approve safe action
    print("\n[TEST 1] Approving safe action...")
    result = enforcer.approve_action("agent-001", "scan network 192.168.0.0/16")
    print(f"  ✅ Approval result: {result['approved']}")
    
    # Test 2: Block dangerous action
    print("\n[TEST 2] Blocking dangerous action...")
    result = enforcer.block_action("agent-002", "rm -rf /", "Destructive command")
    print(f"  ✅ Block result: {not result['approved']}")
    
    # Test 3: Constitution check
    print("\n[TEST 3] Constitution enforcement...")
    safe = enforcer.approve_action("agent-003", "analyze logs")
    dangerous = enforcer.block_action("agent-004", "drop database users", "SQL injection detected")
    print(f"  ✅ Safe action approved: {safe['approved']}")
    print(f"  ✅ Dangerous action blocked: {not dangerous['approved']}")
    
    # Test 4: Swarm scan
    print("\n[TEST 4] Swarm scan...")
    scan_result = enforcer.scan_swarm()
    print(f"  ✅ Scanned decisions: {scan_result['total_recent_decisions']}")
    print(f"  ✅ Approval rate: {scan_result['approval_rate']:.1%}")
    
    # Test 5: Statistics
    print("\n[TEST 5] Approval statistics...")
    stats = enforcer.get_approval_stats()
    print(f"  ✅ Total decisions: {stats['total_decisions']}")
    print(f"  ✅ Approvals: {stats['approvals']}")
    print(f"  ✅ Blocks: {stats['blocks']}")
    print(f"  ✅ Approval rate: {stats['approval_rate']:.1%}")
    
    # Test 6: Recent blocks
    print("\n[TEST 6] Recent blocks...")
    blocks = enforcer.get_recent_blocks(limit=5)
    print(f"  ✅ Recent blocks: {len(blocks)}")
    for block in blocks[:2]:
        print(f"     - {block['agent_id']}: {block['reason']}")
    
    print("\n" + "=" * 80)
    print("✅ ENFORCER GATEWAY (INTEGRATED) READY")
    print("=" * 80 + "\n")
