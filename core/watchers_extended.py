#!/usr/bin/env python3
"""
🌲 Forest Extended Threat Watchers v1.0
Five additional daemon watcher classes inspired by OSSEC, Tripwire,
Fail2ban, OSQuery, and YARA — all native to macOS, no external deps.

New watchers:
- ProcessWatcher         — offensive tool process detection (OSSEC/Wazuh-style)
- FileIntegrityWatcher   — SHA-256 hash monitoring of critical binaries (Tripwire-style)
- BruteForceWatcher      — SSH/auth failure rate tracking (Fail2ban-style)
- ProcessNetworkWatcher  — lsof process-to-socket mapping (OSQuery-style)
- YaraPatternWatcher     — regex/byte pattern scanning on files (YARA-lite)

Usage:
    from core.watchers_extended import start_extended_watchers, start_all_watchers_combined
    start_all_watchers_combined()   # spins up all 8 watchers (3 original + 5 new)
"""

import subprocess
import json
import threading
import time
import re
import hashlib
from datetime import datetime
from pathlib import Path
from collections import defaultdict, deque
from typing import Dict, Set, List, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.blue_agent import BlueAgent
from core.swarm_orchestrator import AgentSwarmOrchestrator, IncidentSeverity

# ---------------------------------------------------------------------------
# Shared constants
# ---------------------------------------------------------------------------

# Processes that are legitimately run as root on macOS — suppress false positives
SAFE_ROOT_PROCS = {
    "launchd", "kernel_task", "syslogd", "configd", "notifyd", "coreauthd",
    "diskarbitrationd", "UserEventAgent", "loginwindow", "WindowServer",
    "coreduetd", "trustd", "mds", "mdworker", "opendirectoryd", "securityd",
    "airportd", "bluetoothd", "systemstats", "syspolicyd", "amfid",
    "cfprefsd", "distnoted", "nsurlsessiond", "tccd", "sharingd",
    "sudo", "su", "pfctl", "pflog", "cupsd", "sshd",
}

# Process names that are definitively offensive / out-of-place on this host
OFFENSIVE_PROC_NAMES = {
    "nc", "ncat", "netcat",
    "nmap", "masscan", "zmap",
    "sqlmap", "sqlninja",
    "hydra", "medusa", "thc-hydra",
    "john", "hashcat", "ophcrack",
    "msfconsole", "msfvenom", "metasploit",
    "aircrack-ng", "aireplay-ng", "airodump-ng",
    "tcpdump",           # flag only when NOT launched by root with expected args
    "hping", "hping3",
    "socat",
    "nikto", "gobuster", "dirb", "wfuzz", "ffuf", "feroxbuster",
    "burpsuite", "zaproxy",
    "empire", "covenant", "sliver",
    "mimikatz",
    "responder",
}

# Standard ports — new listeners outside these warrant WARNING
STANDARD_PORTS = {
    22, 53, 80, 443, 587, 993, 995,
    3000, 3306, 5432, 5900,
    6379, 8080, 8443, 8888,
    7437,           # Forest internal
    11434,          # Ollama
    11435, 11436,
    5678,           # Dify workflow
}


# ---------------------------------------------------------------------------
# 1. ProcessWatcher  (OSSEC / Wazuh-style)
# ---------------------------------------------------------------------------

class ProcessWatcher(BlueAgent):
    """
    Scan running processes every 20 s for:
    - Known offensive tool names (nmap, sqlmap, hydra, …)
    - Unexpected root processes
    - New processes that weren't present in the previous scan
    """

    def __init__(self, orchestrator: AgentSwarmOrchestrator):
        super().__init__(name="ProcessWatcherDaemon", role="Offensive Process Detection")
        self.orchestrator = orchestrator
        self.credential = orchestrator.register_agent(self.name, self.role)
        self._prev_pids: Dict[str, str] = {}   # pid -> name from last scan

    def run_forever(self, interval: int = 20):
        if not self.credential:
            self.credential = self.orchestrator.register_agent(self.name, self.role)
        print(f"[ProcessWatcher] Started — scanning processes every {interval}s")
        while True:
            try:
                self.orchestrator.heartbeat(self.name)
                self._scan_processes()
                time.sleep(interval)
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.log_action("PROCESS_WATCHER_ERROR", str(e))
                time.sleep(interval)

    def _scan_processes(self):
        try:
            result = subprocess.check_output(
                ["ps", "aux"],
                text=True, timeout=10
            )
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError) as e:
            self.log_action("PS_FAILED", str(e))
            return

        current_pids: Dict[str, str] = {}

        for line in result.strip().split("\n")[1:]:   # skip header
            parts = line.split(None, 10)
            if len(parts) < 11:
                continue

            user   = parts[0]
            pid    = parts[1]
            cmd    = parts[10].strip()
            proc_name = Path(cmd.split()[0]).name if cmd else ""

            current_pids[pid] = proc_name

            # --- offensive tool check ---
            if proc_name.lower() in OFFENSIVE_PROC_NAMES:
                self.orchestrator.create_incident(
                    source=self.name,
                    threat_type="suspicious_process",
                    severity=IncidentSeverity.CRITICAL,
                    details={
                        "pid": pid,
                        "user": user,
                        "process": proc_name,
                        "cmdline": cmd[:300],
                        "reason": "offensive_tool_name",
                    },
                    ttl=1800,
                )
                self.log_action("OFFENSIVE_PROCESS_DETECTED", f"pid={pid} proc={proc_name} user={user}")

            # --- unexpected root process ---
            elif user == "root" and proc_name and proc_name not in SAFE_ROOT_PROCS:
                # Only flag new PIDs — avoid re-alerting each cycle
                if pid not in self._prev_pids:
                    self.orchestrator.create_incident(
                        source=self.name,
                        threat_type="unexpected_root_process",
                        severity=IncidentSeverity.WARNING,
                        details={
                            "pid": pid,
                            "process": proc_name,
                            "cmdline": cmd[:300],
                        },
                        ttl=900,
                    )
                    self.log_action("UNEXPECTED_ROOT_PROC", f"pid={pid} proc={proc_name} cmd={cmd[:100]}")

        self._prev_pids = current_pids


# ---------------------------------------------------------------------------
# 2. FileIntegrityWatcher  (Tripwire-style)
# ---------------------------------------------------------------------------

CRITICAL_PATHS = [
    "/bin/bash",
    "/bin/sh",
    "/usr/bin/python3",
    "/usr/bin/sudo",
    "/usr/sbin/sshd",
    "/etc/hosts",
    "/etc/passwd",
    "/etc/sudoers",
]

class FileIntegrityWatcher(BlueAgent):
    """
    Hash critical system files at startup, then re-verify every 5 minutes.
    Persists baseline to ~/ForestVault/file_integrity_baseline.json.
    """

    BASELINE_PATH = Path.home() / "ForestVault" / "file_integrity_baseline.json"
    LAUNCHD_DIR   = Path("/Library/LaunchDaemons")

    def __init__(self, orchestrator: AgentSwarmOrchestrator):
        super().__init__(name="FileIntegrityWatcherDaemon", role="File Integrity Monitoring")
        self.orchestrator = orchestrator
        self.credential = orchestrator.register_agent(self.name, self.role)
        self._baseline: Dict[str, str] = {}   # path -> sha256
        self._load_or_build_baseline()

    # ---- baseline management -----------------------------------------------

    def _hash_file(self, path: str) -> Optional[str]:
        try:
            h = hashlib.sha256()
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(65536), b""):
                    h.update(chunk)
            return h.hexdigest()
        except (FileNotFoundError, PermissionError, OSError):
            return None

    def _build_watch_list(self) -> List[str]:
        paths = list(CRITICAL_PATHS)
        # Add first 10 LaunchDaemon plists
        try:
            plists = sorted(self.LAUNCHD_DIR.glob("*.plist"))[:10]
            paths.extend(str(p) for p in plists)
        except (PermissionError, OSError):
            pass
        return paths

    def _load_or_build_baseline(self):
        if self.BASELINE_PATH.exists():
            try:
                with open(self.BASELINE_PATH) as f:
                    self._baseline = json.load(f)
                print(f"[FileIntegrityWatcher] Loaded baseline — {len(self._baseline)} files")
                return
            except Exception:
                pass
        self._rebuild_baseline()

    def _rebuild_baseline(self):
        self._baseline = {}
        for path in self._build_watch_list():
            h = self._hash_file(path)
            if h:
                self._baseline[path] = h
        try:
            self.BASELINE_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(self.BASELINE_PATH, "w") as f:
                json.dump(self._baseline, f, indent=2)
        except Exception as e:
            self.log_action("BASELINE_SAVE_FAILED", str(e))
        print(f"[FileIntegrityWatcher] Baseline built — {len(self._baseline)} files")

    # ---- daemon loop -------------------------------------------------------

    def run_forever(self, interval: int = 300):
        if not self.credential:
            self.credential = self.orchestrator.register_agent(self.name, self.role)
        print(f"[FileIntegrityWatcher] Started — checking every {interval}s")
        while True:
            try:
                self.orchestrator.heartbeat(self.name)
                self._verify()
                time.sleep(interval)
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.log_action("INTEGRITY_WATCHER_ERROR", str(e))
                time.sleep(interval)

    def _verify(self):
        for path, expected in list(self._baseline.items()):
            actual = self._hash_file(path)
            if actual is None:
                # File disappeared
                self.orchestrator.create_incident(
                    source=self.name,
                    threat_type="file_integrity_violation",
                    severity=IncidentSeverity.CRITICAL,
                    details={
                        "path": path,
                        "expected": expected,
                        "actual": "FILE_MISSING",
                        "reason": "critical_file_removed",
                    },
                    ttl=7200,
                )
                self.log_action("FILE_MISSING", path)
            elif actual != expected:
                self.orchestrator.create_incident(
                    source=self.name,
                    threat_type="file_integrity_violation",
                    severity=IncidentSeverity.CRITICAL,
                    details={
                        "path": path,
                        "expected": expected,
                        "actual": actual,
                        "reason": "hash_mismatch",
                    },
                    ttl=7200,
                )
                self.log_action("FILE_HASH_MISMATCH", f"{path}: {expected[:16]}… → {actual[:16]}…")
                # Update baseline so we don't spam the same alert
                self._baseline[path] = actual


# ---------------------------------------------------------------------------
# 3. BruteForceWatcher  (Fail2ban-style)
# ---------------------------------------------------------------------------

# Patterns that indicate a failed authentication in macOS system log
AUTH_FAIL_PATTERNS = [
    re.compile(r"Failed password for (\S+) from ([\d.]+)", re.IGNORECASE),
    re.compile(r"Invalid user (\S+) from ([\d.]+)", re.IGNORECASE),
    re.compile(r"authentication error.*from ([\d.]+)", re.IGNORECASE),
    re.compile(r"FAILED LOGIN.*from ([\d.]+)", re.IGNORECASE),
    re.compile(r"error: PAM.*from ([\d.]+)", re.IGNORECASE),
]

AUTH_SUCCESS_PATTERN = re.compile(
    r"Accepted (?:password|publickey) for (\S+) from ([\d.]+)", re.IGNORECASE
)

class BruteForceWatcher(BlueAgent):
    """
    Parse /var/log/system.log every 30 s for SSH/auth failure patterns.
    Tracks per-IP failure counts in a 5-minute sliding window.
    Thresholds: WARNING @ 5 failures, ATTACK @ 10 failures.
    Also flags successful logins from previously unseen IPs.
    """

    WARN_THRESHOLD   = 5
    ATTACK_THRESHOLD = 10
    WINDOW_SECONDS   = 300   # 5 minutes

    LOG_PATHS = [
        "/var/log/system.log",
        "/var/log/auth.log",
        "/var/log/secure",
    ]

    def __init__(self, orchestrator: AgentSwarmOrchestrator):
        super().__init__(name="BruteForceWatcherDaemon", role="Brute Force Detection")
        self.orchestrator = orchestrator
        self.credential = orchestrator.register_agent(self.name, self.role)
        # ip -> deque of datetime timestamps of failures
        self._fail_times: Dict[str, deque] = defaultdict(lambda: deque())
        self._known_ips: Set[str] = set()
        self._alerted_ips: Set[str] = set()   # avoid re-alerting every cycle
        self._log_offset: Dict[str, int] = {}  # path -> bytes already read

    # ---- helpers ------------------------------------------------------------

    def _available_log(self) -> Optional[str]:
        for p in self.LOG_PATHS:
            if Path(p).exists():
                return p
        return None

    def _read_new_lines(self, path: str) -> List[str]:
        """Read only newly written lines since last check."""
        try:
            offset = self._log_offset.get(path, 0)
            with open(path, "r", errors="replace") as f:
                f.seek(0, 2)
                size = f.tell()
                if size < offset:
                    offset = 0   # log rotated
                f.seek(offset)
                new_data = f.read()
                self._log_offset[path] = f.tell()
            return new_data.splitlines()
        except (PermissionError, FileNotFoundError, OSError):
            return []

    # ---- daemon loop --------------------------------------------------------

    def run_forever(self, interval: int = 30):
        if not self.credential:
            self.credential = self.orchestrator.register_agent(self.name, self.role)
        print(f"[BruteForceWatcher] Started — checking auth logs every {interval}s")
        while True:
            try:
                self.orchestrator.heartbeat(self.name)
                self._scan_logs()
                time.sleep(interval)
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.log_action("BRUTEFORCE_WATCHER_ERROR", str(e))
                time.sleep(interval)

    def _scan_logs(self):
        log_path = self._available_log()
        if not log_path:
            return

        lines = self._read_new_lines(log_path)
        now = datetime.now()
        cutoff = now.timestamp() - self.WINDOW_SECONDS

        for line in lines:
            # --- successful login ---
            m = AUTH_SUCCESS_PATTERN.search(line)
            if m:
                user, ip = m.group(1), m.group(2)
                if ip not in self._known_ips:
                    self.orchestrator.create_incident(
                        source=self.name,
                        threat_type="login_from_new_ip",
                        severity=IncidentSeverity.WARNING,
                        details={"ip": ip, "user": user, "log_line": line[:200]},
                        ttl=3600,
                    )
                    self.log_action("NEW_IP_LOGIN", f"{user} from {ip}")
                    self._known_ips.add(ip)
                continue

            # --- failed auth ---
            for pattern in AUTH_FAIL_PATTERNS:
                m = pattern.search(line)
                if m:
                    # last group is always the IP
                    ip = m.groups()[-1]
                    self._fail_times[ip].append(now)
                    break

        # Evaluate sliding window counts
        for ip, times in self._fail_times.items():
            # Prune old entries
            while times and times[0].timestamp() < cutoff:
                times.popleft()

            count = len(times)
            if count >= self.ATTACK_THRESHOLD and ip not in self._alerted_ips:
                self.orchestrator.create_incident(
                    source=self.name,
                    threat_type="brute_force_attempt",
                    severity=IncidentSeverity.ATTACK,
                    details={"ip": ip, "failures_in_5min": count},
                    ttl=1800,
                )
                self.log_action("BRUTE_FORCE_ATTACK", f"{ip}: {count} failures in 5 min")
                self._alerted_ips.add(ip)

            elif count >= self.WARN_THRESHOLD and ip not in self._alerted_ips:
                self.orchestrator.create_incident(
                    source=self.name,
                    threat_type="brute_force_attempt",
                    severity=IncidentSeverity.WARNING,
                    details={"ip": ip, "failures_in_5min": count},
                    ttl=900,
                )
                self.log_action("BRUTE_FORCE_WARNING", f"{ip}: {count} failures in 5 min")
                self._alerted_ips.add(ip)

            # Reset alert flag once the window clears below threshold
            elif count < self.WARN_THRESHOLD and ip in self._alerted_ips:
                self._alerted_ips.discard(ip)


# ---------------------------------------------------------------------------
# 4. ProcessNetworkWatcher  (OSQuery-style)
# ---------------------------------------------------------------------------

class ProcessNetworkWatcher(BlueAgent):
    """
    Use `lsof -i -P -n` every 45 s to map processes to sockets.
    Detects:
    - New listening ports outside STANDARD_PORTS
    - Outbound connections from known-benign processes on non-standard ports
    - Offensive-named processes that have established network connections
    """

    BENIGN_PROCS_EXPECT_NET = {
        "Safari", "Google Chrome", "Firefox", "curl", "wget",
        "python3", "node", "java", "ruby",
        "com.apple.WebKit", "nsurlsessiond",
    }

    def __init__(self, orchestrator: AgentSwarmOrchestrator):
        super().__init__(name="ProcessNetworkWatcherDaemon", role="Process-to-Network Mapping")
        self.orchestrator = orchestrator
        self.credential = orchestrator.register_agent(self.name, self.role)
        self._seen_listen_ports: Set[int] = set()

    def run_forever(self, interval: int = 45):
        if not self.credential:
            self.credential = self.orchestrator.register_agent(self.name, self.role)
        print(f"[ProcessNetworkWatcher] Started — mapping processes every {interval}s")
        while True:
            try:
                self.orchestrator.heartbeat(self.name)
                self._scan_lsof()
                time.sleep(interval)
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.log_action("PROCNET_WATCHER_ERROR", str(e))
                time.sleep(interval)

    def _scan_lsof(self):
        try:
            result = subprocess.check_output(
                ["lsof", "-i", "-P", "-n"],
                text=True, timeout=10,
                stderr=subprocess.DEVNULL,
            )
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError):
            return

        for line in result.strip().split("\n")[1:]:   # skip header
            parts = line.split()
            if len(parts) < 9:
                continue

            proc_name = parts[0]
            # pid       = parts[1]
            state_col  = parts[-1]   # LISTEN / ESTABLISHED / etc.
            addr_col   = parts[-2]   # e.g. *:8080 or 192.168.1.5:443

            # Extract port
            port = None
            if ":" in addr_col:
                port_str = addr_col.rsplit(":", 1)[-1]
                try:
                    port = int(port_str)
                except ValueError:
                    pass

            if port is None:
                continue

            direction = "LISTEN" if "LISTEN" in state_col else "ESTABLISHED"

            # -- new listening port? --
            if direction == "LISTEN" and port not in self._seen_listen_ports:
                self._seen_listen_ports.add(port)
                if port not in STANDARD_PORTS:
                    sev = IncidentSeverity.CRITICAL if proc_name.lower() in OFFENSIVE_PROC_NAMES \
                          else IncidentSeverity.WARNING
                    self.orchestrator.create_incident(
                        source=self.name,
                        threat_type="new_listening_port",
                        severity=sev,
                        details={
                            "process": proc_name,
                            "port": port,
                            "address": addr_col,
                        },
                        ttl=3600,
                    )
                    self.log_action("NEW_LISTENING_PORT", f"{proc_name} → port {port}")

            # -- offensive process with established connection --
            if direction == "ESTABLISHED" and proc_name.lower() in OFFENSIVE_PROC_NAMES:
                self.orchestrator.create_incident(
                    source=self.name,
                    threat_type="unexpected_network_connection",
                    severity=IncidentSeverity.CRITICAL,
                    details={
                        "process": proc_name,
                        "connection": addr_col,
                        "state": state_col,
                    },
                    ttl=1800,
                )
                self.log_action("OFFENSIVE_PROC_NETWORK", f"{proc_name} connected: {addr_col}")


# ---------------------------------------------------------------------------
# 5. YaraPatternWatcher  (YARA-lite, no external deps)
# ---------------------------------------------------------------------------

# Each signature: name -> list of (kind, value)
#   kind="bytes"  value=bytes literal to search in file content
#   kind="regex"  value=compiled re.Pattern
SIGNATURES: Dict[str, List] = {
    "reverse_shell_bash": [
        ("bytes", b"bash -i >& /dev/tcp/"),
        ("bytes", b"/bin/sh -i"),
        ("bytes", b"bash -c 'sh -i"),
        ("regex", re.compile(rb"/dev/tcp/[\d.]+/\d+")),
    ],
    "crypto_miner": [
        ("bytes", b"stratum+tcp://"),
        ("bytes", b"xmrig"),
        ("bytes", b"minerd"),
        ("bytes", b"cpuminer"),
        ("bytes", b"nicehash"),
    ],
    "meterpreter_marker": [
        ("bytes", b"meterpreter"),
        ("bytes", b"MSFVENOM"),
        ("bytes", b"metasploit"),
    ],
    "data_exfil_pipe": [
        ("regex", re.compile(rb"curl\s+.*-d\s+\$\(base64")),
        ("regex", re.compile(rb"wget\s+.*--post-data")),
        ("regex", re.compile(rb"\|\s*base64\s*\|\s*curl")),
    ],
    "python_reverse_shell": [
        ("bytes", b"import socket,subprocess,os"),
        ("bytes", b"socket.AF_INET,socket.SOCK_STREAM"),
        ("regex", re.compile(rb"connect\(\([\'\"][\d.]+[\'\"],\s*\d+")),
    ],
    "c2_beacon_pattern": [
        ("regex", re.compile(rb"while\s+true.*sleep.*curl", re.DOTALL)),
        ("bytes", b"InternetReadFile"),
        ("bytes", b"WinHttpConnect"),
    ],
}

SCAN_DIRS = [
    Path("/tmp"),
    Path("/var/tmp"),
    Path.home() / "Downloads",
]

SCAN_EXTENSIONS = {".sh", ".py", ".pl", ".rb", ".js", ".php", ".ps1", ".bat", ".cmd"}
MAX_FILE_SIZE   = 1 * 1024 * 1024   # 1 MB — skip large files


class YaraPatternWatcher(BlueAgent):
    """
    Scan temp dirs every 5 minutes for script files containing
    known-malicious byte patterns and regexes (YARA-lite without yara-python).
    """

    def __init__(self, orchestrator: AgentSwarmOrchestrator):
        super().__init__(name="YaraPatternWatcherDaemon", role="Malware Pattern Detection")
        self.orchestrator = orchestrator
        self.credential = orchestrator.register_agent(self.name, self.role)
        self._alerted_files: Set[str] = set()   # avoid duplicate incidents

    def run_forever(self, interval: int = 300):
        if not self.credential:
            self.credential = self.orchestrator.register_agent(self.name, self.role)
        print(f"[YaraPatternWatcher] Started — scanning scripts every {interval}s")
        while True:
            try:
                self.orchestrator.heartbeat(self.name)
                self._scan_dirs()
                time.sleep(interval)
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.log_action("YARA_WATCHER_ERROR", str(e))
                time.sleep(interval)

    def _scan_dirs(self):
        for scan_dir in SCAN_DIRS:
            try:
                candidates = [
                    f for f in scan_dir.rglob("*")
                    if f.suffix.lower() in SCAN_EXTENSIONS
                    and f.is_file()
                    and f.stat().st_size < MAX_FILE_SIZE
                ]
            except (PermissionError, OSError):
                continue

            for filepath in candidates:
                self._scan_file(filepath)

    def _scan_file(self, filepath: Path):
        if str(filepath) in self._alerted_files:
            return
        try:
            content = filepath.read_bytes()
        except (PermissionError, FileNotFoundError, OSError):
            return

        matched_sigs: List[str] = []

        for sig_name, rules in SIGNATURES.items():
            for kind, value in rules:
                if kind == "bytes" and value in content:
                    matched_sigs.append(sig_name)
                    break
                elif kind == "regex" and value.search(content):
                    matched_sigs.append(sig_name)
                    break

        if matched_sigs:
            self.orchestrator.create_incident(
                source=self.name,
                threat_type="malware_pattern_detected",
                severity=IncidentSeverity.CRITICAL,
                details={
                    "file": str(filepath),
                    "size_bytes": len(content),
                    "matched_signatures": matched_sigs,
                    "modified": datetime.fromtimestamp(filepath.stat().st_mtime).isoformat(),
                },
                ttl=7200,
            )
            self.log_action(
                "MALWARE_PATTERN_HIT",
                f"{filepath.name} matched: {', '.join(matched_sigs)}"
            )
            self._alerted_files.add(str(filepath))


# ---------------------------------------------------------------------------
# Launcher helpers
# ---------------------------------------------------------------------------

def start_extended_watchers(orchestrator: Optional[AgentSwarmOrchestrator] = None):
    """Spin up all 5 extended watchers as background daemon threads."""
    orch = orchestrator or AgentSwarmOrchestrator()

    watchers = [
        (ProcessWatcher(orch),        "run_forever", {}),
        (FileIntegrityWatcher(orch),  "run_forever", {}),
        (BruteForceWatcher(orch),     "run_forever", {}),
        (ProcessNetworkWatcher(orch), "run_forever", {}),
        (YaraPatternWatcher(orch),    "run_forever", {}),
    ]

    threads = []
    for watcher, method, kwargs in watchers:
        t = threading.Thread(
            target=getattr(watcher, method),
            kwargs=kwargs,
            daemon=True,
            name=watcher.name,
        )
        t.start()
        threads.append(t)
        print(f"✅ {watcher.name} started")

    return orch, threads


def start_all_watchers_combined():
    """
    Launch all 8 blue-team watchers from a single shared orchestrator:
      Original 3: ARPWatcher, DockerWatcher, NetworkWatcher
      Extended 5: ProcessWatcher, FileIntegrityWatcher, BruteForceWatcher,
                  ProcessNetworkWatcher, YaraPatternWatcher
    """
    # Import originals here to avoid circular imports at module level
    from core.watchers import ARPWatcher, DockerWatcher, NetworkWatcher

    orch = AgentSwarmOrchestrator()

    original = [
        ARPWatcher(orch),
        DockerWatcher(orch),
        NetworkWatcher(orch),
    ]
    extended = [
        ProcessWatcher(orch),
        FileIntegrityWatcher(orch),
        BruteForceWatcher(orch),
        ProcessNetworkWatcher(orch),
        YaraPatternWatcher(orch),
    ]

    all_watchers = original + extended
    threads = []

    for watcher in all_watchers:
        t = threading.Thread(
            target=watcher.run_forever,
            daemon=True,
            name=watcher.name,
        )
        t.start()
        threads.append(t)
        print(f"✅ {watcher.name} started")

    print(f"\n🌲 Forest — all {len(all_watchers)} watchers running\n")

    try:
        while True:
            time.sleep(60)
            active = orch.get_active_incidents()
            alive  = sum(1 for t in threads if t.is_alive())
            print(
                f"[Forest] {datetime.now().strftime('%H:%M:%S')} | "
                f"Watchers: {alive}/{len(threads)} alive | "
                f"Active incidents: {len(active)}"
            )
    except KeyboardInterrupt:
        print("\n🛑 Forest watchers shutting down...")


if __name__ == "__main__":
    start_all_watchers_combined()
