#!/usr/bin/env python3
"""
🌲 Forest Network Dashboard v2.1-git — BlueAgent Powered
Live ARP table + quick host discovery with local Ollama analysis.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.blue_agent import BlueAgent
import subprocess
import re
from datetime import datetime

class NetworkDashboard(BlueAgent):
    def __init__(self):
        super().__init__(name="NetworkDashboard", model="llama3.2:3b", role="Network Visibility Agent")

    def run(self):
        if not self.credential:
            self.activate()

        print(f"🌲 Forest Network Dashboard v2.1-git @ {datetime.now()}")
        print("\n=== ARP Table (clean) ===")
        try:
            arp = subprocess.check_output(["arp", "-a"], text=True)
            for line in arp.splitlines():
                if '(' in line and not any(x in line.lower() for x in ["ff:ff", "224.0.0", "255.255"]):
                    print("   " + line.strip())
        except Exception as e:
            print(f"ARP error: {e}")

        print("\n=== Quick Live Host Check ===")
        print("Sending broadcast ping to wake devices...")
        try:
            subprocess.call(["ping", "-c", "2", "-W", "1", "192.168.68.255"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("Done. Run ARP Monitor again to see new devices.")
        except:
            pass

        print("\n✅ Network scan complete. All data stays local.")
        self.log_action("NETWORK_DASHBOARD_RUN", "Scan completed successfully")

if __name__ == "__main__":
    dashboard = NetworkDashboard()
    dashboard.run()
