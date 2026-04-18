#!/usr/bin/env python3
"""
🌲 Forest Firewall Harden v3.3-git — BlueAgent + Training Pipeline
Safe pf anchor method for macOS. Decepticon sandbox blocks active.
"""
import sys
import os
import subprocess
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.blue_agent import BlueAgent

class FirewallHardenAgent(BlueAgent):
    def __init__(self):
        super().__init__(name="FirewallHardenAgent", model="llama3.2:3b", role="Network Defense")

    def run(self):
        if not self.credential:
            self.activate()

        print(f"🌲 Forest Firewall Harden v3.3-git @ {datetime.now()}")
        print("Loading Decepticon-hardened rules into pf anchor 'forest/blue'")

        choice = input("\n⚠️ Type 'yes' to apply (anything else = abort): ").strip().lower()
        if choice != "yes":
            print("Aborted by user.")
            self.log_action("FIREWALL_ABORTED", "User veto")
            return

        rules = """# Forest Decepticon-Hardened Anchor v3.3
block drop out quick on en1 inet from 172.17.0.0/16 to any
block drop out quick on en1 inet from 172.18.0.0/16 to any
pass out all flags S/SA keep state
"""

        target = "/tmp/forest_anchor.conf"
        with open(target, "w") as f:
            f.write(rules)

        try:
            subprocess.run(["sudo", "pfctl", "-a", "forest/blue", "-f", target], check=True)
            print("✅ Decepticon-hardened anchor loaded successfully")
            print("   View:  sudo pfctl -a forest/blue -s rules")
            print("   Flush: sudo pfctl -a forest/blue -F rules")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to load anchor: {e}")
            self.log_action("FIREWALL_ANCHOR_FAILED", str(e))
            return

        self.log_action("FIREWALL_ANCHOR_LOADED", "Decepticon sandbox blocks active")
        print("\nTraining pipeline contribution: Outbound from Docker/sandbox ranges blocked.")

if __name__ == "__main__":
    agent = FirewallHardenAgent()
    agent.run()
