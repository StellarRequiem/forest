#!/usr/bin/env python3
"""
Forest Detection Rules v1.0 — hard rules that run alongside the LLM

These rules fire instantly (no LLM tokens spent) and inject [RULE ALERT]
blocks into the worker prompts so the LLM has additional context when
writing its assessment.

Rule philosophy:
  - Only flag things a defender genuinely needs to see
  - Avoid false-positive noise (common dev tools are not flagged)
  - Rules are additive — multiple alerts can fire per cycle
"""

import re
from pathlib import Path

# ── Suspicious network ports ──────────────────────────────────────────────────
# Classic backdoor, C2, and tool-listener ports that should NEVER appear in
# normal production/dev traffic. If you intentionally use one of these (e.g.
# port 8888 for Jupyter), add it to your local allowlist in .env.

SUSPICIOUS_PORTS: dict[int, str] = {
    4444:  "classic Metasploit default listener",
    31337: "classic elite/Back Orifice port",
    1337:  "common script-kiddie backdoor port",
    6666:  "IRC / common malware C2",
    6667:  "IRC plaintext (unusual on modern systems)",
    1234:  "generic test/backdoor port",
    12345: "NetBus RAT default",
    5555:  "Android Debug Bridge remote — should not be open",
    9001:  "Tor relay port",
    9050:  "Tor SOCKS proxy",
    9051:  "Tor control port",
    65535: "suspicious high port — often used to evade scans",
}

# ── Suspicious process names ──────────────────────────────────────────────────
# Match process names exactly (case-insensitive) or by substring where noted.
# Legitimate security tools (nmap, etc.) that researchers run intentionally
# are still flagged — the human gate is the final decision point.

SUSPICIOUS_PROC_NAMES: dict[str, str] = {
    # Network pivoting / shells
    "nc":        "netcat — raw TCP/UDP shell tool; rare in production",
    "ncat":      "ncat (nmap netcat) — same concern as nc",
    "netcat":    "netcat — raw TCP/UDP shell tool",
    "socat":     "socat — advanced socket relay, unusual in production",
    # Scanners
    "nmap":      "port scanner — expected only during authorized scans",
    "masscan":   "high-speed port scanner",
    "zmap":      "Internet-wide scanner",
    # Crypto miners
    "xmrig":     "XMRig Monero miner — strong malware indicator",
    "minerd":    "cpuminer daemon — crypto mining",
    "cryptominer": "generic miner name",
    "ethminer":  "Ethereum miner",
    # Reverse shells / RATs
    "msfconsole": "Metasploit console",
    "msfvenom":  "Metasploit payload generator",
    "empire":    "PowerShell Empire C2 framework",
    "cobalt":    "Cobalt Strike (partial match — also matches cobalt-strike)",
    # Persistence tools
    "crontab":   "crontab modification — check for unexpected scheduling",
    "launchctl": "macOS service launcher — watch for unexpected loads",
}

# ── Suspicious path fragments ─────────────────────────────────────────────────
# Processes running from these directories are unusual and worth calling out.

SUSPICIOUS_PATHS: list[str] = [
    "/tmp/",
    "/var/tmp/",
    "/dev/shm/",
    "/private/tmp/",     # macOS /tmp symlinks here
]

# ── External IP reputation heuristics ────────────────────────────────────────
# Basic heuristics before we even call AbuseIPDB.
# These are not blocklists — just patterns worth flagging in the prompt.

_TOR_EXIT_RANGES: list[str] = []          # populated dynamically if available
_KNOWN_GOOD_CLOUDS: tuple[str, ...] = (   # major CDNs/cloud — don't spam alerts
    "13.", "52.", "54.", "3.",             # AWS us-east
    "35.", "34.", "104.",                  # GCP / Cloudflare
    "151.101.",                            # Fastly
    "199.232.",                            # Fastly
)


# ── Rule check functions ──────────────────────────────────────────────────────

def check_network_rules(
    ports: list[int],
    ext_ips: list[str],
) -> list[str]:
    """
    Check listening ports and external IPs against hard rules.
    Returns a list of [RULE ALERT] strings (may be empty).
    """
    alerts: list[str] = []

    # Port rules
    for port in ports:
        if port in SUSPICIOUS_PORTS:
            alerts.append(
                f"[RULE ALERT] Port {port} is listening — "
                f"{SUSPICIOUS_PORTS[port]}. Verify this is intentional."
            )

    # External IP heuristics — unusual port ranges in ESTABLISHED connections
    for conn in ext_ips:
        # conn format is "host:port" from netstat parsing
        parts = conn.rsplit(":", 1)
        if len(parts) == 2 and parts[1].isdigit():
            port = int(parts[1])
            host = parts[0]
            # Outbound to Tor default ports
            if port in (9001, 9030, 9050, 9051):
                alerts.append(
                    f"[RULE ALERT] Outbound connection to {host}:{port} — "
                    f"this is a Tor relay/proxy port."
                )
            # Outbound to IRC (unencrypted)
            if port in (6667, 6668, 6669):
                alerts.append(
                    f"[RULE ALERT] Outbound IRC connection to {host}:{port} — "
                    f"IRC is often used by older botnets for C2."
                )

    return alerts


def check_process_rules(
    proc_names: list[str],
    proc_details: list[dict] | None = None,
) -> list[str]:
    """
    Check running process names against the suspicious-name list.
    proc_details: optional list of psutil info dicts for path checking.
    Returns a list of [RULE ALERT] strings (may be empty).
    """
    alerts: list[str] = []
    seen: set[str] = set()

    name_lower_map = {name.lower(): name for name in proc_names}

    for suspect_name, reason in SUSPICIOUS_PROC_NAMES.items():
        # Exact match
        if suspect_name in name_lower_map and suspect_name not in seen:
            actual = name_lower_map[suspect_name]
            alerts.append(
                f"[RULE ALERT] Process '{actual}' is running — {reason}"
            )
            seen.add(suspect_name)
        else:
            # Substring match (for partial names like "cobalt")
            for lname, actual in name_lower_map.items():
                if suspect_name in lname and suspect_name not in seen:
                    alerts.append(
                        f"[RULE ALERT] Process '{actual}' matches suspicious pattern "
                        f"'{suspect_name}' — {reason}"
                    )
                    seen.add(suspect_name)
                    break

    # Path-based checks
    if proc_details:
        for info in proc_details:
            try:
                exe = str(info.get("exe", "") or "")
                name = info.get("name", "?")
                for sus_path in SUSPICIOUS_PATHS:
                    if exe.startswith(sus_path):
                        key = f"path:{exe}"
                        if key not in seen:
                            alerts.append(
                                f"[RULE ALERT] Process '{name}' is running from "
                                f"suspicious path '{exe}' — executables in {sus_path} "
                                f"are a common persistence/dropper location."
                            )
                            seen.add(key)
            except Exception:
                pass

    return alerts


def format_rule_alerts(alerts: list[str]) -> str:
    """
    Format a list of rule alert strings into a block suitable for LLM injection.
    Returns empty string if no alerts.
    """
    if not alerts:
        return ""
    block = "[RULE-BASED DETECTIONS — verify each before acting]\n"
    block += "\n".join(f"  • {a}" for a in alerts)
    return block


# ── Smoke test ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== Rules smoke test ===\n")

    net_alerts = check_network_rules(
        ports=[22, 80, 443, 4444, 9050],
        ext_ips=["104.16.1.1:443", "192.168.1.5:9001"],
    )
    proc_alerts = check_process_rules(["python3", "nc", "xmrig", "Ollama"])

    all_alerts = net_alerts + proc_alerts
    if all_alerts:
        print(format_rule_alerts(all_alerts))
    else:
        print("No alerts fired.")
