#!/usr/bin/env python3
"""
Forest Semantic Drift Detector v1.0

Creates a vector embedding of the current system fingerprint (ports,
connections, processes) using nomic-embed-text via Ollama, then compares
it to a rolling window of previous cycle embeddings via cosine similarity.

Why this matters:
  Hard rules catch known-bad signatures. Baseline delta catches explicit
  changes. Semantic drift catches *behavioral shifts* — situations where
  the system looks different in a way no single rule covers. For example:
  10 new processes that are all individually benign but together represent
  a new workload pattern, or a gradual increase in external connections
  that no threshold would trigger.

  The drift score is 0.0–1.0 where 1.0 = identical to recent history.
  A sudden drop (e.g. 0.95 → 0.72) warrants human review even if no
  other alerts fired.

History is stored in ~/ForestVault/drift_history.json.
  - Keeps the last HISTORY_SIZE cycle embeddings (default 20)
  - Detection activates after 3 cycles (building baseline window)
  - The embedding model (nomic-embed-text) produces 768-dimensional vectors
  - Cosine similarity is computed in pure Python — no numpy required
"""

import json
import math
import subprocess
import re
from datetime import datetime
from pathlib import Path

import ollama
import psutil

# ── Config ────────────────────────────────────────────────────────────────────

VAULT_DIR    = Path.home() / "ForestVault"
HISTORY_FILE = VAULT_DIR / "drift_history.json"
HISTORY_SIZE = 20      # rolling window size
MIN_CYCLES   = 3       # cycles before drift detection activates

EMBED_MODEL  = "nomic-embed-text"

# Thresholds for drift verdict
THRESHOLD_STABLE   = 0.97   # similarity >= this → STABLE
THRESHOLD_MINOR    = 0.90   # similarity >= this → MINOR_DRIFT
THRESHOLD_MODERATE = 0.75   # similarity >= this → MODERATE_DRIFT
                             # similarity < THRESHOLD_MODERATE → SIGNIFICANT_DRIFT

# RFC1918 — filter from fingerprint (not interesting as "external")
_PRIVATE_PREFIXES = ("127.", "10.", "192.168.", "172.16.", "172.17.",
                     "172.18.", "172.19.", "172.2", "::1", "fe80")


# ── Embedding helpers ─────────────────────────────────────────────────────────

def _embed(text: str) -> list[float] | None:
    """
    Call nomic-embed-text via Ollama to produce a 768-dim embedding vector.
    Returns None if the model is unavailable.
    """
    try:
        resp = ollama.embeddings(model=EMBED_MODEL, prompt=text)
        vec = resp.get("embedding", [])
        return vec if vec else None
    except Exception as exc:
        print(f"[DRIFT] Embedding unavailable: {exc}")
        return None


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Pure-Python cosine similarity. Returns 0.0 if either vector is zero."""
    if len(a) != len(b):
        return 0.0
    dot   = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(x * x for x in b))
    if mag_a == 0.0 or mag_b == 0.0:
        return 0.0
    return dot / (mag_a * mag_b)


def _average_embedding(embeddings: list[list[float]]) -> list[float]:
    """Element-wise mean of a list of equal-length embedding vectors."""
    if not embeddings:
        return []
    dim = len(embeddings[0])
    avg = [0.0] * dim
    for vec in embeddings:
        for i, v in enumerate(vec):
            avg[i] += v
    n = len(embeddings)
    return [x / n for x in avg]


# ── History I/O ───────────────────────────────────────────────────────────────

def _load_history() -> list[dict]:
    """
    Load drift history from disk.
    Returns list of dicts: [{"timestamp": str, "embedding": [float, ...]}, ...]
    """
    VAULT_DIR.mkdir(exist_ok=True)
    if not HISTORY_FILE.exists():
        return []
    try:
        return json.loads(HISTORY_FILE.read_text())
    except Exception:
        return []


def _save_history(history: list[dict], new_embedding: list[float]) -> list[dict]:
    """
    Append new_embedding to history, trim to HISTORY_SIZE, write to disk.
    Returns the updated history list.
    """
    history.append({
        "timestamp": datetime.now().isoformat(),
        "embedding": new_embedding,
    })
    history = history[-HISTORY_SIZE:]
    VAULT_DIR.mkdir(exist_ok=True)
    HISTORY_FILE.write_text(json.dumps(history))
    return history


# ── System fingerprint ────────────────────────────────────────────────────────

def _make_fingerprint() -> tuple[str, dict]:
    """
    Build a text fingerprint of the current system state. Designed to be:
      - Stable: identical systems produce very similar text
      - Sensitive: real changes (new ports, new processes) change it
      - Fast: no LLM calls, just shell + psutil

    Returns (fingerprint_text, stats_dict) where stats_dict has human-
    readable counts for the worker output string.
    """
    lines = []
    stats = {"ports": 0, "ext_ips": 0, "processes": 0}

    # ── Network: listening ports ──────────────────────────────────────────
    listening_ports: list[int] = []
    ext_ips: list[str] = []
    try:
        result = subprocess.run(
            ["netstat", "-an", "-p", "tcp"],
            capture_output=True, text=True, timeout=8,
        )
        for line in result.stdout.splitlines():
            parts = line.split()
            if len(parts) < 5:
                continue
            if "LISTEN" in line:
                local = parts[3]
                port_str = local.rsplit(".", 1)[-1]
                if port_str.isdigit():
                    listening_ports.append(int(port_str))
            if "ESTABLISHED" in line:
                remote = parts[4]
                ip_part = remote.rsplit(".", 1)[0]
                port_part = remote.rsplit(".", 1)[-1]
                if (not any(ip_part.startswith(p) for p in _PRIVATE_PREFIXES)
                        and port_part.isdigit()):
                    ext_ips.append(ip_part)
    except Exception:
        pass

    listening_ports = sorted(set(listening_ports))
    ext_ips = sorted(set(ext_ips))
    stats["ports"] = len(listening_ports)
    stats["ext_ips"] = len(ext_ips)

    lines.append(f"Listening ports ({len(listening_ports)}): {listening_ports[:25]}")
    lines.append(f"External IP count: {len(ext_ips)}")
    # Don't include actual external IPs in the fingerprint — they change
    # legitimately (browser traffic, updates) and would swamp drift signal.
    # Connection count and port list are the stable signal.

    # ── Processes: compact summary ────────────────────────────────────────
    # nomic-embed-text has a limited context window (~512 tokens effectively).
    # Listing all 400+ process names by itself exceeds it.
    # Strategy: total count (stable signal) + first 40 sorted unique names
    # (alphabetical sort is consistent across runs for the same process set).
    proc_names: list[str] = []
    try:
        for p in psutil.process_iter(["name"]):
            try:
                n = p.info.get("name", "")
                if n:
                    proc_names.append(n)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    except Exception:
        pass

    unique_sorted = sorted(set(proc_names))
    stats["processes"] = len(unique_sorted)
    # Include total count (changes when new processes appear) and the first
    # 40 names (catches additions near the start of the alphabet; combined
    # with count it creates a stable fingerprint that shifts on new entries).
    sample = unique_sorted[:40]
    lines.append(
        f"Process count: {len(unique_sorted)} | "
        f"Sample (first 40 alphabetical): {sample}"
    )

    fingerprint = "\n".join(lines)
    return fingerprint, stats


# ── Main worker class ─────────────────────────────────────────────────────────

class SemanticDriftDetector:
    """
    Embeds the current system fingerprint and compares to a rolling window
    of previous embeddings. Reports a similarity score and drift verdict.

    Requires nomic-embed-text to be available in Ollama. If unavailable,
    returns a graceful error message that passes constitution check.
    """

    MODEL = EMBED_MODEL
    NAME  = "semantic_drift_detector"

    def run(self) -> str:
        # Build fingerprint of current state
        fingerprint, stats = _make_fingerprint()

        # Embed it
        embedding = _embed(fingerprint)
        if embedding is None:
            return (
                f"[{self.NAME}] nomic-embed-text unavailable — "
                f"run: ollama pull nomic-embed-text"
            )

        # Load history
        history = _load_history()
        n_before = len(history)

        # Save this cycle's embedding first (don't include current in comparison)
        history = _save_history(history, embedding)

        # Not enough history yet
        if n_before < MIN_CYCLES:
            cycles_done = n_before + 1   # including the one we just saved
            remaining   = MIN_CYCLES - cycles_done
            return (
                f"[{self.NAME}] Building baseline window — "
                f"cycle {cycles_done}/{MIN_CYCLES} recorded. "
                f"Drift detection activates in {remaining} more cycle(s). "
                f"Fingerprint: {stats['ports']} listening ports, "
                f"{stats['processes']} processes, "
                f"{stats['ext_ips']} external IPs."
            )

        # Compute cosine similarity against rolling average of recent history
        # (exclude the entry we just added so we're comparing against past state)
        comparison_window = history[:-1][-HISTORY_SIZE:]
        avg_vec = _average_embedding([e["embedding"] for e in comparison_window])
        similarity = _cosine_similarity(embedding, avg_vec)

        # Determine verdict
        if similarity >= THRESHOLD_STABLE:
            verdict  = "STABLE"
            detail   = "System fingerprint is highly consistent with recent cycles."
            urgency  = ""
        elif similarity >= THRESHOLD_MINOR:
            verdict  = "MINOR_DRIFT"
            detail   = "Small but detectable change in system state. Review delta items for explanation."
            urgency  = ""
        elif similarity >= THRESHOLD_MODERATE:
            verdict  = "MODERATE_DRIFT"
            detail   = "Moderate behavioral shift detected. Investigate new ports or processes."
            urgency  = " ⚠"
        else:
            verdict  = "SIGNIFICANT_DRIFT"
            detail   = "Major shift in system fingerprint. High-priority manual review required."
            urgency  = " 🚨"

        return (
            f"[{self.NAME}]{urgency} Drift: {verdict} | "
            f"similarity={similarity:.4f} | "
            f"window={len(comparison_window)} cycles | "
            f"fingerprint: {stats['ports']} ports, "
            f"{stats['processes']} procs, "
            f"{stats['ext_ips']} ext_ips | "
            f"{detail}"
        )


# ── History stats (for dashboard / CLI) ──────────────────────────────────────

def history_stats() -> dict:
    """Return a summary of the drift history file for the dashboard."""
    history = _load_history()
    if not history:
        return {"cycles": 0, "oldest": "", "newest": "", "embeddings": False}

    embeddings = [e["embedding"] for e in history if e.get("embedding")]
    return {
        "cycles":     len(history),
        "oldest":     history[0]["timestamp"][:19],
        "newest":     history[-1]["timestamp"][:19],
        "embeddings": len(embeddings),
        "dim":        len(embeddings[0]) if embeddings else 0,
    }


# ── Smoke test ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== Semantic Drift smoke test ===\n")
    fp, stats = _make_fingerprint()
    print(f"Fingerprint stats: {stats}")
    print(f"Fingerprint text ({len(fp)} chars):\n{fp[:300]}...\n")

    vec = _embed(fp[:200])
    if vec:
        print(f"Embedding: {len(vec)}-dim vector, first 5 values: {vec[:5]}")
        sim = _cosine_similarity(vec, vec)
        print(f"Self-similarity: {sim:.6f} (should be 1.0)")
    else:
        print("Embedding failed — is nomic-embed-text pulled in Ollama?")

    print(f"\nHistory: {history_stats()}")
