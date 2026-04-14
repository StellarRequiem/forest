#!/usr/bin/env python3
"""
🌲 Forest Network Dashboard v1
Quick overview of ARP + basic live hosts
"""
import subprocess
import re
from datetime import datetime

def network_dashboard():
    print(f"🌲 Forest Network Dashboard @ {datetime.now()}")
    print("\n=== ARP Table (clean) ===")
    try:
        arp = subprocess.check_output(["arp", "-a"], text=True)
        for line in arp.splitlines():
            if '(' in line and not any(x in line.lower() for x in ["ff:ff", "224.0.0", "255.255"]):
                print("   " + line.strip())
    except Exception as e:
        print(f"ARP error: {e}")
    
    print("\n=== Quick Live Host Check ===")
    try:
        print("Sending broadcast ping to wake devices...")
        subprocess.call(["ping", "-c", "2", "-W", "1", "192.168.68.255"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("Done. Run ARP monitor again to see new devices.")
    except:
        pass

if __name__ == "__main__":
    network_dashboard()
