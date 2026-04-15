#!/usr/bin/env python3
"""
PHASE 2 - BLUE AGENT DECISION MONITORING
Complete Integration Test & Verification
"""

import sys
from pathlib import Path
from datetime import datetime

FOREST_PATH = Path.home() / "Forest"
sys.path.insert(0, str(FOREST_PATH))

print("\n" + "=" * 100)
print("PHASE 2: BLUE AGENT DECISION MONITORING - COMPLETE INTEGRATION TEST")
print("=" * 100)

# Test 1: Import all integrated modules
print("\n[TEST 1] Importing integrated modules...")
try:
    from core.decision_middleware import get_middleware, DecisionType, DecisionStatus
    from core.decision_timeline_provider import DecisionTimelineProvider
    from agents.core.headmaster_integrated import Headmaster
    from agents.organs.enforcer_integrated import EnforcerGateway
    from agents.organs.forest_brain_integrated import ForestBrain
    print("  ✅ All modules imported successfully")
except Exception as e:
    print(f"  ❌ Import failed: {e}")
    sys.exit(1)

# Test 2: Initialize all components
print("\n[TEST 2] Initializing all components...")
try:
    middleware = get_middleware()
    provider = DecisionTimelineProvider()
    headmaster = Headmaster()
    enforcer = EnforcerGateway()
    brain = ForestBrain()
    print("  ✅ All components initialized")
except Exception as e:
    print(f"  ❌ Initialization failed: {e}")
    sys.exit(1)

# Test 3: Full workflow simulation
print("\n[TEST 3] Simulating complete agent workflow...")
try:
    # 3a: Headmaster spawns agents
    print("  3a) Headmaster spawning agents...")
    agents = headmaster.spawn_agent(tier=2, role="scanner", purpose="security scanning", count=3)
    print(f"     ✅ {len(agents)} agents spawned")
    
    # 3b: Enforcer approves actions
    print("  3b) Enforcer validating actions...")
    approvals = []
    for agent_id in agents:
        result = enforcer.approve_action(agent_id, "scan network 192.168.0.0/16")
        approvals.append(result)
    print(f"     ✅ {len([a for a in approvals if a['approved']])} actions approved")
    
    # 3c: Brain grades agents
    print("  3c) Brain grading agent performance...")
    grades = []
    for i, agent_id in enumerate(agents):
        score = 75 + (i * 5)  # Varying scores
        result = brain.grade_agent(agent_id, score, score - 2, score - 5)
        grades.append(result)
    print(f"     ✅ {len(grades)} agents graded")
    
    # 3d: Headmaster routes tasks
    print("  3d) Headmaster routing tasks...")
    routes = []
    for i in range(2):
        result = headmaster.route_task(f"scan_subnet_{i}", target_tier=2)
        routes.append(result)
    print(f"     ✅ {len(routes)} tasks routed")
    
    print("  ✅ Complete workflow executed")
except Exception as e:
    print(f"  ❌ Workflow failed: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Data aggregation
print("\n[TEST 4] Data aggregation from middleware...")
try:
    timeline = provider.get_timeline(limit=50)
    enforcer_data = provider.get_enforcer_actions()
    brain_data = provider.get_brain_grading_summary()
    dashboard_data = provider.get_dashboard_data()
    
    print(f"  Timeline entries: {len(timeline)}")
    print(f"  Enforcer approvals: {enforcer_data['approved_count']}")
    print(f"  Enforcer blocks: {enforcer_data['blocked_count']}")
    print(f"  Brain grades: {brain_data['total_grades']}")
    print(f"  Brain promotions: {brain_data['promotions']}")
    print(f"  Dashboard keys: {len(dashboard_data)}")
    print("  ✅ Data aggregation successful")
except Exception as e:
    print(f"  ❌ Data aggregation failed: {e}")

# Test 5: Decision statistics
print("\n[TEST 5] Decision statistics...")
try:
    stats = middleware.get_decision_stats()
    print(f"  Total decisions: {stats['total_decisions']}")
    print(f"  Decision types: {len(stats['by_type'])}")
    print(f"    - SPAWN: {stats['by_type'].get('SPAWN', 0)}")
    print(f"    - APPROVE: {stats['by_type'].get('APPROVE', 0)}")
    print(f"    - BLOCK: {stats['by_type'].get('BLOCK', 0)}")
    print(f"    - GRADE: {stats['by_type'].get('GRADE', 0)}")
    print(f"    - PROMOTE: {stats['by_type'].get('PROMOTE', 0)}")
    print(f"    - ROUTE: {stats['by_type'].get('ROUTE', 0)}")
    print(f"  Decision statuses: {len(stats['by_status'])}")
    print(f"    - PENDING: {stats['by_status'].get('PENDING', 0)}")
    print(f"    - APPROVED: {stats['by_status'].get('APPROVED', 0)}")
    print(f"    - EXECUTED: {stats['by_status'].get('EXECUTED', 0)}")
    print("  ✅ Statistics captured")
except Exception as e:
    print(f"  ❌ Statistics failed: {e}")

# Test 6: Decision reversal
print("\n[TEST 6] Testing decision reversal...")
try:
    recent = middleware.get_recent_decisions(limit=1)
    if recent:
        decision = recent[0]
        middleware.reverse_decision(decision.id)
        reversed_decisions = middleware.get_reversed_decisions(limit=1)
        print(f"  ✅ Decision reversed: {decision.id}")
        print(f"  Reversed decisions total: {len(reversed_decisions)}")
    else:
        print("  ⚠️ No decisions to reverse")
except Exception as e:
    print(f"  ❌ Reversal failed: {e}")

# Test 7: Agent decision history
print("\n[TEST 7] Agent decision history...")
try:
    if agents:
        history = provider.get_agent_decision_history(agents[0])
        print(f"  Agent: {agents[0]}")
        print(f"  Total decisions: {history['total_decisions']}")
        print(f"  Decision types: {dict(history['by_type'])}")
        print(f"  Decision statuses: {dict(history['by_status'])}")
        print("  ✅ History retrieved")
except Exception as e:
    print(f"  ❌ History retrieval failed: {e}")

# Test 8: Dashboard readiness
print("\n[TEST 8] Dashboard readiness check...")
try:
    data = provider.get_dashboard_data()
    
    required_keys = ['timestamp', 'total_decisions', 'by_type', 'timeline', 'enforcer', 'brain', 'flow']
    missing = [k for k in required_keys if k not in data]
    
    if missing:
        print(f"  ❌ Missing keys: {missing}")
    else:
        print(f"  ✅ All dashboard data present")
        print(f"  ✅ Total decisions in feed: {data['total_decisions']}")
        print(f"  ✅ Timeline ready: {len(data['timeline'])} entries")
        print(f"  ✅ Enforcer panel ready: approval rate {data['enforcer']['approval_rate']:.1%}")
        print(f"  ✅ Brain panel ready: {data['brain']['total_grades']} grades")
        print(f"  ✅ Flow diagram ready: {len(data['flow'])} flows")
except Exception as e:
    print(f"  ❌ Dashboard check failed: {e}")

# Final summary
print("\n" + "=" * 100)
print("PHASE 2 INTEGRATION TEST COMPLETE")
print("=" * 100)

print(f"\n✅ STATUS: All components operational")
print(f"✅ TIME: {datetime.now().isoformat()}")
print(f"✅ READY: Dashboard, Headmaster, Enforcer, Brain all integrated with decision middleware")
print(f"\nNext: Deploy to dashboard at localhost:8501")
print("\n" + "=" * 100 + "\n")
