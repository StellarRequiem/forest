#!/usr/bin/env python3
"""
Forest Workers v1.1 — Real system data + Ollama analysis
Three blue-team Lvl1 workers that gather actual system state and ask
a local LLM to interpret it. No hardcoded outputs.

v1.1 changes:
  - NetworkWatcher: replaced broken psutil.net_connections() (needs root on macOS)
    with netstat subprocess + per-process psutil fallback
  - NetworkWatcher: upgraded model qwen2:0.5b → qwen2.5:3b for better analysis
  - LogAnomalySpecialist: filter macOS internal service noise before sending to LLM
"""

import subprocess
import re
import warnings
from datetime import datetime
from pathlib import Path
from collections import Counter

import psutil
import ollama

# ── shared helpers ────────────────────────────────────────────────────────────

def _call_llm(model: str, prompt: str, max_tokens: int = 180) -> str:
    """Call Ollama, return trimmed text. Returns fallback string on failure."""
    try:
        resp = ollama.generate(
            model=model,
            prompt=prompt,
            options={"temperature": 0.1, "num_predict": max_tokens},
        )
        return resp.get("response", "").strip()
    except Exception as exc:
        return f"[LLM unavailable: {exc}]"


def _timestamp() -> str:
    return datetime.now().strftime("%H:%M:%S")


# ── Worker 1: NetworkWatcher ──────────────────────────────────────────────────

class NetworkWatcher:
    """
    Gathers live network connection state and asks qwen2.5:3b to flag
    anything worth investigating.

    Data sources (in priority order):
      1. netstat -an  — connection states + listening ports (no root needed)
      2. Per-process psutil — external established IPs (best-effort)
      3. psutil.net_io_counters — I/O totals (always available)
    """

    MODEL = "qwen2.5:3b"
    NAME  = "network_watcher"

    # RFC1918 + loopback prefixes — not interesting as "external"
    _PRIVATE = ("127.", "192.168.", "10.", "172.16.", "172.17.", "172.18.",
                "172.19.", "172.2", "::1", "fe80", "fd", "fc")

    def run(self) -> str:
        snapshot = self._gather()
        prompt = (
            "You are a blue-team network analyst.\n"
            "Review this network snapshot and give a 2–3 sentence assessment.\n"
            "Flag anything unusual: unexpected external IPs, unusual listening ports, "
            "or abnormal connection counts.\n\n"
            f"Snapshot ({_timestamp()}):\n{snapshot}\n\n"
            "Assessment:"
        )
        analysis = _call_llm(self.MODEL, prompt)
        return f"[{self.NAME}] {analysis}"

    def _gather(self) -> str:
        lines = []

        # ── 1. netstat for state counts and listening ports ───────────────────
        state_counts: Counter = Counter()
        listening_ports: list = []
        external_conns: list = []

        try:
            result = subprocess.run(
                ["netstat", "-an", "-p", "tcp"],
                capture_output=True, text=True, timeout=8,
            )
            for line in result.stdout.splitlines():
                parts = line.split()
                if len(parts) < 5:
                    continue
                # macOS netstat columns: Proto Recv-Q Send-Q Local Foreign (state)
                state = parts[-1] if parts[-1].isupper() else ""
                if state:
                    state_counts[state] += 1

                # Listening ports
                if "LISTEN" in line:
                    local = parts[3]
                    port_part = local.rsplit(".", 1)[-1]
                    if port_part.isdigit():
                        listening_ports.append(int(port_part))

                # External established connections
                if "ESTABLISHED" in line and len(parts) >= 5:
                    remote = parts[4]
                    ip_part = remote.rsplit(".", 1)[0]
                    port_part = remote.rsplit(".", 1)[-1]
                    if not any(ip_part.startswith(p) for p in self._PRIVATE):
                        if port_part.isdigit():
                            external_conns.append(f"{ip_part}:{port_part}")

            if state_counts:
                lines.append("Connection states: " + ", ".join(
                    f"{s}={n}" for s, n in sorted(state_counts.items())
                ))
            listening_ports = sorted(set(listening_ports))
            if listening_ports:
                lines.append("Listening ports: " + ", ".join(
                    str(p) for p in listening_ports[:20]
                ))
            if external_conns:
                unique_ext = list(dict.fromkeys(external_conns))[:8]
                lines.append("External connections: " + ", ".join(unique_ext))
            else:
                lines.append("External connections: none detected")

        except Exception as exc:
            lines.append(f"netstat unavailable: {exc}")
            # Fallback to per-process psutil (suppresses deprecation warning)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                st: Counter = Counter()
                for p in psutil.process_iter():
                    try:
                        for c in p.connections(kind="inet"):
                            if c.status:
                                st[c.status] += 1
                    except (psutil.AccessDenied, psutil.NoSuchProcess):
                        pass
                if st:
                    lines.append("Connection states (per-proc): " + ", ".join(
                        f"{s}={n}" for s, n in sorted(st.items())
                    ))

        # ── 2. I/O counters (always available without root) ───────────────────
        try:
            io = psutil.net_io_counters()
            lines.append(
                f"I/O since boot — sent: {io.bytes_sent // 1024:,} KB, "
                f"recv: {io.bytes_recv // 1024:,} KB, "
                f"err_in: {io.errin}, err_out: {io.errout}, "
                f"drop_in: {io.dropin}, drop_out: {io.dropout}"
            )
        except Exception:
            pass

        return "\n".join(lines) if lines else "No network data available."


# ── Worker 2: LogAnomalySpecialist ────────────────────────────────────────────

class LogAnomalySpecialist:
    """
    Pulls recent macOS system log errors/faults and asks phi3:mini to flag
    anomalies. Filters out high-volume macOS internal service noise so the
    LLM sees signal, not noise.
    """

    MODEL = "phi3:mini"
    NAME  = "log_anomaly_specialist"
    MAX_LOG_CHARS = 2000

    # macOS generates thousands of these per minute from internal subsystems.
    # They are not security-relevant and drown out real signals.
    _NOISE_SUBSTRINGS = (
        "CLAvengerObservationReporterService",
        "DCPDPTXController",
        "protectLinkGated",
        "ultra constrained",
        "com.apple.CoreBrightness",
        "com.apple.iokit",
        "com.apple.driver.AppleDisplay",
        "com.apple.WindowServer",
        "CoreAnalytics",
        "com.apple.MobileAsset",
        "com.apple.cloudd",
        "com.apple.nsurlsessiond",
        "ASPStorage",
        "symptomsd",
    )

    def run(self) -> str:
        raw = self._gather_logs()
        prompt = (
            "You are a log analysis expert on a blue team.\n"
            "Review these recent system log entries and give a 2–3 sentence summary.\n"
            "Highlight: repeated errors, crash indicators, authentication failures, "
            "unexpected service restarts, or anything that warrants follow-up.\n"
            "If the logs look clean, say so clearly.\n\n"
            f"Recent logs ({_timestamp()}):\n{raw}\n\n"
            "Analysis:"
        )
        analysis = _call_llm(self.MODEL, prompt)
        return f"[{self.NAME}] {analysis}"

    def _gather_logs(self) -> str:
        # macOS unified log — last 5 minutes, error/fault level
        try:
            result = subprocess.run(
                [
                    "log", "show",
                    "--last", "5m",
                    "--predicate", "messageType == error OR messageType == fault",
                    "--style", "compact",
                ],
                capture_output=True, text=True, timeout=15,
            )
            output = result.stdout.strip()
            if output and len(output) > 50:
                filtered = self._filter_noise(output)
                if len(filtered) > 100:
                    return filtered[-self.MAX_LOG_CHARS:]
                # If filtering removed everything, fall through to report clean
                return "No significant errors in the last 5 minutes (all entries were routine system noise)."
        except Exception:
            pass

        # Fallback: /var/log/system.log
        syslog = Path("/var/log/system.log")
        if syslog.exists():
            try:
                text = syslog.read_text(errors="replace")
                return self._filter_noise(text)[-self.MAX_LOG_CHARS:]
            except Exception:
                pass

        return "Log access unavailable — system log requires elevated permissions."

    def _filter_noise(self, raw: str) -> str:
        """Drop lines that contain known macOS internal noise substrings."""
        lines = raw.splitlines()
        kept  = [
            line for line in lines
            if not any(noise in line for noise in self._NOISE_SUBSTRINGS)
        ]
        return "\n".join(kept)


# ── Worker 3: ThreatPatternDetector ──────────────────────────────────────────

class ThreatPatternDetector:
    """
    Samples running processes (top CPU + memory consumers) and asks
    phi3:mini to assess whether any look suspicious or anomalous.
    """

    MODEL = "phi3:mini"
    NAME  = "threat_pattern_detector"

    def run(self) -> str:
        snapshot = self._gather()
        prompt = (
            "You are a threat detection analyst.\n"
            "Review these running processes and give a 2–3 sentence assessment.\n"
            "Flag: unusually high CPU or memory usage, unfamiliar process names, "
            "or patterns that could indicate malware, cryptomining, or compromise.\n\n"
            f"Process snapshot ({_timestamp()}):\n{snapshot}\n\n"
            "Threat assessment:"
        )
        analysis = _call_llm(self.MODEL, prompt)
        return f"[{self.NAME}] {analysis}"

    def _gather(self) -> str:
        lines = []

        # Collect process info
        procs = []
        for p in psutil.process_iter(["pid", "name", "cpu_percent",
                                       "memory_percent", "username", "status"]):
            try:
                info = p.info
                if info["cpu_percent"] is not None:
                    procs.append(info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        # Top 10 by CPU
        top_cpu = sorted(procs, key=lambda x: x.get("cpu_percent") or 0,
                         reverse=True)[:10]
        lines.append("Top CPU consumers:")
        for p in top_cpu:
            lines.append(
                f"  {p['name'][:30]:<30} pid={p['pid']:<7} "
                f"cpu={p['cpu_percent']:>5.1f}%  mem={p.get('memory_percent', 0):>4.1f}%  "
                f"user={p.get('username', '?')}"
            )

        # Top 5 by memory
        top_mem = sorted(procs, key=lambda x: x.get("memory_percent") or 0,
                         reverse=True)[:5]
        lines.append("\nTop memory consumers:")
        for p in top_mem:
            lines.append(
                f"  {p['name'][:30]:<30} mem={p.get('memory_percent', 0):>4.1f}%"
            )

        # System-wide resource summary
        try:
            cpu_all = psutil.cpu_percent(interval=0.5)
            mem     = psutil.virtual_memory()
            lines.append(
                f"\nSystem: CPU={cpu_all:.1f}%  "
                f"RAM used={mem.percent:.1f}%  "
                f"available={mem.available // (1024**2)} MB"
            )
        except Exception:
            pass

        # Count processes per user (spot unusual user activity)
        user_counts = Counter(p.get("username", "?") for p in procs)
        lines.append("Process owners: " + ", ".join(
            f"{u}={n}" for u, n in user_counts.most_common(5)
        ))

        return "\n".join(lines)


# ── Registry (used by cus_langgraph) ─────────────────────────────────────────

WORKER_REGISTRY = {
    "network_watcher":       NetworkWatcher,
    "log_anomaly_specialist": LogAnomalySpecialist,
    "threat_pattern_detector": ThreatPatternDetector,
}


# ── Quick smoke-test ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== Forest Workers v1.0 — smoke test ===\n")
    for name, cls in WORKER_REGISTRY.items():
        print(f"--- {name} ---")
        result = cls().run()
        print(result)
        print()
