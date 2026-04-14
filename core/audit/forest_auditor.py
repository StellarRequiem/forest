#!/usr/bin/env python3
"""
Forest Lvl1Worker — ForestAuditor v1.2
Daily incremental + weekly deep + monthly compile/compare (background safe)
"""

from agents.core.lvl1_worker import Lvl1Worker
from agents.organs.forest_brain import log_chain
from agents.organs.enforcer import enforcer
import ollama
import json
from pathlib import Path
from datetime import datetime, timedelta

VAULT = Path.home() / "ForestVault"
CRYPTEX_FILE = VAULT / "training_chain.json"
QUARANTINE_DIR = VAULT / "Quarantine" / "Audit"
QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)
MONTHLY_DIR = VAULT / "MonthlyAudits"
MONTHLY_DIR.mkdir(parents=True, exist_ok=True)

class ForestAuditor(Lvl1Worker):
    def __init__(self):
        super().__init__("forest_auditor", "phi3:mini", "Background decomposer — daily/weekly/monthly audits")

    def perform_task(self, task_description="Incremental daily audit"):
        if not self.credential:
            return "Not activated"

        print(f"[AUDITOR] {task_description}...")

        if not CRYPTEX_FILE.exists():
            return "No Cryptex"

        with open(CRYPTEX_FILE, "r") as f:
            lines = f.readlines()

        # Mode selection
        if "weekly" in task_description.lower():
            scan_lines = lines[-20000:] if len(lines) > 20000 else lines
            mode = "weekly"
        elif "monthly" in task_description.lower():
            scan_lines = lines
            mode = "monthly"
        else:
            scan_lines = lines[-5000:] if len(lines) > 5000 else lines
            mode = "daily"

        kept = 0
        pruned = 0
        archived = []

        for line in scan_lines:
            line = line.strip()
            if not line: continue

            prompt = f"""Reassess this Forest log entry for long-term value:
{line}
Criteria: Still useful for blue-team training? Outdated/duplicated/low-quality? Violates constitution?
Reply ONLY: KEEP or PRUNE"""

            try:
                resp = ollama.generate(model=self.model, prompt=prompt, options={"temperature": 0.3})
                decision = resp['response'].strip().upper()
            except:
                decision = "KEEP"

            if decision == "PRUNE":
                pruned += 1
                archived.append(line)
            else:
                kept += 1

        if pruned > 0:
            archive_file = QUARANTINE_DIR / f"{mode}_pruned_{int(datetime.now().timestamp())}.json"
            with open(archive_file, "w") as f:
                json.dump({"timestamp": datetime.now().isoformat(), "mode": mode, "pruned": pruned, "entries": archived}, f, indent=2)

        log_chain("AUDIT_COMPLETE", f"{mode} | kept:{kept} | pruned:{pruned} | scanned:{len(scan_lines)}")

        if mode == "monthly":
            summary_file = MONTHLY_DIR / f"monthly_summary_{datetime.now().strftime('%Y-%m')}.json"
            with open(summary_file, "w") as f:
                json.dump({"month": datetime.now().strftime('%Y-%m'), "kept": kept, "pruned": pruned, "total_scanned": len(lines)}, f, indent=2)
            print(f"[AUDITOR] Monthly compile saved to {summary_file.name}")

        summary = f"{mode.capitalize()} audit complete — Kept {kept} | Pruned {pruned}"
        print(f"[AUDITOR] {summary}")
        return summary

if __name__ == "__main__":
    print("=== ForestAuditor v1.2 Loaded — daily/weekly/monthly background mode ===")
    w = ForestAuditor()
    if w.activate():
        if enforcer.approve("ForestAuditor v1.2 full audit cycle"):
            result = w.perform_task("Daily incremental audit")
            print(f"\n✅ Audit complete → {result}")
        else:
            print("❌ Enforcer blocked")
    else:
        print("❌ Activation failed")
