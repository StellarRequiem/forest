#!/usr/bin/env python3
"""
🌲 Forest Swarm Entrypoint - Simplified
Starts all components: Orchestrator, Watchers, Firewall, Response Engine
"""
import sys
import os

# Force unbuffered  
os.environ['PYTHONUNBUFFERED'] = '1'

print('🌲 Forest Blue-Team Guardian - Starting Orchestrated Swarm', flush=True)
print('⏱️  Initializing...', flush=True)

sys.path.insert(0, '/forest')

# Import and start
try:
    import time
    import subprocess
    from core.swarm_orchestrator import AgentSwarmOrchestrator
    from core.watchers import start_all_watchers
    from core.dynamic_firewall import start_dynamic_firewall
    from core.incident_response import start_incident_response_engine
    import threading
    
    print('[Init] Imports successful', flush=True)
    
    # Start watchers
    print('[Startup] Starting watchers...', flush=True)
    watchers_thread = threading.Thread(target=start_all_watchers, daemon=True)
    watchers_thread.start()
    print('✅ Watchers started', flush=True)
    
    # Start firewall
    print('[Startup] Starting firewall...', flush=True)
    firewall_thread = threading.Thread(target=start_dynamic_firewall, daemon=True)
    firewall_thread.start()
    print('✅ Firewall started', flush=True)
    
    # Start engine
    print('[Startup] Starting incident response engine...', flush=True)
    engine_thread = threading.Thread(target=start_incident_response_engine, daemon=True)
    engine_thread.start()
    print('✅ Incident Response Engine started', flush=True)
    
    print('\n🌲 Forest Swarm ONLINE\n', flush=True)
    
    # Keep alive
    while True:
        time.sleep(60)
        print('[Swarm] Running...', flush=True)

except KeyboardInterrupt:
    print('\n🛑 Shutdown', flush=True)
    sys.exit(0)
except Exception as e:
    print(f'❌ Error: {e}', flush=True)
    import traceback
    traceback.print_exc()
    time.sleep(10)
    sys.exit(1)
