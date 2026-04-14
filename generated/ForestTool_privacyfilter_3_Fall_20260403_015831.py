#!/usr/bin/env python3
"""
🌲 Forest Privacy Hosts Updater v1
Downloads StevenBlack hosts list (strong ad/tracker/malware blocking)
"""
import requests
from datetime import datetime
import shutil
import os

def update_privacy_hosts():
    print(f"🌲 Forest Privacy Hosts Updater started at {datetime.now()}")
    try:
        r = requests.get("https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts", timeout=30)
        if r.status_code == 200:
            backup_path = f"/tmp/hosts_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            if os.path.exists("/etc/hosts"):
                shutil.copy2("/etc/hosts", backup_path)
                print(f"✅ Backed up current /etc/hosts to {backup_path}")
            
            target = "/tmp/forest_privacy_hosts"
            with open(target, "w") as f:
                f.write(r.text)
            print(f"✅ New hosts file saved ({len(r.text.splitlines())} lines) → {target}")
            print("   Review the file, then apply with:")
            print("   sudo cp /tmp/forest_privacy_hosts /etc/hosts")
            print("   Flush DNS: sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder")
    except Exception as e:
        print(f"Update failed: {e}")

if __name__ == "__main__":
    update_privacy_hosts()
