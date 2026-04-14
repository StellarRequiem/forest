#!/usr/bin/env python3
"""
Forest Lvl1Worker — TheWell v2.1 Safe Nutrient Ingester
Real open-internet physics data pull → heavy filtering → sandbox test → integrate ONLY quality material
"""

from lvl1_worker import Lvl1Worker
from forest_brain import log_chain
from enforcer import enforcer
import requests
import json
import time
from pathlib import Path
from datetime import datetime
import tempfile
import shutil

VAULT = Path.home() / "ForestVault"
WELL_DIR = VAULT / "TheWell"
QUARANTINE_DIR = VAULT / "Quarantine" / "TheWell"
WELL_DIR.mkdir(parents=True, exist_ok=True)
QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)

# Safe seed sources (arXiv physics simulation metadata — academic, high quality, text-only)
SEED_SOURCES = [
    "http://export.arxiv.org/api/query?search_query=all:simulation+OR+physics+OR+n-body+OR+fluid+OR+gravity&start=0&max_results=5&sortBy=submittedDate&sortOrder=descending"
]

class TheWellWorker(Lvl1Worker):
    def __init__(self):
        super().__init__(
            name="the_well",
            model="phi3:mini",
            role="Safe internet nutrient ingester — pulls & filters physics simulation data from open web"
        )

    def _sandbox_test(self, raw_data: dict) -> bool:
        """Rigorous sandbox test before any integration"""
        print("[THE WELL] Running sandbox test on new nutrient...")
        test_dir = Path(tempfile.mkdtemp(dir=Path.home() / "Forest"))
        test_file = test_dir / "test_nutrient.json"
        
        with open(test_file, "w") as f:
            json.dump(raw_data, f)
        
        content = json.dumps(raw_data).lower()
        if any(bad in content for bad in ["hack", "malware", "phish real user", "ddos", "steal", "exploit"]):
            shutil.rmtree(test_dir)
            return False
        
        if not enforcer.enforce_constitution(content):
            shutil.rmtree(test_dir)
            return False
        
        if test_file.stat().st_size > 5_000_000:  # 5MB max
            shutil.rmtree(test_dir)
            return False
        
        shutil.rmtree(test_dir)
        return True

    def perform_task(self, task_description: str = "Ingest new physics nutrients from open internet"):
        if not self.credential:
            return "Not activated"

        print(f"[THE WELL] Starting safe nutrient ingestion: {task_description}")

        quality_nutrients = 0
        discarded = 0

        for url in SEED_SOURCES:
            try:
                print(f"[THE WELL] Pulling from {url}")
                resp = requests.get(url, timeout=15)
                resp.raise_for_status()
                
                # arXiv returns Atom XML, not JSON — handle gracefully
                if "application/atom+xml" in resp.headers.get("content-type", ""):
                    data = {"raw_xml": resp.text[:2000], "source": "arxiv"}
                else:
                    data = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {"raw": resp.text}

                content_str = json.dumps(data).lower()
                quality_score = 0
                if any(kw in content_str for kw in ["n-body", "fluid", "gravity", "simulation", "physics", "pde", "navier-stokes", "particle"]):
                    quality_score += 40
                if len(content_str) > 500:
                    quality_score += 30
                if "arxiv" in url.lower():
                    quality_score += 30

                if quality_score < 60:
                    discarded += 1
                    log_chain("THE_WELL_DISCARDED", f"low quality from {url}")
                    continue

                if not self._sandbox_test(data):
                    discarded += 1
                    qfile = QUARANTINE_DIR / f"quarantined_{int(time.time())}.json"
                    with open(qfile, "w") as f:
                        json.dump({"source": url, "reason": "sandbox failed", "data": data}, f)
                    log_chain("THE_WELL_QUARANTINED", f"{url} → sandbox")
                    continue

                batch_file = WELL_DIR / f"nutrient_{int(time.time())}.json"
                with open(batch_file, "w") as f:
                    json.dump({
                        "batch_id": f"well-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                        "source": url,
                        "quality_score": quality_score,
                        "timestamp": datetime.now().isoformat(),
                        "data": data,
                        "usage_note": "Safe physics simulation nutrient — ready for Forest organs"
                    }, f, indent=2)

                quality_nutrients += 1
                log_chain("THE_WELL_INGESTED", f"quality nutrient from {url} → {batch_file.name}")

            except Exception as e:
                discarded += 1
                log_chain("THE_WELL_ERROR", f"pull failed {url}: {str(e)[:80]}")

        summary = f"The Well ingested {quality_nutrients} quality nutrients | {discarded} discarded/quarantined"
        print(f"[THE WELL] {summary}")
        return summary

if __name__ == "__main__":
    print("=== The Well v2.1 Safe Nutrient Ingester — real internet pull with sandbox filtering ===")
    w = TheWellWorker()
    if w.activate():
        if enforcer.approve("TheWell v2.1 full open-internet nutrient ingestion"):
            result = w.perform_task("First real open-internet physics nutrient batch")
            print(f"\n✅ Well v2.1 complete → {result}")
        else:
            print("❌ Enforcer blocked ingestion")
    else:
        print("❌ Activation failed")
