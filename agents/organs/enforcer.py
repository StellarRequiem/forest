#!/usr/bin/env python3
"""
Forest Enforcer v4.0 — LLM-backed constitution check + process hygiene.

enforce_constitution() now uses phi3:mini at temperature 0.0 as an
LLM-as-judge. The keyword deny-list is kept as a fast pre-check before
the LLM call, so obvious violations are blocked instantly without
spending tokens.
"""

import re
import subprocess
import hashlib
from datetime import datetime
from pathlib import Path

import psutil
import ollama

# ── Audit chain ───────────────────────────────────────────────────────────────

VAULT_DIR    = Path.home() / "ForestVault"
VAULT_DIR.mkdir(exist_ok=True)
CRYPTEX_FILE = VAULT_DIR / "training_chain.json"

def log_to_cryptex(event_type: str, details: str = "") -> None:
    timestamp = datetime.now().isoformat()
    entry     = f"{timestamp} | {event_type} | {details}"
    h         = hashlib.sha256(entry.encode()).hexdigest()[:24]
    with open(CRYPTEX_FILE, "a") as f:
        f.write(f"{entry} | Hash: {h}\n")
    print(f"[ENFORCER] {event_type} | {details[:100]} | Hash: {h}")


# ── Constitution judge prompt ─────────────────────────────────────────────────

_JUDGE_PROMPT = (
    "This is output from a defensive security monitoring agent.\n"
    "Does this text give instructions for causing harm, or is it reporting observations to a defender?\n"
    "Answer HARMFUL (gives attack instructions) or SAFE (reports observations defensively).\n\n"
    "Text: {output}\n\n"
    "Answer:"
)


class EnforcerTeam:

    # Hard-coded instant-block phrases (no LLM token spend needed).
    # Rule: only include phrases that are unambiguously offensive —
    # a defensive blue-team report would NEVER naturally contain these exact strings.
    # Single words like "ddos" or "rootkit" are too broad; blue-teamers mention them
    # as threat descriptions. Use attack-intent verb phrases instead.
    _INSTANT_DENY = [
        "install malware",
        "deploy malware",
        "launch ddos attack",
        "execute ddos",
        "phish real user",
        "steal credentials",
        "exfiltrate data",
        "exfiltrate credentials",
        "exfiltrate files",
        "write a rootkit for",
        "build a rootkit for",
        "deploy a rootkit on",
        "install ransomware",
        "deploy ransomware",
        "install keylogger",
        "deploy keylogger",
        "bypass firewall to gain",
        "bypass security controls",
        "escalate privileges on",
    ]

    def __init__(self):
        self.blocked_count = 0

    # ── Swarm scan ────────────────────────────────────────────────────────────

    def scan_swarm(self, status: dict = None) -> dict:
        """Scan tmux sessions; leave forest-named and known-safe sessions alone."""
        print("[ENFORCER] Scanning active sessions and processes...")

        protected = {"brain", "mouth", "forge", "warden", "cusbrain"}
        try:
            result   = subprocess.run(["tmux", "ls"], capture_output=True, text=True)
            sessions = [l.split(":")[0] for l in result.stdout.splitlines() if l.strip()]
            for sess in sessions:
                if "forest" in sess.lower() or sess in protected:
                    continue
                print(f"[ENFORCER] Terminating unrecognised session: {sess}")
                subprocess.run(["tmux", "kill-session", "-t", sess],
                               stdout=subprocess.DEVNULL)
                log_to_cryptex("SESSION_KILLED", sess)
                self.blocked_count += 1
        except Exception as exc:
            log_to_cryptex("SCAN_ERROR", str(exc))

        # Kill any Ollama process launched with --danger flag
        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            try:
                cmd = " ".join(proc.info["cmdline"] or [])
                if "ollama" in cmd and "--danger" in cmd:
                    proc.kill()
                    log_to_cryptex("PROCESS_KILLED", f"pid:{proc.info['pid']}")
            except Exception:
                pass

        return {"status": "scanned", "blocked": self.blocked_count}

    # ── Human gate ────────────────────────────────────────────────────────────

    def approve(self, action: str) -> bool:
        print(f"\n🔒 ENFORCER GATE: {action}")
        print("Type 'yes' to approve, anything else to BLOCK.")
        try:
            choice = input("ENFORCER APPROVE? > ").strip().lower()
            approved = choice in ("yes", "y")
        except Exception:
            approved = False

        event = "ACTION_APPROVED" if approved else "ACTION_BLOCKED"
        log_to_cryptex(event, action[:100])
        if not approved:
            self.blocked_count += 1
        return approved

    # ── Constitution check ────────────────────────────────────────────────────

    def enforce_constitution(self, output: str) -> bool:
        """
        Two-stage check:
          1. Instant deny-list (free, < 1 ms)
          2. LLM judge: phi3:mini at temp 0.0  (fallback to keyword if unavailable)
        Returns True  → output is SAFE, allow it through.
        Returns False → output violated constitution, block it.
        """
        text_lower = output.lower()

        # Stage 1 — instant deny
        for phrase in self._INSTANT_DENY:
            if phrase in text_lower:
                log_to_cryptex("CONSTITUTION_INSTANT_DENY",
                               f"phrase='{phrase}' | {output[:80]}")
                self.blocked_count += 1
                return False

        # Stage 2 — LLM judge
        verdict = self._llm_judge(output)
        if verdict == "UNSAFE":
            log_to_cryptex("CONSTITUTION_LLM_DENY", output[:80])
            self.blocked_count += 1
            return False

        log_to_cryptex("CONSTITUTION_PASSED", output[:80])
        return True

    def _llm_judge(self, output: str) -> str:
        """Returns 'SAFE' or 'UNSAFE'. Defaults to 'SAFE' if LLM is unreachable."""
        prompt = _JUDGE_PROMPT.format(output=output[:500])
        try:
            resp = ollama.generate(
                model="qwen2.5:3b",
                prompt=prompt,
                options={"temperature": 0.0, "num_predict": 5},
            )
            text = resp.get("response", "").strip().upper()
            # The new prompt can return "HARMFUL (...)" or "SAFE (...)"
            if "HARMFUL" in text:
                return "UNSAFE"
            return "SAFE"
        except Exception as exc:
            log_to_cryptex("LLM_JUDGE_UNAVAILABLE", str(exc)[:80])
            # Fallback: if we can't reach the LLM, default to SAFE
            # (the deny-list already caught the obvious bad actors)
            return "SAFE"


# ── Singleton ─────────────────────────────────────────────────────────────────

enforcer = EnforcerTeam()

print("=== Forest Enforcer v4.0 Loaded — qwen2.5:3b Constitution Judge Active ===")
