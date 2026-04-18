"""
Forest Status API — thin read-only FastAPI on port 7438.

Reads from ~/ForestVault without importing the live swarm orchestrator.
Buddy calls this to surface active forest incidents in its UI.

Start manually:
  cd ~/forest-blue-team-guardian && .venv/bin/uvicorn api.status_api:app --host 127.0.0.1 --port 7438

Auto-start: see scripts/forest-api-start.sh + launchd plist (optional)
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

VAULT = Path.home() / "ForestVault"

app = FastAPI(
    title="Forest Status API",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:7437", "http://127.0.0.1:7437"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _read_recent_incidents(n: int = 50) -> list[dict]:
    """Read last n incident entries from incidents.jsonl."""
    path = VAULT / "incidents.jsonl"
    if not path.exists():
        return []
    try:
        lines = [l for l in path.read_text().strip().splitlines() if l.strip()]
        entries: list[dict] = []
        for line in lines[-n:]:
            try:
                entries.append(json.loads(line))
            except Exception:
                continue
        return entries
    except Exception:
        return []


def _chain_length() -> int:
    """Return number of entries in the cus-core audit chain."""
    path = VAULT / "training_chain.json"
    if not path.exists():
        return 0
    try:
        data = json.loads(path.read_text())
        return len(data.get("entries", []))
    except Exception:
        return 0


def _improvement_count() -> int:
    """Count graded improvements in training_improvements.jsonl."""
    path = VAULT / "training_improvements.jsonl"
    if not path.exists():
        return 0
    try:
        lines = [l for l in path.read_text().strip().splitlines() if l.strip()]
        return len(lines)
    except Exception:
        return 0


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "online", "vault": str(VAULT)}


@app.get("/forest/status")
async def status():
    incidents = _read_recent_incidents(50)

    # Aggregate stats
    severity_counts: dict[str, int] = {}
    phase_counts: dict[str, int] = {}
    active_incidents: list[dict] = []

    for inc in incidents:
        sev = inc.get("severity", "UNKNOWN")
        phase = inc.get("phase", "unknown")
        severity_counts[sev] = severity_counts.get(sev, 0) + 1
        phase_counts[phase] = phase_counts.get(phase, 0) + 1

        # Active = not yet resolved (detect / analyze / respond phases)
        if phase in ("detect", "analyze", "respond"):
            active_incidents.append({
                "id": inc.get("id", "?"),
                "threat_type": inc.get("threat_type", "unknown"),
                "severity": sev,
                "phase": phase,
                "timestamp": inc.get("timestamp", ""),
                "response_actions": inc.get("response_actions", [])[:3],
                "blocked_ips": inc.get("blocked_ips", [])[:3],
            })

    return {
        "status": "online",
        "vault": str(VAULT),
        "total_logged": len(incidents),
        "severity_breakdown": severity_counts,
        "phase_breakdown": phase_counts,
        "active_incidents": active_incidents[:5],    # cap at 5 for buddy widget
        "chain_length": _chain_length(),
        "improvements_logged": _improvement_count(),
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.status_api:app", host="127.0.0.1", port=7438, log_level="warning")
