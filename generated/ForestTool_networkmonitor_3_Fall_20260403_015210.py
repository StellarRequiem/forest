#!/usr/bin/env python3
"""
🌲 Forest ARP Network Monitor v4
Quiet, clean, no more SyntaxWarnings
"""
import subprocess
import re
from datetime import datetime
import time
import argparse

def monitor_arp(watch=False, interval=10):
    print(f"🌲 Forest ARP Monitor v4 started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("   Quiet mode — alerts only on suspicious activity\n")
    
    last_state = None
    while True:
        try:
            arp = subprocess.check_output(["arp", "-a"], text=True, timeout=8)
            mac_to_ips = {}
            for line in arp.splitlines():
                # Proper raw regex - no escape warning
                match = re.search(r'\(([\d.]+)\) at ([0-9a-f:]+)', line, re.IGNORECASE)
                if match:
                    ip = match.group(1)
                    mac = match.group(2).lower()
                    if mac.startswith(("ff:ff", "01:00", "33:33")) or mac in ["00:00:00:00:00:00", "1:0:5e:0:0:fb"]:
                        continue
                    mac_to_ips.setdefault(mac, []).append(ip)
            
            current_state = {mac: tuple(sorted(set(ips))) for mac, ips in mac_to_ips.items()}
            
            alerts = []
            for mac, ips in current_state.items():
                if len(ips) > 2:
                    alerts.append(f"⚠️ MAC {mac} → {len(ips)} IPs: {ips}")
            
            if alerts:
                for alert in alerts:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] {alert}")
            else:
                print(f"✅ Clean at {datetime.now().strftime('%H:%M:%S')}")
            
            if watch and last_state is not None and current_state != last_state:
                print(f"🔄 ARP table changed at {datetime.now().strftime('%H:%M:%S')}")
            
            last_state = current_state.copy()
            
            if not watch:
                break
            time.sleep(interval)
            
        except KeyboardInterrupt:
            print("\n🌲 Monitor stopped by user.")
            break
        except Exception as e:
            print(f"Error: {e}")
            if not watch:
                break
            time.sleep(interval)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Forest ARP Monitor v4")
    parser.add_argument("--watch", action="store_true", help="Continuous monitoring")
    parser.add_argument("--interval", type=int, default=10, help="Seconds between checks")
    args = parser.parse_args()
    monitor_arp(watch=args.watch, interval=args.interval)
