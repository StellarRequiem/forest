#!/usr/bin/env python3
"""
Forest Rebuilt Network Monitor
Purpose: Watch for suspicious ARP changes and duplicate MACs
"""
import subprocess
import re
from datetime import datetime

def monitor_arp():
    print(f"🌲 Forest ARP Monitor started at {datetime.now()}")
    try:
        arp = subprocess.check_output(["arp", "-a"], text=True)
        mac_to_ips = {}
        for line in arp.splitlines():
            match = re.search(r'\(([\d.]+)\) at ([0-9a-f:]+)', line, re.IGNORECASE)
            if match:
                ip, mac = match.group(1), match.group(2).lower()
                if not mac.startswith(("ff:", "01:", "33:")):
                    mac_to_ips.setdefault(mac, []).append(ip)
        
        for mac, ips in mac_to_ips.items():
            unique = list(dict.fromkeys(ips))
            if len(unique) > 2:
                print(f"⚠️ ALERT: MAC {mac} seen on {len(unique)} IPs → {unique}")
            else:
                print(f"✅ {mac} → {unique[0]}")
    except Exception as e:
        print(f"Monitor error: {e}")

if __name__ == "__main__":
    monitor_arp()
