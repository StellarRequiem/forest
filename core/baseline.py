#!/usr/bin/env python3
"""
Forest Baseline Engine v1.0

Stores a known-good snapshot of the system in ~/ForestVault/baseline.json.
Workers load it, compute a delta, and inject changed items into their LLM
prompts so the model focuses on *what changed*, not just what exists.

Baseline is created automatically on the first swarm cycle and is never
auto-updated — intentional, so persistent drift is always visible.
Update manually with:  python3 core/cus_langgraph.py --update-baseline

Baseline schema:
  {
    "created":  "ISO timestamp",
    "updated":  "ISO timestamp",
    "cycles":   int,           # how many cycles have run since last update
    "network": {
      "listening_ports":  [int, ...],
      "external_ips":     ["host:port", ...]
    },
    "processes": {
      "known_names": ["name", ...]
    }
  }
"""

import json
from datetime import datetime
from pathlib import Path

VAULT_DIR     = Path.home() / "ForestVault"
BASELINE_FILE = VAULT_DIR / "baseline.json"


# ── I/O ───────────────────────────────────────────────────────────────────────

def load() -> dict | None:
    """Return the baseline dict, or None if no baseline exists yet."""
    if not BASELINE_FILE.exists():
        return None
    try:
        return json.loads(BASELINE_FILE.read_text())
    except Exception:
        return None


def save(data: dict) -> None:
    """Write baseline to disk, creating ForestVault if needed."""
    VAULT_DIR.mkdir(exist_ok=True)
    BASELINE_FILE.write_text(json.dumps(data, indent=2))


def create(network_ports: list[int],
           network_ext_ips: list[str],
           process_names: list[str]) -> dict:
    """Build a fresh baseline dict from current observations."""
    now = datetime.now().isoformat()
    return {
        "created":  now,
        "updated":  now,
        "cycles":   0,
        "network": {
            "listening_ports": sorted(set(network_ports)),
            "external_ips":    list(dict.fromkeys(network_ext_ips)),
        },
        "processes": {
            "known_names": sorted(set(process_names)),
        },
    }


def increment_cycles(baseline: dict) -> None:
    """Bump the cycle counter in-place (caller must call save() afterwards)."""
    baseline["cycles"] = baseline.get("cycles", 0) + 1


# ── Delta helpers ─────────────────────────────────────────────────────────────

def network_delta(baseline: dict,
                  current_ports: list[int],
                  current_ext_ips: list[str]) -> dict:
    """
    Return a delta dict with three keys:
      new_ports     — ports listening now but not in baseline
      removed_ports — ports that were in baseline but are gone
      new_ext_ips   — external IPs not seen before
    All values are sorted lists; empty list = no change.
    """
    b_ports = set(baseline.get("network", {}).get("listening_ports", []))
    c_ports = set(current_ports)

    b_ips   = set(baseline.get("network", {}).get("external_ips", []))
    c_ips   = set(current_ext_ips)

    return {
        "new_ports":     sorted(c_ports - b_ports),
        "removed_ports": sorted(b_ports - c_ports),
        "new_ext_ips":   sorted(c_ips - b_ips),
    }


def process_delta(baseline: dict, current_names: list[str]) -> dict:
    """
    Return a delta dict:
      new_processes  — process names running now but not in baseline
    """
    b_names = set(baseline.get("processes", {}).get("known_names", []))
    c_names = set(current_names)
    return {
        "new_processes": sorted(c_names - b_names),
    }


def format_network_delta(delta: dict) -> str:
    """
    Human-readable delta block for injection into an LLM prompt.
    Returns empty string if nothing changed.
    """
    parts = []
    if delta["new_ports"]:
        parts.append(f"NEW listening ports (not in baseline): {delta['new_ports']}")
    if delta["removed_ports"]:
        parts.append(f"REMOVED ports (were in baseline, now gone): {delta['removed_ports']}")
    if delta["new_ext_ips"]:
        parts.append(f"NEW external IPs (not seen before): {delta['new_ext_ips']}")
    if not parts:
        return ""
    return "[DELTA — changes since baseline]\n" + "\n".join(parts)


def format_process_delta(delta: dict) -> str:
    """
    Human-readable delta block for process changes.
    Returns empty string if nothing changed.
    """
    if not delta["new_processes"]:
        return ""
    return (
        "[DELTA — changes since baseline]\n"
        f"NEW processes (not in baseline): {delta['new_processes']}"
    )


# ── Smoke test ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    existing = load()
    if existing:
        print(f"Baseline exists — created {existing['created']}, "
              f"cycles since update: {existing.get('cycles', 0)}")
        print(f"  Known ports: {existing['network']['listening_ports']}")
        print(f"  Known processes: {len(existing['processes']['known_names'])}")
    else:
        print("No baseline file. Will be created on first swarm cycle.")
