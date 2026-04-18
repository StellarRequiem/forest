#!/usr/bin/env python3
"""
🌲 Forest Privacy Hosts Updater v2.1-git — BlueAgent Powered
Human-gated, credentialed, uses StevenBlack blocklist.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.blue_agent import BlueAgent
import requests
from datetime import datetime
import shutil
import sys

class PrivacyHostsAgent(BlueAgent):
    def __init__(self):
        super().__init__(name="PrivacyHostsAgent", model="llama3.2:3b", role="Privacy & Hosts Defense")

    def run(self):
        if not self.credential:
            self.activate()

        print(f"🌲 Forest Privacy Hosts Updater v2.1-git @ {datetime.now()}")
        print("This tool will replace your /etc/hosts with StevenBlack's strong blocklist.")

        choice = input("\n⚠️ Type 'yes' to continue (anything else = abort): ").strip().lower()
        if choice != "yes":
            print("Aborted by user.")
            self.log_action("PRIVACY_HOSTS_ABORTED", "User veto")
            return

        try:
            r = requests.get("https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts", timeout=30)
            if r.status_code != 200:
                print("❌ Failed to download blocklist.")
                return

            backup_path = f"/tmp/hosts_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            if os.path.exists("/etc/hosts"):
                shutil.copy2("/etc/hosts", backup_path)
                print(f"✅ Backed up current /etc/hosts to {backup_path}")

            target = "/tmp/forest_privacy_hosts"
            with open(target, "w") as f:
                f.write(r.text)

            print(f"✅ New hosts file ready ({len(r.text.splitlines())} lines) → {target}")
            print("\nTo apply (requires sudo):")
            print(f"   sudo cp {target} /etc/hosts")
            print("   sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder")
            print("\nForest will NOT run sudo for you.")

            self.log_action("PRIVACY_HOSTS_PREPARED", f"Blocklist size: {len(r.text.splitlines())} lines")
        except Exception as e:
            print(f"❌ Update failed: {e}")
            self.log_action("PRIVACY_HOSTS_ERROR", str(e))

if __name__ == "__main__":
    agent = PrivacyHostsAgent()
    agent.run()
