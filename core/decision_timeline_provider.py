#!/usr/bin/env python3
"""
Decision Timeline Data Provider
Feeds decision data to dashboard visualization
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

FOREST_PATH = Path.home() / "Forest"
sys.path.insert(0, str(FOREST_PATH))

from core.decision_middleware import get_middleware, DecisionStatus, DecisionType

class DecisionTimelineProvider:
    """Provides timeline data for dashboard visualization"""
    
    def __init__(self):
        self.middleware = get_middleware()
    
    def get_timeline(self, hours: int = 24, limit: int = 100) -> list:
        """Get decision timeline for specified hours"""
        
        decisions = self.middleware.get_recent_decisions(limit=limit)
        
        timeline = []
        for d in decisions:
            timeline.append({
                'timestamp': d.created_at,
                'decision_id': d.id,
                'type': d.decision_type.value,
                'agent_id': d.agent_id,
                'action': d.action[:50],
                'reasoning': d.reasoning[:100],
                'status': d.status.value,
                'hash': d.hash,
            })
        
        return sorted(timeline, key=lambda x: x['timestamp'])
    
    def get_decision_flow(self) -> dict:
        """Get decision flow data (Sankey diagram)"""
        
        stats = self.middleware.get_decision_stats()
        
        # Decision type flows
        flows = []
        
        # Agent → Decision Type
        for agent_id, count in list(stats.get('by_agent', {}).items())[:10]:
            flows.append({
                'source': agent_id,
                'target': 'Decision Gate',
                'value': count
            })
        
        # Decision Type → Status
        for dtype, count in stats.get('by_type', {}).items():
            flows.append({
                'source': 'Decision Gate',
                'target': dtype,
                'value': count
            })
        
        # Type → Status
        for status, count in stats.get('by_status', {}).items():
            flows.append({
                'source': 'Decision Gate',
                'target': status,
                'value': count
            })
        
        return flows
    
    def get_agent_decision_history(self, agent_id: str) -> dict:
        """Get complete decision history for an agent"""
        
        decisions = self.middleware.get_decisions_by_agent(agent_id, limit=50)
        
        history = {
            'agent_id': agent_id,
            'total_decisions': len(decisions),
            'by_type': defaultdict(int),
            'by_status': defaultdict(int),
            'timeline': []
        }
        
        for d in decisions:
            history['by_type'][d.decision_type.value] += 1
            history['by_status'][d.status.value] += 1
            history['timeline'].append({
                'timestamp': d.created_at,
                'type': d.decision_type.value,
                'status': d.status.value,
                'action': d.action[:50],
                'hash': d.hash
            })
        
        return history
    
    def get_enforcer_actions(self) -> dict:
        """Get enforcer gate actions (approvals vs blocks)"""
        
        blocked = self.middleware.get_blocked_decisions(limit=100)
        approved = self.middleware.get_decisions_by_type(DecisionType.APPROVE, limit=100)
        
        return {
            'approved_count': len(approved),
            'blocked_count': len(blocked),
            'approval_rate': len(approved) / (len(approved) + len(blocked)) if (len(approved) + len(blocked)) > 0 else 0,
            'recent_blocks': [
                {
                    'agent_id': d.agent_id,
                    'action': d.action[:50],
                    'timestamp': d.created_at,
                    'hash': d.hash
                }
                for d in blocked[:5]
            ]
        }
    
    def get_brain_grading_summary(self) -> dict:
        """Get Forest Brain grading summary"""
        
        grades = self.middleware.get_decisions_by_type(DecisionType.GRADE, limit=100)
        
        promotions = sum(1 for d in grades if 'PROMOTE' in d.reasoning.upper())
        study = sum(1 for d in grades if 'STUDY' in d.reasoning.upper())
        recycled = sum(1 for d in grades if 'RECYCLE' in d.reasoning.upper())
        
        return {
            'total_grades': len(grades),
            'promotions': promotions,
            'study': study,
            'recycled': recycled,
            'promotion_rate': promotions / len(grades) if len(grades) > 0 else 0,
            'recent_grades': [
                {
                    'agent_id': d.agent_id,
                    'reasoning': d.reasoning[:80],
                    'timestamp': d.created_at,
                    'status': d.status.value
                }
                for d in grades[:5]
            ]
        }
    
    def get_dashboard_data(self) -> dict:
        """Get all dashboard data in one call"""
        
        stats = self.middleware.get_decision_stats()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_decisions': stats['total_decisions'],
            'by_type': stats['by_type'],
            'by_status': stats['by_status'],
            'timeline': self.get_timeline(limit=50),
            'enforcer': self.get_enforcer_actions(),
            'brain': self.get_brain_grading_summary(),
            'flow': self.get_decision_flow(),
        }


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("DECISION TIMELINE PROVIDER - DATA VERIFICATION")
    print("=" * 80)
    
    provider = DecisionTimelineProvider()
    
    # Test 1: Timeline
    print("\n[TEST 1] Decision timeline...")
    timeline = provider.get_timeline(limit=10)
    print(f"  Total decisions: {len(timeline)}")
    for t in timeline[-3:]:
        print(f"    - {t['timestamp']}: {t['type']} ({t['agent_id']})")
    
    # Test 2: Enforcer summary
    print("\n[TEST 2] Enforcer actions...")
    enforcer = provider.get_enforcer_actions()
    print(f"  Approved: {enforcer['approved_count']}")
    print(f"  Blocked: {enforcer['blocked_count']}")
    print(f"  Approval rate: {enforcer['approval_rate']:.1%}")
    
    # Test 3: Brain summary
    print("\n[TEST 3] Brain grading...")
    brain = provider.get_brain_grading_summary()
    print(f"  Total grades: {brain['total_grades']}")
    print(f"  Promotions: {brain['promotions']}")
    print(f"  Study: {brain['study']}")
    print(f"  Recycled: {brain['recycled']}")
    
    # Test 4: Full dashboard data
    print("\n[TEST 4] Dashboard data...")
    data = provider.get_dashboard_data()
    print(f"  Total decisions: {data['total_decisions']}")
    print(f"  Timeline entries: {len(data['timeline'])}")
    print(f"  Flow entries: {len(data['flow'])}")
    print(f"  Data keys: {list(data.keys())}")
    
    print("\n" + "=" * 80)
    print("✅ DECISION TIMELINE PROVIDER READY")
    print("=" * 80 + "\n")
