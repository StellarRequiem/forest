#!/usr/bin/env python3
"""
🌲 Forest Claude Analyzer v1.0
Anthropic API-powered threat analysis with:
- Prompt caching on system prompt (saves ~90% of input tokens after first call)
- Model routing: Haiku for routine, Sonnet for CRITICAL/ATTACK escalation
- Graceful fallback to local phi4-mini via Ollama if API is unavailable
- Cost tracking logged to ForestVault/claude_usage.jsonl
"""

import json
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Cached system prompt — this is sent once then reused from Anthropic's cache.
# Every subsequent call costs ~10% of the normal input token price for this block.
# ---------------------------------------------------------------------------
FOREST_SYSTEM_PROMPT = """You are a senior blue-team security analyst protecting a macOS M4 Mac Mini \
running Forest — an AI-powered threat detection swarm.

PLATFORM:
- macOS Apple Silicon M4, 16GB unified memory
- Docker stack: Forest swarm, Dify, Decepticon red-team sandbox, Ollama, Open-WebUI
- Firewall: pf/pfctl with dynamic IP/port blocking
- Local LLMs: phi4-mini, qwen2.5:3b, nomic-embed-text via Ollama

WATCHERS ACTIVE (sources of incidents):
- ARPWatcher: detects ARP spoofing, MAC changes, Docker subnet ARP activity
- DockerWatcher: detects unexpected container spawns, escape attempts
- NetworkWatcher: detects port scans via SYN_RECV spike patterns
- ProcessWatcher: detects offensive tools (nmap, sqlmap, nc, hydra, hashcat, etc.)
- FileIntegrityWatcher: SHA-256 monitoring of /bin/bash, /etc/hosts, /usr/sbin/sshd, LaunchDaemons
- BruteForceWatcher: SSH/auth failure rate via /var/log/system.log
- ProcessNetworkWatcher: lsof-based process-to-socket mapping, new listening ports
- YaraPatternWatcher: script pattern matching in /tmp, /var/tmp, ~/Downloads

RESPONSE CAPABILITIES:
- block_ip: add IP to pf firewall blocklist
- block_port: block inbound port via pf
- isolate_container: docker kill + network disconnect
- kill_process: kill suspicious process by PID
- quarantine_file: move suspicious file to ~/ForestVault/quarantine/
- alert_admin: log high-priority alert
- collect_evidence: snapshot process list, network state, file hashes

SEVERITY SCALE:
1 = INFO (log only, no action)
2 = WARNING (monitor, alert)
3 = CRITICAL (active response required)
4 = ATTACK (immediate block + escalation)

Always output structured, actionable analysis. Be concise — this runs in a real-time loop."""

# ---------------------------------------------------------------------------
# Model routing
# ---------------------------------------------------------------------------
MODEL_HAIKU   = "claude-haiku-3-5"    # routine analysis — fast, ~$0.25/1M input
MODEL_SONNET  = "claude-sonnet-4-5"   # escalated CRITICAL/ATTACK incidents
MODEL_FALLBACK = "phi4-mini"          # local fallback when API unavailable

USAGE_LOG = Path.home() / "ForestVault" / "claude_usage.jsonl"

# Cost estimates per million tokens (approximate, for tracking only)
COST_PER_M = {
    MODEL_HAIKU:  {"input": 0.80,  "output": 4.00,  "cache_read": 0.08,  "cache_write": 1.00},
    MODEL_SONNET: {"input": 3.00,  "output": 15.00, "cache_read": 0.30,  "cache_write": 3.75},
}


class ClaudeAnalyzer:
    """
    Drop-in replacement for subprocess.run(["ollama", "run", ...]) calls.
    Uses Anthropic API with cached system prompt + phi4-mini fallback.
    """

    def __init__(self):
        self._client = None
        self._api_available: Optional[bool] = None
        self._consecutive_failures = 0
        self._circuit_open_until: float = 0.0   # circuit breaker timestamp

    def _get_client(self):
        """Lazy-init Anthropic client — only imported if API key is present."""
        if self._client is None:
            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if not api_key:
                return None
            try:
                import anthropic
                self._client = anthropic.Anthropic(api_key=api_key)
                self._api_available = True
            except ImportError:
                print("[ClaudeAnalyzer] anthropic package not installed — using fallback")
                self._api_available = False
        return self._client

    # -----------------------------------------------------------------------
    # Public interface
    # -----------------------------------------------------------------------

    def analyze_incident(self, threat_type: str, details: dict,
                         severity_hint: int = 2) -> str:
        """
        Analyze a threat incident. Returns structured text with ANALYSIS/SEVERITY/IMMEDIATE_ACTIONS.
        Routes to Haiku for INFO/WARNING, Sonnet for CRITICAL/ATTACK.
        Falls back to phi4-mini if API unavailable.
        """
        model = MODEL_SONNET if severity_hint >= 3 else MODEL_HAIKU

        user_prompt = f"""Analyze this security incident detected on the Forest blue-team system.

THREAT TYPE: {threat_type}
DETAILS:
{json.dumps(details, indent=2)}

Respond in this exact format:
ANALYSIS: [2-3 sentences describing what is happening and why it matters]
SEVERITY: [1-4]
IMMEDIATE_ACTIONS: [comma-separated list from: block_ip, block_port, isolate_container, kill_process, quarantine_file, alert_admin, collect_evidence]
CONFIDENCE: [1-10]"""

        return self._call(model=model, user_prompt=user_prompt,
                          context=f"analyze:{threat_type}")

    def suggest_improvement(self, threat_type: str, actions_taken: list) -> str:
        """
        Generate a training improvement suggestion after an incident is resolved.
        Always uses Haiku — training suggestions are lower priority.
        """
        user_prompt = f"""Based on this resolved incident, suggest one concrete improvement
for the Forest blue-team detection or response system.

THREAT: {threat_type}
ACTIONS TAKEN: {', '.join(actions_taken[:5])}

Respond in this exact format:
IMPROVEMENT: [specific detection rule, pf rule, or response action]
TYPE: [pf_rule | detection_pattern | response_action | logging]
REASON: [one sentence why this helps]
CONFIDENCE: [1-10]"""

        return self._call(model=MODEL_HAIKU, user_prompt=user_prompt,
                          context=f"train:{threat_type}")

    # -----------------------------------------------------------------------
    # Internal: API call with caching + circuit breaker + fallback
    # -----------------------------------------------------------------------

    def _call(self, model: str, user_prompt: str, context: str = "") -> str:
        """Execute API call with cached system prompt. Falls back to Ollama on failure."""

        # Circuit breaker — if we've had 3 consecutive failures, pause API for 5 min
        if time.time() < self._circuit_open_until:
            return self._ollama_fallback(user_prompt, context)

        client = self._get_client()
        if client is None:
            return self._ollama_fallback(user_prompt, context)

        try:
            import anthropic

            response = client.messages.create(
                model=model,
                max_tokens=512,
                system=[
                    {
                        "type": "text",
                        "text": FOREST_SYSTEM_PROMPT,
                        "cache_control": {"type": "ephemeral"},  # cache this block
                    }
                ],
                messages=[
                    {"role": "user", "content": user_prompt}
                ],
            )

            result = response.content[0].text.strip()
            self._consecutive_failures = 0   # reset circuit breaker

            # Log usage + estimated cost
            self._log_usage(model, response.usage, context)

            return result

        except Exception as e:
            self._consecutive_failures += 1
            print(f"[ClaudeAnalyzer] API error ({self._consecutive_failures}): {e}")

            if self._consecutive_failures >= 3:
                # Open circuit for 5 minutes
                self._circuit_open_until = time.time() + 300
                print("[ClaudeAnalyzer] Circuit open — switching to local phi4-mini for 5 min")

            return self._ollama_fallback(user_prompt, context)

    def _ollama_fallback(self, prompt: str, context: str = "") -> str:
        """Call local phi4-mini via Ollama subprocess."""
        try:
            result = subprocess.run(
                ["ollama", "run", MODEL_FALLBACK, prompt],
                capture_output=True, text=True, timeout=45
            )
            output = result.stdout.strip()
            if not output:
                return "ANALYSIS: Fallback analysis unavailable\nSEVERITY: 2\nIMMEDIATE_ACTIONS: alert_admin\nCONFIDENCE: 1"
            return output
        except Exception as e:
            return f"ANALYSIS: Analysis failed — {e}\nSEVERITY: 2\nIMMEDIATE_ACTIONS: alert_admin\nCONFIDENCE: 1"

    def _log_usage(self, model: str, usage, context: str):
        """Append token usage + estimated cost to ForestVault/claude_usage.jsonl."""
        try:
            rates = COST_PER_M.get(model, {"input": 1.0, "output": 5.0, "cache_read": 0.1, "cache_write": 1.25})

            input_tokens  = getattr(usage, "input_tokens", 0)
            output_tokens = getattr(usage, "output_tokens", 0)
            cache_read    = getattr(usage, "cache_read_input_tokens", 0)
            cache_write   = getattr(usage, "cache_creation_input_tokens", 0)

            # Cached reads cost 10% of normal input price
            cost = (
                (input_tokens  / 1_000_000) * rates["input"]  +
                (output_tokens / 1_000_000) * rates["output"] +
                (cache_read    / 1_000_000) * rates["cache_read"] +
                (cache_write   / 1_000_000) * rates["cache_write"]
            )

            entry = {
                "ts":           datetime.now().isoformat(),
                "model":        model,
                "context":      context,
                "input_tok":    input_tokens,
                "output_tok":   output_tokens,
                "cache_read":   cache_read,
                "cache_write":  cache_write,
                "cost_usd":     round(cost, 6),
            }

            USAGE_LOG.parent.mkdir(exist_ok=True)
            with open(USAGE_LOG, "a") as f:
                f.write(json.dumps(entry) + "\n")

            print(f"[ClaudeAnalyzer] {model} | {input_tokens}in/{output_tokens}out "
                  f"| cache_read={cache_read} | ${cost:.5f} | {context}")

        except Exception:
            pass   # never let logging break the main flow

    def get_spend_summary(self) -> dict:
        """Read usage log and return total spend + call counts."""
        if not USAGE_LOG.exists():
            return {"total_usd": 0.0, "calls": 0, "cache_hit_rate": 0.0}

        total_cost  = 0.0
        calls       = 0
        cache_reads = 0
        total_input = 0

        try:
            for line in USAGE_LOG.read_text().splitlines():
                if not line.strip():
                    continue
                entry = json.loads(line)
                total_cost  += entry.get("cost_usd", 0)
                calls       += 1
                cache_reads += entry.get("cache_read", 0)
                total_input += entry.get("input_tok", 0)
        except Exception:
            pass

        return {
            "total_usd":      round(total_cost, 4),
            "calls":          calls,
            "cache_hit_rate": round(cache_reads / max(total_input, 1), 3),
        }


# Module-level singleton — import and use directly
analyzer = ClaudeAnalyzer()
