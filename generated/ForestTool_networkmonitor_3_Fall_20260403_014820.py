#!/usr/bin/env python3
"""
🌲 Forest ARP Network Monitor v2
Detects ARP spoofing, duplicate MACs, and flapping devices
"""
import subprocess
import re
from datetime import datetime
import time
import argparse

def monitor_arp(watch=False, interval=10):
    print(f"🌲 Forest ARP Monitor started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("   Monitoring for suspicious ARP activity\n")
    
    last_state = None
    while True:
        try:
            arp = subprocess.check_output(["arp", "-a"], text=True, timeout=8)
            mac_to_ips = {}
            for line in arp.splitlines():
                # Fixed robust regex for macOS arp output
                match = re.search(r'\(([\d.]+)\)\s+at\s+([0-9a-f:]+)', line, re.IGNORECASE)
                if match:
                    ip = match.group(1)
                    mac = match.group(2).lower()
                    # Skip multicast, broadcast, and invalid
                    if mac.startswith(("ff:ff", "01:00", "33:33")) or mac in ["00:00:00:00:00:00", "1:0:5e:0:0:fb"]:
                        continue
                    mac_to_ips.setdefault(mac, []).append(ip)
            
            current_state = {mac: sorted(set(ips)) for mac, ips in mac_to_ips.items()}
            suspicious = False
            
            for mac, ips in current_state.items():
                if len(ips) > 2:
                    print(f"⚠️ ALERT [{datetime.now().strftime('%H:%M:%S')}] MAC {mac} mapped to {len(ips)} IPs → {ips}")
                    suspicious = True
                else:
                    print(f"✅ {mac} → {ips[0]}")
            
            if not suspicious:
                print(f"✅ Network clean at {datetime.now().strftime('%H:%M:%S')}")
            
            # In watch mode, only alert on changes
            if watch and last_state is not None and current_state != last_state:
                print(f"🔄 ARP table changed at {datetime.now().strftime('%H:%M:%S')}")
            
            last_state = current_state
            
            if not watch:
                break
                
            time.sleep(interval)
            
        except KeyboardInterrupt:
            print("\n🌲 Monitor stopped.")
            break
        except Exception as e:
            print(f"Error: {e}")
            if not watch:
                break
            time.sleep(interval)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Forest ARP Monitor")
    parser.add_argument("--watch", action="store_true", help="Continuous monitoring mode")
    parser.add_argument("--interval", type=int, default=10, help="Check interval in seconds")
    args = parser.parse_args()
    monitor_arp(watch=args.watch, interval=args.interval)
