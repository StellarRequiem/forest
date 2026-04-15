#!/usr/bin/env python3
"""
Forest Brain (Integrated with Decision Middleware)
Agent grading, credentialing, and reward system
All grading decisions logged via middleware
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple
import uuid
from datetime import datetime
import json

FOREST_PATH = Path.home() / "Forest"
VAULT_PATH = Path.home() / "ForestVault"
sys.path.insert(0, str(FOREST_PATH))

from core.decision_middleware import get_middleware, DecisionType

# Ensure vault exists
VAULT_PATH.mkdir(exist_ok=True)


class ForestBrain:
    """
    Forest Brain - Agent grading and credentialing system
    Evaluates agent performance and makes promotion/study/recycle decisions
    All decisions logged via middleware
    """
    
    def __init__(self):
        self.middleware = get_middleware()
        self.id = f"brain-{uuid.uuid4().hex[:8]}"
        self.agent_credentials = {}  # agent_id → credential record
        self.reward_ledger = {}      # agent_id → reward points
        self.grade_history = []
        self._load_ledger()
        print(f"[BRAIN] Initialized: {self.id}")
    
    def _load_ledger(self):
        """Load existing reward ledger"""
        ledger_path = VAULT_PATH / "reward_ledger.json"
        if ledger_path.exists():
            try:
                with open(ledger_path, 'r') as f:
                    data = json.load(f)
                    self.reward_ledger = data.get('ledger', {})
                    self.agent_credentials = data.get('credentials', {})
            except:
                pass
    
    def _save_ledger(self):
        """Save reward ledger to vault"""
        ledger_path = VAULT_PATH / "reward_ledger.json"
        try:
            with open(ledger_path, 'w') as f:
                json.dump({
                    'ledger': self.reward_ledger,
                    'credentials': self.agent_credentials,
                    'updated_at': datetime.now().isoformat()
                }, f, indent=2)
        except Exception as e:
            print(f"[BRAIN] Error saving ledger: {e}")
    
    def issue_credential(self, agent_id: str, tier: int, role: str) -> Dict[str, Any]:
        """
        Issue credential to new agent
        Creates cryptographic-style signature
        """
        
        credential = {
            'agent_id': agent_id,
            'credential_id': f"cred-{uuid.uuid4().hex[:12]}",
            'tier': tier,
            'role': role,
            'issued_at': datetime.now().isoformat(),
            'status': 'active',
            'signature': f"sig-{uuid.uuid4().hex[:16]}",
            'expiry': None
        }
        
        self.agent_credentials[agent_id] = credential
        self.reward_ledger[agent_id] = 0  # Start at 0 points
        
        self._save_ledger()
        
        print(f"[BRAIN] ✅ Issued credential to {agent_id}: {credential['credential_id']}")
        
        return credential
    
    def grade_agent(self, agent_id: str, task_score: float, behavior_score: float = None, 
                    efficiency_score: float = None, reasoning: str = "") -> Dict[str, Any]:
        """
        Grade agent performance
        Calculates overall score and determines action (PROMOTE/STUDY/RECYCLE)
        Logs GRADE decision via middleware
        """
        
        # Calculate scores
        if behavior_score is None:
            behavior_score = task_score * 0.8
        if efficiency_score is None:
            efficiency_score = task_score * 0.9
        
        # Overall score (weighted average)
        overall_score = (task_score * 0.5 + behavior_score * 0.25 + efficiency_score * 0.25)
        
        # Determine action
        if overall_score >= 85:
            action = "PROMOTE"
            reward_delta = 5
            action_reason = f"Excellent performance ({overall_score:.1f}/100)"
        elif overall_score >= 70:
            action = "STUDY"
            reward_delta = 2
            action_reason = f"Good performance, needs improvement ({overall_score:.1f}/100)"
        else:
            action = "RECYCLE"
            reward_delta = -3
            action_reason = f"Poor performance ({overall_score:.1f}/100), recommend recycling"
        
        # Update reward ledger
        current_reward = self.reward_ledger.get(agent_id, 0)
        self.reward_ledger[agent_id] = max(0, current_reward + reward_delta)
        
        # Log grading decision
        full_reasoning = reasoning or action_reason
        decision = self.middleware.record_brain_grade(
            agent_id=agent_id,
            score=overall_score,
            decision_type_str=action,
            reasoning=full_reasoning
        )
        
        decision.metadata = {
            'task_score': task_score,
            'behavior_score': behavior_score,
            'efficiency_score': efficiency_score,
            'overall_score': overall_score,
            'action': action,
            'reward_delta': reward_delta,
            'total_reward': self.reward_ledger[agent_id],
            'brain_id': self.id
        }
        
        grade_record = {
            'agent_id': agent_id,
            'graded_at': datetime.now().isoformat(),
            'scores': {
                'task': task_score,
                'behavior': behavior_score,
                'efficiency': efficiency_score,
                'overall': overall_score
            },
            'action': action,
            'reward_delta': reward_delta,
            'total_reward': self.reward_ledger[agent_id],
            'decision_id': decision.id
        }
        
        self.grade_history.append(grade_record)
        self._save_ledger()
        
        print(f"[BRAIN] ✅ Graded {agent_id}: {overall_score:.1f}/100 → {action} (+{reward_delta} reward)")
        
        return grade_record
    
    def promote_agent(self, agent_id: str) -> Dict[str, Any]:
        """Promote agent to higher tier"""
        if agent_id not in self.agent_credentials:
            return {'success': False, 'error': 'agent_not_found'}
        
        credential = self.agent_credentials[agent_id]
        new_tier = credential['tier'] + 1
        
        credential['tier'] = new_tier
        credential['promoted_at'] = datetime.now().isoformat()
        
        self._save_ledger()
        
        print(f"[BRAIN] 📈 Promoted {agent_id} to tier {new_tier}")
        
        return {
            'success': True,
            'agent_id': agent_id,
            'new_tier': new_tier,
            'updated_credential': credential
        }
    
    def recycle_agent(self, agent_id: str, reason: str = "") -> Dict[str, Any]:
        """Recycle (retire) underperforming agent"""
        if agent_id not in self.agent_credentials:
            return {'success': False, 'error': 'agent_not_found'}
        
        credential = self.agent_credentials[agent_id]
        credential['status'] = 'recycled'
        credential['recycled_at'] = datetime.now().isoformat()
        credential['recycle_reason'] = reason
        
        # Remove from reward ledger
        self.reward_ledger.pop(agent_id, None)
        
        self._save_ledger()
        
        print(f"[BRAIN] ♻️ Recycled {agent_id}: {reason}")
        
        return {
            'success': True,
            'agent_id': agent_id,
            'status': 'recycled',
            'reason': reason
        }
    
    def get_agent_credential(self, agent_id: str) -> Dict[str, Any]:
        """Retrieve agent credential"""
        return self.agent_credentials.get(agent_id, None)
    
    def get_reward_balance(self, agent_id: str) -> int:
        """Get current reward balance for agent"""
        return self.reward_ledger.get(agent_id, 0)
    
    def get_agent_grade_history(self, agent_id: str) -> List[Dict]:
        """Get all grades for an agent"""
        return [g for g in self.grade_history if g['agent_id'] == agent_id]
    
    def get_grading_summary(self) -> Dict[str, Any]:
        """Get grading statistics"""
        if not self.grade_history:
            return {
                'total_grades': 0,
                'promotions': 0,
                'study': 0,
                'recycled': 0
            }
        
        promotions = sum(1 for g in self.grade_history if g['action'] == 'PROMOTE')
        study = sum(1 for g in self.grade_history if g['action'] == 'STUDY')
        recycled = sum(1 for g in self.grade_history if g['action'] == 'RECYCLE')
        
        avg_score = sum(g['scores']['overall'] for g in self.grade_history) / len(self.grade_history)
        
        return {
            'total_grades': len(self.grade_history),
            'promotions': promotions,
            'study': study,
            'recycled': recycled,
            'average_score': avg_score,
            'promotion_rate': promotions / len(self.grade_history),
            'recent_grades': self.grade_history[-5:]
        }
    
    def get_decision_history(self) -> List[Dict]:
        """Get all brain decisions"""
        decisions = self.middleware.get_decisions_by_agent(self.id, limit=50)
        return [d.to_dict() for d in decisions]


# Global instance
_brain = None

def get_brain() -> ForestBrain:
    """Get or create global Brain instance"""
    global _brain
    if _brain is None:
        _brain = ForestBrain()
    return _brain


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("FOREST BRAIN (INTEGRATED) - VERIFICATION TEST")
    print("=" * 80)
    
    brain = get_brain()
    
    # Test 1: Issue credentials
    print("\n[TEST 1] Issuing agent credentials...")
    cred1 = brain.issue_credential("agent-001", tier=1, role="scanner")
    cred2 = brain.issue_credential("agent-002", tier=2, role="analyzer")
    print(f"  ✅ Issued {cred1['credential_id']}")
    print(f"  ✅ Issued {cred2['credential_id']}")
    
    # Test 2: Grade agents
    print("\n[TEST 2] Grading agent performance...")
    grade1 = brain.grade_agent("agent-001", task_score=88, behavior_score=85, efficiency_score=90)
    grade2 = brain.grade_agent("agent-002", task_score=60, behavior_score=55, efficiency_score=65)
    print(f"  ✅ Agent-001 graded: {grade1['scores']['overall']:.1f} → {grade1['action']}")
    print(f"  ✅ Agent-002 graded: {grade2['scores']['overall']:.1f} → {grade2['action']}")
    
    # Test 3: Reward tracking
    print("\n[TEST 3] Reward tracking...")
    reward1 = brain.get_reward_balance("agent-001")
    reward2 = brain.get_reward_balance("agent-002")
    print(f"  ✅ Agent-001 reward: {reward1}")
    print(f"  ✅ Agent-002 reward: {reward2}")
    
    # Test 4: Promote agent
    print("\n[TEST 4] Promoting agent...")
    promote_result = brain.promote_agent("agent-001")
    new_tier = promote_result['new_tier']
    print(f"  ✅ Agent-001 promoted to tier {new_tier}")
    
    # Test 5: Recycle agent
    print("\n[TEST 5] Recycling underperforming agent...")
    recycle_result = brain.recycle_agent("agent-002", reason="Performance below threshold")
    print(f"  ✅ Agent-002 recycled: {recycle_result['reason']}")
    
    # Test 6: Grading summary
    print("\n[TEST 6] Grading summary...")
    summary = brain.get_grading_summary()
    print(f"  ✅ Total grades: {summary['total_grades']}")
    print(f"  ✅ Promotions: {summary['promotions']}")
    print(f"  ✅ Study: {summary['study']}")
    print(f"  ✅ Recycled: {summary['recycled']}")
    print(f"  ✅ Average score: {summary['average_score']:.1f}")
    print(f"  ✅ Promotion rate: {summary['promotion_rate']:.1%}")
    
    # Test 7: Grade history
    print("\n[TEST 7] Agent grade history...")
    history = brain.get_agent_grade_history("agent-001")
    print(f"  ✅ Agent-001 grades: {len(history)}")
    for h in history:
        print(f"     - {h['action']}: {h['scores']['overall']:.1f}/100")
    
    print("\n" + "=" * 80)
    print("✅ FOREST BRAIN (INTEGRATED) READY")
    print("=" * 80 + "\n")
