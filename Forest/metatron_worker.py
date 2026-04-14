#!/usr/bin/env python3
"""
Forest Lvl1Worker — MetatronWorker v1.6
Safe, silent background mode with robust timeout
"""

from lvl1_worker import Lvl1Worker
from forest_brain import log_chain
import subprocess
from pathlib import Path

class MetatronWorker(Lvl1Worker):
    def __init__(self):
        super().__init__("metatron_redteam", "phi3:mini", "Contained red-team pentesting black box (METATRON)")
        self.sandbox_path = Path.home() / "Forest/danger_room/sandbox/metatron"

    def perform_task(self, task_description, background_mode=False):
        if not self.credential:
            return "Not activated"

        print(f"[METATRON BLACK BOX] Received task: {task_description[:80]}...")

        command = f"cd {self.sandbox_path} && python metatron.py --task '{task_description}' --non-interactive"

        if background_mode:
            print("[METATRON] Background mode — running silently")
            approved = True
        else:
            approved = True

        log_chain("METATRON_EXECUTING", command[:100])

        try:
            result = subprocess.run(
                f"source ~/Forest/danger_room/danger_venv/bin/activate && {command}",
                shell=True, capture_output=True, text=True, timeout=45, stdin=subprocess.DEVNULL
            )
            output = result.stdout + result.stderr
            log_chain("METATRON_OUTPUT", f"exit:{result.returncode}")
            return f"METATRON completed — {output[:300]}..."
        except Exception as e:
            log_chain("METATRON_ERROR", str(e))
            return f"METATRON sandbox error: {e}"

print("=== MetatronWorker v1.6 loaded — safe silent mode ===")
