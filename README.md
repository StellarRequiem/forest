# Forest CUS — Blue-Team AI Monitoring Swarm

A local-first AI agent framework for blue-team security monitoring. Three specialized workers collect live system data, analyze it with local LLMs via Ollama, and return findings that are graded, constitution-checked, and logged to a tamper-evident audit chain.

No cloud required. Runs entirely on your machine.

---

## What it does

Each **swarm cycle** runs three workers in sequence:

| Worker | Data source | Model |
|---|---|---|
| `network_watcher` | `netstat` — connection states, listening ports, external IPs | qwen2.5:3b |
| `log_anomaly_specialist` | macOS unified log — errors/faults from last 5 minutes | llama3.2:3b |
| `threat_pattern_detector` | `psutil` — top CPU/memory processes, system load | llama3.2:3b |
| `semantic_drift_detector` | system fingerprint — ports + process list, embedded + compared | nomic-embed-text |

Each worker's output is:
1. **Constitution-checked** — `qwen2.5:3b` at temp 0.0 judges whether output is defensive observation or attack instruction. Blocked outputs are logged and rejected.
2. **Graded** — four dimensions: constitution compliance (45%), usefulness (30%), efficiency (15%), novelty (10%). Scored 0–100.
3. **Saved** to `~/ForestVault/proposals/` as a markdown file for review.
4. **Audited** — every event is SHA-256 hashed and appended to `~/ForestVault/training_chain.json`.

The human gate requires explicit approval (`yes`) before each cycle runs.

---

## Requirements

- macOS 13+ or Ubuntu 22.04+
- Python 3.10+
- [Ollama](https://ollama.ai) running locally
- 8 GB RAM minimum (16 GB recommended)

---

## Quick start

```bash
git clone https://github.com/StellarRequiem/forest.git
cd forest
bash setup.sh
```

`setup.sh` handles everything: Python venv, dependencies, Ollama install, model pulls, and directory setup. Takes about 5 minutes on a new machine (model downloads dominate).

After setup:
```bash
source venv/bin/activate

# One monitoring cycle
echo "yes" | python3 core/cus_langgraph.py

# Or continuous mode (runs every 30 min, desktop alerts on low scores)
python3 core/cus_langgraph.py --continuous 30 --alert
```

**Optional — threat intel (free):**
```bash
# Sign up at https://www.abuseipdb.com, then:
echo "ABUSEIPDB_API_KEY=your_key_here" >> .env
source .env
```

**Example output:**
```
🌲 Forest CUS LangGraph v5.0
Task : Blue-team monitoring cycle

🔒 HUMAN GATE — cycle requires approval
Approve cycle? > yes

▶ network_watcher (qwen2.5:3b)
  Output: The network snapshot shows 35 established connections, 26 listening ports.
  Port 11434 (Ollama) and 5900 (VNC) are listening — VNC warrants review if unused.
  Grade: 86.2 → PROMOTE

▶ log_anomaly_specialist (phi3:mini)
  Output: Repeated failures in ContinuityCaptureAgent service detected.
  Both warrant investigation for system stability.
  Grade: 86.5 → PROMOTE

▶ threat_pattern_detector (phi3:mini)
  Output: Ollama is the primary memory consumer at 22%. All processes owned by
  llm01. No unfamiliar process names or unusual CPU spikes detected.
  Grade: 90.2 → PROMOTE
```

---

## Dashboard

A Streamlit dashboard provides a live view of swarm data, trainer tools, and audit chain verification.

```bash
./bin/forest-dash
# → http://localhost:8501
```

**Three tabs:**

| Tab | What it shows |
|---|---|
| 🌲 Swarm Monitor | Latest cycle scores, score trend chart, proposal queue, recent audit events |
| 🎯 Trainer Hub | Phishing detection quiz (19 scenarios), URL risk scanner (15 scenarios), password hygiene checker |
| 🔐 Audit Chain | SHA-256 chain integrity check, event breakdown table, scrollable event feed |

**Sidebar** shows live CPU/RAM meters, queue count, and total audit events.

**Via Docker** (starts Ollama + dashboard together):
```bash
docker-compose up -d
# Streamlit → http://localhost:8501
# Ollama API → http://localhost:11434
```

---

## Tools

### Run the dashboard
```bash
./bin/forest-dash              # Streamlit on :8501
```

### Review proposals
```bash
./bin/forest-review              # interactive ranked table
./bin/forest-review --summary    # one-shot table, exit
./bin/forest-review --clear      # archive queue to ~/ForestVault/proposals_archive/
```

### Verify audit chain
```bash
./bin/forest-audit               # verify last 1,000 events
./bin/forest-audit --full        # verify all events
./bin/forest-audit --events      # print recent event log
./bin/forest-audit --tail 500    # verify last N events
```

---

## Project structure

```
Forest/
├── core/
│   ├── cus_langgraph.py        LangGraph state machine (Headmaster → Supervisor → Workers)
│   ├── workers.py              Three worker classes — network, log, threat
│   ├── baseline.py             Known-good snapshot + delta computation
│   ├── rules.py                Hard detection rules (ports, processes, paths)
│   ├── intel.py                AbuseIPDB threat intel + 24h file cache
│   ├── grading_engine.py       LLM-backed 4-factor scoring
│   └── enforcer.py             Constitution gatekeeper
├── agents/organs/
│   ├── enforcer.py             EnforcerTeam v4.0 — qwen2.5:3b judge + deny-list
│   └── forest_brain.py         Agent credentialing + audit chain logging
├── dashboard/
│   ├── app.py                  Streamlit dashboard (3 tabs)
│   └── scenarios.py            Trainer scenario bank (phishing, URL, password)
├── tools/
│   ├── review.py               Proposal queue browser
│   ├── audit.py                SHA-256 chain verifier
│   └── report.py               Score trend report (--days N)
├── bin/
│   ├── forest-dash             Streamlit dashboard launcher
│   ├── forest-review           Proposal queue launcher
│   ├── forest-audit            Audit chain verifier launcher
│   └── forest-report           Score report launcher
├── ForestSuite/                Blue-team trainer applications (Tkinter, standalone)
├── setup.sh                    One-command installer
├── .env.example                Config template (AbuseIPDB key, thresholds)
├── baseline_example.json       Annotated example of ~/ForestVault/baseline.json
└── requirements.txt
```

---

## Detection layers

Each swarm cycle runs three independent detection layers before the LLM writes its assessment:

| Layer | What it does | Requires |
|---|---|---|
| **Baseline delta** | Compares current ports/processes/IPs to your last known-good snapshot. New items are flagged as `[DELTA]`. | First cycle auto-creates the baseline. |
| **Hard rules** | Instant checks against a deny-list of suspicious ports (4444, 31337, etc.), process names (nc, xmrig, etc.), and executable paths (/tmp/). Results injected as `[RULE ALERT]`. | Built-in, no config needed. |
| **Threat intel** | Checks external IPs against AbuseIPDB's reputation database. Results injected as `[INTEL ALERT]` with confidence score. Cached 24 hours. | Free AbuseIPDB API key. |

All three layers feed into the same LLM prompt, so the model sees everything at once and writes a unified assessment.

---

## Architecture

```
Headmaster  →  scan tmux sessions, check for dangerous processes
    ↓
Supervisor  →  HUMAN GATE: operator types "yes" to approve
    ↓
Workers (3, sequential)
    ├─ network_watcher       netstat → baseline delta + rules + intel → LLM
    ├─ log_anomaly_specialist system logs → LLM
    └─ threat_pattern_detector processes → baseline delta + rules → LLM
         ↓ each worker output:
    Constitution check (qwen2.5:3b at temp 0.0)
         ↓ if SAFE:
    Grade (4-factor weighted score)
         ↓
    Save to ~/ForestVault/proposals/
    Log to ~/ForestVault/training_chain.json (SHA-256 hash chain)
```

---

## Audit chain

Every event (agent spawn, grading, constitution check, human gate decision) is appended to `~/ForestVault/training_chain.json` as:

```
2026-04-15T07:11:42 | GRADING_COMPLETED | network_watcher | score=88.2 | ... | Hash: 538c280e74b12eb4
```

The hash covers the full line content. Run `./bin/forest-audit` to verify none have been modified.

---

## Models used

| Model | Size | Role |
|---|---|---|
| `qwen2.5:3b` | 1.9 GB | Network analysis, constitution judge |
| `llama3.2:3b` | 2.0 GB | Log analysis, threat assessment |
| `nomic-embed-text` | 274 MB | Semantic drift detection (embeddings) |
| `qwen2:0.5b` | 352 MB | Fast fallback |

All models run locally. No API keys, no cloud calls.

---

## Hardware recommendations

Forest CUS is tested on a **Mac Mini M4 (16 GB unified memory)**. This is the recommended minimum for running all three workers in parallel without swap pressure.

| RAM | Recommended model config | Performance |
|---|---|---|
| 8 GB | `qwen2:0.5b` for all workers | Functional — slower, lower analysis quality. Disable intel to reduce memory. |
| 16 GB | `qwen2.5:3b` (network) + `phi3:mini` (logs, threat) | **Recommended** — this is the default config. Smooth cycle times ~25–40 sec. |
| 32 GB+ | Upgrade to `qwen2.5:7b` or `mistral:7b` | Better reasoning, fewer missed signals. Swap workers.py model constants. |

**CPU vs Apple Silicon:**
- Apple Silicon (M1–M4): Ollama uses the Neural Engine natively. All models run fast, low fan noise, low power.
- Intel Mac / AMD PC: Models run on CPU via llama.cpp — 2–5× slower on equivalent RAM, louder fans. Still works; just expect longer cycle times.
- NVIDIA GPU (Linux): Ollama uses CUDA automatically. 7B+ models become practical on 8+ GB VRAM.

**To upgrade models** (edit `core/workers.py`):
```python
class NetworkWatcher:
    MODEL = "qwen2.5:7b"   # upgrade from qwen2.5:3b for better network analysis

class LogAnomalySpecialist:
    MODEL = "mistral:7b"   # upgrade from phi3:mini for richer log interpretation

class ThreatPatternDetector:
    MODEL = "mistral:7b"   # upgrade from phi3:mini for better threat reasoning
```
Then `ollama pull qwen2.5:7b` / `ollama pull mistral:7b`.

---

## Trainer applications

`ForestSuite/` contains standalone blue-team training tools (Tkinter UI):
- **phishing_trainer_v5.py** — spot phishing emails
- **password_hygiene_trainer.py** — evaluate password strength
- **url_risk_scanner_trainer.py** — identify risky URLs
- **dynamic_trainer_v6.py** — dynamic scenario generator

The `dashboard/` tab provides the same training in the web UI without Tkinter.

---

## License

Apache 2.0 — see [LICENSE](LICENSE)
