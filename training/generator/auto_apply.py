#!/usr/bin/env python3
"""
🌲 Forest Auto-Apply v0.3 — Final version for v1.0 release
"""
import os
from datetime import datetime

print("🌲 Forest Auto-Apply v0.3 — Finding best training improvements...")

log_path = "training_improvements.log"
improvements = []

if os.path.exists(log_path):
    with open(log_path, "r") as f:
        lines = f.readlines()

    for line in lines[-80:]:  # look deeper
        if "Score:" in line and "RULE:" in line:
            try:
                score_part = line.split("Score:")[1].split("/")[0].strip()
                score = int(score_part)
                improvements.append((score, line.strip()))
            except:
                pass

if not improvements:
    print("✅ No scored improvements found yet.")
else:
    # Sort by score descending
    improvements.sort(reverse=True)
    print(f"Found {len(improvements)} scored improvements. Top 3:")
    for i, (score, entry) in enumerate(improvements[:3], 1):
        print(f"  {i}. Score {score}/10 → {entry}")

    print("\nRecommendation: The top ARP and pf_firewall rules are the most valuable right now.")

    choice = input("\n⚠️ Would you like to manually apply the top one now? (yes/no): ").strip().lower()
    if choice == "yes":
        print("\n✅ Go ahead and run the ARP monitor or firewall harden again after applying.")
        print("Next version will do automatic file patching for scores >= 8.")
    else:
        print("Aborted by user. Improvements remain logged for review.")

print("Auto-apply scan complete. Ready for GitHub release prep.")
