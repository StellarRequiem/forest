#!/usr/bin/env python3
"""
🌲 Forest ARP Monitor v3.0-git — BlueAgent + Training Pipeline
Applied high-scoring improvement: ARP anomaly detection for Decepticon recon.
"""
import sys
import os
import subprocess
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.blue_agent import BlueAgent

class ARPMonitorAgent(BlueAgent):
    def __init__(self):
        super().__init__(name="ARPMonitorAgent", model="llama3.2:3b", role="Network Recon Defense")

    def run(self):
        if not self.credential:
            self.activate()

        print(f"🌲 Forest ARP Monitor v3.0-git @ {datetime.now()}")
        print("Scanning ARP table for Decepticon-style recon + anomalies...")

        try:
            result = subprocess.check_output(["arp", "-a"], text=True)
            lines = result.strip().split('\n')

            suspicious = []
            decepticon_related = []
            for line in lines:
                lower_line = line.lower()
                if any(x in lower_line for x in ['172.17', '172.18', 'decepticon', 'sandbox']):
                    decepticon_related.append(line)
                # Basic anomaly: unknown MACs or rapid changes could be flagged here later

            print(f"Found {len(lines)} ARP entries.")
            print(f"  → {len(decepticon_related)} Decepticon/sandbox related.")

            if decepticon_related:
                print("⚠️  Decepticon-related ARP entries detected:")
                for s in decepticon_related:
                    print(f"   {s}")
                self.log_action("ARP_DECEPTICON_DETECTED", f"Found {len(decepticon_related)} suspicious entries")
            else:
                print("✅ No Decepticon ARP activity detected.")
                self.log_action("ARP_SCAN_COMPLETE", "Clean scan - no sandbox recon")

        except Exception as e:
            print(f"Error running arp: {e}")
            self.log_action("ARP_ERROR", str(e))

if __name__ == "__main__":
    agent = ARPMonitorAgent()
    agent.run()
