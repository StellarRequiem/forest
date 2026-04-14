#!/usr/bin/env python3
"""
Forest Decision Middleware
Intercepts and logs all agent decisions with reasoning
Central decision tracking for the entire agent system
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from enum import Enum
import threading
import queue

FOREST_PATH = Path.home() / "Forest"
VAULT_PATH = Path.home() / "ForestVault"
DECISION_LOG = VAULT_PATH / "decision_log.json"

VAULT_PATH.mkdir(exist_ok=True)


class DecisionType(Enum):
    """Types of agent decisions"""
    SPAWN = "SPAWN"  # Headmaster spawns new agent
    APPROVE = "APPROVE"  # Enforcer approves action
    BLOCK = "BLOCK"  # Enforcer blocks action
    GRADE = "GRADE"  # Brain grades agent performance
    PROMOTE = "PROMOTE"  # Brain promotes agent
    RECYCLE = "RECYCLE"  # Brain recycles agent
    EXECUTE = "EXECUTE"  # Agent executes task
    ROUTE = "ROUTE"  # CUS routes to worker
    GATE = "GATE"  # Human gate decision
    ERROR = "ERROR"  # Error decision


class DecisionStatus(Enum):
    """Status of decision"""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    BLOCKED = "BLOCKED"
    EXECUTED = "EXECUTED"
    FAILED = "FAILED"
    REVERSED = "REVERSED"


class Decision:
    """Represents a single agent decision"""
    
    def __init__(self, decision_type: DecisionType, agent_id: str, action: str, reasoning: str = ""):
        self.id = hashlib.md5(f"{agent_id}{action}{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        self.decision_type = decision_type
        self.agent_id = agent_id
        self.action = action
        self.reasoning = reasoning
        self.status = DecisionStatus.PENDING
        self.created_at = datetime.now().isoformat()
        self.approved_at = None
        self.executed_at = None
        self.reversed_at = None
        self.result = None
        self.metadata = {}
        self.hash = self._compute_hash()
    
    def _compute_hash(self) -> str:
        """Compute decision hash for tamper-evidence"""
        data = f"{self.id}|{self.decision_type.value}|{self.agent_id}|{self.action}|{self.created_at}"
        return hashlib.sha256(data.encode()).hexdigest()[:24]
    
    def approve(self):
        """Mark decision as approved"""
        self.status = DecisionStatus.APPROVED
        self.approved_at = datetime.now().isoformat()
    
    def block(self):
        """Mark decision as blocked"""
        self.status = DecisionStatus.BLOCKED
        self.approved_at = datetime.now().isoformat()
    
    def execute(self, result: Any = None):
        """Mark decision as executed"""
        self.status = DecisionStatus.EXECUTED
        self.executed_at = datetime.now().isoformat()
        self.result = result
    
    def reverse(self):
        """Reverse a decision"""
        self.status = DecisionStatus.REVERSED
        self.reversed_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'decision_type': self.decision_type.value,
            'agent_id': self.agent_id,
            'action': self.action[:100],
            'reasoning': self.reasoning[:200],
            'status': self.status.value,
            'created_at': self.created_at,
            'approved_at': self.approved_at,
            'executed_at': self.executed_at,
            'reversed_at': self.reversed_at,
            'result': str(self.result)[:100] if self.result else None,
            'hash': self.hash,
            'metadata': self.metadata,
        }


class DecisionMiddleware:
    """Middleware layer for intercepting and logging decisions"""
    
    def __init__(self):
        self.decisions: Dict[str, Decision] = {}
        self.decision_queue = queue.Queue()
        self.lock = threading.Lock()
        self._load_decisions()
    
    def _load_decisions(self):
        """Load existing decisions from log"""
        if not DECISION_LOG.exists():
            return
        
        try:
            with open(DECISION_LOG, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        decision = Decision(
                            DecisionType(data['decision_type']),
                            data['agent_id'],
                            data['action'],
                            data['reasoning']
                        )
                        self.decisions[decision.id] = decision
                    except:
                        continue
        except Exception as e:
            print(f"[ERROR] Loading decisions: {e}")
    
    def _save_decision(self, decision: Decision):
        """Save decision to log"""
        try:
            with open(DECISION_LOG, 'a') as f:
                f.write(json.dumps(decision.to_dict()) + '\n')
        except Exception as e:
            print(f"[ERROR] Saving decision: {e}")
    
    # ===== DECISION CREATION METHODS =====
    
    def record_spawn_decision(self, agent_id: str, tier: int, role: str) -> Decision:
        """Record Headmaster spawn decision"""
        action = f"Spawn tier-{tier} {role} agent"
        reasoning = f"Headmaster allocating tier-{tier} worker for {role} task"
        
        decision = Decision(DecisionType.SPAWN, agent_id, action, reasoning)
        with self.lock:
            self.decisions[decision.id] = decision
        self._save_decision(decision)
        
        print(f"[DECISION] SPAWN {agent_id}: {action}")
        return decision
    
    def record_enforcer_approval(self, agent_id: str, action: str, approved: bool) -> Decision:
        """Record Enforcer approval/block decision"""
        decision_type = DecisionType.APPROVE if approved else DecisionType.BLOCK
        reasoning = f"Enforcer gate check: {'APPROVED' if approved else 'BLOCKED'} - Action validated against constitution"
        
        decision = Decision(decision_type, agent_id, action, reasoning)
        with self.lock:
            self.decisions[decision.id] = decision
        
        if approved:
            decision.approve()
        else:
            decision.block()
        
        self._save_decision(decision)
        
        status = "APPROVED" if approved else "BLOCKED"
        print(f"[DECISION] ENFORCER {status}: {agent_id} - {action[:50]}")
        return decision
    
    def record_brain_grade(self, agent_id: str, score: float, decision_type_str: str, reasoning: str = "") -> Decision:
        """Record Forest Brain grading decision"""
        if decision_type_str == "PROMOTE":
            dtype = DecisionType.PROMOTE
        elif decision_type_str == "RECYCLE":
            dtype = DecisionType.RECYCLE
        else:
            dtype = DecisionType.GRADE
        
        action = f"Grade agent {agent_id}: {score:.1f}/100"
        full_reasoning = reasoning or f"Forest Brain evaluation: Score {score:.1f} → {decision_type_str}"
        
        decision = Decision(dtype, agent_id, action, full_reasoning)
        with self.lock:
            self.decisions[decision.id] = decision
        
        decision.execute(decision_type_str)
        self._save_decision(decision)
        
        print(f"[DECISION] BRAIN GRADE {agent_id}: {score:.1f} → {decision_type_str}")
        return decision
    
    def record_task_execution(self, agent_id: str, task: str, result: Any = None) -> Decision:
        """Record task execution decision"""
        reasoning = f"Agent {agent_id} executing assigned task"
        
        decision = Decision(DecisionType.EXECUTE, agent_id, task, reasoning)
        with self.lock:
            self.decisions[decision.id] = decision
        
        decision.execute(result)
        self._save_decision(decision)
        
        print(f"[DECISION] EXECUTE {agent_id}: {task[:50]}")
        return decision
    
    def record_cus_route(self, agent_id: str, tier: int, target_agent: str) -> Decision:
        """Record CUS routing decision"""
        action = f"Route task to tier-{tier} agent {target_agent}"
        reasoning = f"CUS orchestration: routing through tier hierarchy to {target_agent}"
        
        decision = Decision(DecisionType.ROUTE, agent_id, action, reasoning)
        with self.lock:
            self.decisions[decision.id] = decision
        
        decision.approve()
        self._save_decision(decision)
        
        print(f"[DECISION] ROUTE {agent_id} → tier-{tier} {target_agent}")
        return decision
    
    def record_human_gate(self, agent_id: str, action: str, approved: bool) -> Decision:
        """Record human gate decision"""
        decision_type = DecisionType.GATE
        reasoning = f"Human operator gate: {'APPROVED' if approved else 'REQUESTED REVIEW'}"
        
        decision = Decision(decision_type, agent_id, action, reasoning)
        with self.lock:
            self.decisions[decision.id] = decision
        
        if approved:
            decision.approve()
        else:
            decision.block()
        
        self._save_decision(decision)
        
        status = "APPROVED" if approved else "BLOCKED"
        print(f"[DECISION] HUMAN GATE {status}: {agent_id}")
        return decision
    
    # ===== DECISION REVERSAL =====
    
    def reverse_decision(self, decision_id: str) -> bool:
        """Reverse a decision"""
        with self.lock:
            if decision_id in self.decisions:
                decision = self.decisions[decision_id]
                decision.reverse()
                self._save_decision(decision)
                print(f"[DECISION] REVERSED: {decision_id} ({decision.decision_type.value})")
                return True
        return False
    
    # ===== QUERY METHODS =====
    
    def get_decisions_by_agent(self, agent_id: str, limit: int = 50) -> List[Decision]:
        """Get all decisions for an agent"""
        with self.lock:
            decisions = [d for d in self.decisions.values() if d.agent_id == agent_id]
        return sorted(decisions, key=lambda d: d.created_at, reverse=True)[:limit]
    
    def get_decisions_by_type(self, dtype: DecisionType, limit: int = 50) -> List[Decision]:
        """Get decisions by type"""
        with self.lock:
            decisions = [d for d in self.decisions.values() if d.decision_type == dtype]
        return sorted(decisions, key=lambda d: d.created_at, reverse=True)[:limit]
    
    def get_recent_decisions(self, limit: int = 50) -> List[Decision]:
        """Get most recent decisions"""
        with self.lock:
            decisions = list(self.decisions.values())
        return sorted(decisions, key=lambda d: d.created_at, reverse=True)[:limit]
    
    def get_blocked_decisions(self, limit: int = 50) -> List[Decision]:
        """Get decisions that were blocked"""
        with self.lock:
            decisions = [d for d in self.decisions.values() if d.status == DecisionStatus.BLOCKED]
        return sorted(decisions, key=lambda d: d.created_at, reverse=True)[:limit]
    
    def get_reversed_decisions(self, limit: int = 50) -> List[Decision]:
        """Get decisions that were reversed"""
        with self.lock:
            decisions = [d for d in self.decisions.values() if d.status == DecisionStatus.REVERSED]
        return sorted(decisions, key=lambda d: d.created_at, reverse=True)[:limit]
    
    def get_decision_stats(self) -> Dict[str, Any]:
        """Get decision statistics"""
        with self.lock:
            decisions = list(self.decisions.values())
        
        stats = {
            'total_decisions': len(decisions),
            'by_type': {},
            'by_status': {},
            'by_agent': {},
            'blocked_count': 0,
            'reversed_count': 0,
        }
        
        for decision in decisions:
            # Count by type
            dtype = decision.decision_type.value
            stats['by_type'][dtype] = stats['by_type'].get(dtype, 0) + 1
            
            # Count by status
            status = decision.status.value
            stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
            
            # Count by agent
            agent = decision.agent_id
            stats['by_agent'][agent] = stats['by_agent'].get(agent, 0) + 1
            
            # Count blocks and reversals
            if decision.status == DecisionStatus.BLOCKED:
                stats['blocked_count'] += 1
            if decision.status == DecisionStatus.REVERSED:
                stats['reversed_count'] += 1
        
        return stats
    
    def get_all_decisions_as_dict(self, limit: int = 100) -> List[Dict]:
        """Get all decisions as dictionaries for dashboard"""
        decisions = self.get_recent_decisions(limit)
        return [d.to_dict() for d in decisions]


# Global middleware instance
_middleware = None

def get_middleware() -> DecisionMiddleware:
    """Get or create global middleware instance"""
    global _middleware
    if _middleware is None:
        _middleware = DecisionMiddleware()
    return _middleware


if __name__ == "__main__":
    middleware = get_middleware()
    
    print("\n" + "=" * 80)
    print("FOREST DECISION MIDDLEWARE - VERIFICATION TEST")
    print("=" * 80)
    
    # Test decision creation
    print("\n[TEST 1] Creating test decisions...")
    
    d1 = middleware.record_spawn_decision("agent-001", 2, "worker")
    print(f"  ✅ Spawn decision: {d1.id}")
    
    d2 = middleware.record_enforcer_approval("agent-001", "Execute scan", approved=True)
    print(f"  ✅ Approval decision: {d2.id}")
    
    d3 = middleware.record_enforcer_approval("agent-002", "Delete file", approved=False)
    print(f"  ✅ Block decision: {d3.id}")
    
    d4 = middleware.record_brain_grade("agent-001", 85.5, "PROMOTE", "Excellent performance")
    print(f"  ✅ Grade decision: {d4.id}")
    
    d5 = middleware.record_task_execution("agent-001", "Network scan", result="Completed")
    print(f"  ✅ Execute decision: {d5.id}")
    
    # Test queries
    print("\n[TEST 2] Testing queries...")
    
    agent_decisions = middleware.get_decisions_by_agent("agent-001")
    print(f"  ✅ Decisions for agent-001: {len(agent_decisions)}")
    
    blocked = middleware.get_blocked_decisions()
    print(f"  ✅ Blocked decisions: {len(blocked)}")
    
    stats = middleware.get_decision_stats()
    print(f"  ✅ Total decisions: {stats['total_decisions']}")
    print(f"     By type: {stats['by_type']}")
    print(f"     By status: {stats['by_status']}")
    
    # Test reversal
    print("\n[TEST 3] Testing reversal...")
    middleware.reverse_decision(d2.id)
    print(f"  ✅ Reversed decision: {d2.id}")
    
    # Show sample decisions
    print("\n[TEST 4] Sample decisions (as dictionary)...")
    all_dicts = middleware.get_all_decisions_as_dict(limit=3)
    for d in all_dicts:
        print(f"  - {d['id']}: {d['decision_type']} ({d['status']}) - {d['action'][:50]}")
    
    print("\n" + "=" * 80)
    print("✅ DECISION MIDDLEWARE VERIFICATION COMPLETE")
    print("=" * 80 + "\n")
