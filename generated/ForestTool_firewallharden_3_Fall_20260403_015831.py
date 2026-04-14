#!/usr/bin/env python3
"""
🌲 Forest macOS pf Firewall Quick Harden v1
"""
import subprocess
from datetime import datetime

def harden_firewall():
    print(f"🌲 Forest Firewall Harden started at {datetime.now()}")
    rules = """# Forest-generated pf rules for home use
block in all
pass in on lo0
pass out all keep state
pass in inet proto tcp from any to any port {22, 80, 443, 11434} keep state  # SSH, HTTP/S, Ollama
pass in inet proto udp from any to any port 5353 keep state  # mDNS if needed
    """
    path = "/tmp/forest_pf_rules.conf"
    with open(path, "w") as f:
        f.write(rules)
    print(f"✅ Safe pf rules written to {path}")
    print("   To review: cat /tmp/forest_pf_rules.conf")
    print("   Load:      sudo pfctl -f /tmp/forest_pf_rules.conf")
    print("   Enable:    sudo pfctl -e")
    print("   Status:    sudo pfctl -s info")

if __name__ == "__main__":
    harden_firewall()
