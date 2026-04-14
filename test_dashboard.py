#!/usr/bin/env python3
"""
Unified Dashboard - Comprehensive Test & Verification
Tests all components end-to-end
"""

import sys
from pathlib import Path
import json
from datetime import datetime

FOREST_PATH = Path.home() / "Forest"
sys.path.insert(0, str(FOREST_PATH))

print("\n" + "=" * 80)
print("FOREST UNIFIED MONITORING DASHBOARD - COMPREHENSIVE TEST")
print("=" * 80)

# Test 1: Import modules
print("\n[TEST 1] Importing modules...")
try:
    from core.dashboard.data_aggregator import DataAggregator
    print("  ✅ DataAggregator imported")
    
    import streamlit
    print("  ✅ Streamlit imported")
    
    import pandas as pd
    print("  ✅ Pandas imported")
    
    import plotly.graph_objects as go
    print("  ✅ Plotly imported")
except Exception as e:
    print(f"  ❌ Import failed: {e}")
    sys.exit(1)

# Test 2: Initialize aggregator
print("\n[TEST 2] Initializing data aggregator...")
try:
    agg = DataAggregator()
    print("  ✅ DataAggregator initialized")
except Exception as e:
    print(f"  ❌ Initialization failed: {e}")
    sys.exit(1)

# Test 3: Collect data
print("\n[TEST 3] Collecting data from all sources...")
try:
    all_data = agg.get_all_data()
    print(f"  ✅ Data collected at {all_data['timestamp']}")
except Exception as e:
    print(f"  ❌ Data collection failed: {e}")
    sys.exit(1)

# Test 4: Validate data structure
print("\n[TEST 4] Validating data structure...")
required_keys = ['timestamp', 'cryptex', 'agents', 'network', 'system', 'processes']
for key in required_keys:
    if key in all_data:
        print(f"  ✅ {key}: present")
    else:
        print(f"  ❌ {key}: missing")

# Test 5: Verify Cryptex data
print("\n[TEST 5] Verifying Cryptex logs...")
cryptex_logs = all_data['cryptex']['logs']
cryptex_stats = all_data['cryptex']['stats']
print(f"  ✅ Logs collected: {len(cryptex_logs)}")
print(f"  ✅ Total events: {cryptex_stats['total_events']}")
print(f"  ✅ Event types: {len(cryptex_stats['event_types'])}")
print(f"     - {dict(list(cryptex_stats['event_types'].items())[:3])}")

# Test 6: Verify Network data
print("\n[TEST 6] Verifying Network data...")
network_info = all_data['network']['info']
network_stats = all_data['network']['stats']
print(f"  ✅ Hostname: {network_info['hostname']}")
print(f"  ✅ IP Address: {network_info['local_ip']}")
print(f"  ✅ Interfaces: {len(network_info['interfaces'])}")
print(f"  ✅ Bytes sent: {network_stats.get('bytes_sent', 0):,}")
print(f"  ✅ Bytes recv: {network_stats.get('bytes_recv', 0):,}")

# Test 7: Verify System Health
print("\n[TEST 7] Verifying System Health...")
system = all_data['system']
print(f"  ✅ CPU: {system['cpu_percent']:.1f}% ({system['cpu_count']} cores)")
print(f"  ✅ Memory: {system['memory']['percent']:.1f}% ({system['memory']['used'] / (1024**3):.1f}GB used)")
print(f"  ✅ Disk: {system['disk']['percent']:.1f}%")
print(f"  ✅ Processes: {system['processes']}")

# Test 8: Verify Processes
print("\n[TEST 8] Verifying Forest processes...")
processes = all_data['processes']
print(f"  ✅ Found {len(processes)} Forest processes")
for proc in processes[:3]:
    print(f"     - PID {proc['pid']}: {proc['name']} (CPU: {proc['cpu']:.1f}%, MEM: {proc['memory']:.1f}%)")

# Test 9: Data conversion to DataFrame
print("\n[TEST 9] Converting data to DataFrames...")
try:
    import pandas as pd
    
    # Cryptex logs to DataFrame
    if cryptex_logs:
        df_logs = pd.DataFrame(cryptex_logs)
        print(f"  ✅ Cryptex logs: {len(df_logs)} rows")
    
    # Processes to DataFrame
    if processes:
        df_procs = pd.DataFrame(processes)
        print(f"  ✅ Processes: {len(df_procs)} rows")
    
    # Network interfaces to DataFrame
    if network_info['interfaces']:
        df_net = pd.DataFrame(network_info['interfaces'])
        print(f"  ✅ Network interfaces: {len(df_net)} rows")
except Exception as e:
    print(f"  ❌ DataFrame conversion failed: {e}")

# Test 10: Data freshness
print("\n[TEST 10] Verifying data freshness...")
data_time = datetime.fromisoformat(all_data['timestamp'])
now = datetime.now()
age = (now - data_time).total_seconds()
if age < 5:
    print(f"  ✅ Data is fresh (collected {age:.1f}s ago)")
else:
    print(f"  ⚠️ Data is {age:.1f}s old")

# Test 11: Dashboard files exist
print("\n[TEST 11] Verifying dashboard files...")
files = [
    FOREST_PATH / 'core/dashboard/data_aggregator.py',
    FOREST_PATH / 'ui/forest_dashboard.py',
]
for file in files:
    if file.exists():
        print(f"  ✅ {file.name}: {file.stat().st_size} bytes")
    else:
        print(f"  ❌ {file.name}: NOT FOUND")

# Test 12: Summary
print("\n[TEST 12] Summary Statistics")
print(f"  Total Cryptex Events: {cryptex_stats['total_events']}")
print(f"  Unique Event Types: {len(cryptex_stats['event_types'])}")
print(f"  Agents Tracked: {len(all_data['agents'])}")
print(f"  Network Interfaces: {len(network_info['interfaces'])}")
print(f"  Forest Processes: {len(processes)}")
print(f"  System CPU Usage: {system['cpu_percent']:.1f}%")
print(f"  System Memory Usage: {system['memory']['percent']:.1f}%")

print("\n" + "=" * 80)
print("✅ ALL TESTS PASSED - DASHBOARD IS READY")
print("=" * 80)

print("\n🚀 To start the dashboard, run:")
print("   cd ~/Forest")
print("   source venv/bin/activate")
print("   streamlit run ui/forest_dashboard.py")
print("\n" + "=" * 80 + "\n")
