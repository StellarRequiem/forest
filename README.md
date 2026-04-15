# Forest CUS — Blue-Team AI Monitoring Swarm

A local-first AI agent framework for blue-team security monitoring. Three specialized workers collect live system data, analyze it with local LLMs via Ollama, and return findings that are graded, constitution-checked, and logged to a tamper-evident audit chain.

No cloud required. Runs entirely on your machine.

---

## What it does

Each **swarm cycle** runs three workers in sequence:

| Worker | Data source | Model |
|---|---|---|
| `network_watcher` | `netstat` — connection states, listening ports, external IPs | qwen2.5:3b |
| `log_anomaly_specialist` | macOS unified log — errors/faults from last 5 minutes | phi3:mini |
| `threat_pattern_detector` | `psutil` — top CPU/memory processes, system load | phi3:mini |

Each worker's output is:
1. **Constitution-checked** — `qwen2.5:3b` at temp 0.0 judges whether output is defensive observation or attack instruction. Blocked outputs are logged and rejected.
2. **Graded** — four dimensions: constitution compliance (45%), usefulness (30%), efficiency (15%), novelty (10%). Scored 0–100.
3. **Saved** to `~/ForestVault/proposals/` as a markdown file for review.
4. **Audited** — every event is SHA-256 hashed and appended to `~/ForestVault/training_chain.json`.

The human gate requires explicit approval (`yes`) before each cycle runs.

---

## Requirements

- macOS (tested) or Linux
- Python 3.10+
- [Ollama](https://ollama.ai) running locally with these models pulled:
  ```bash
  ollama pull qwen2.5:3b
  ollama pull phi3:mini
  ollama pull qwen2:0.5b
  ```
- Python dependencies (install into venv):
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  ```

---

## Quick start

```bash
git clone https://github.com/YOUR_USERNAME/forest.git
cd forest

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start Ollama (if not already running)
ollama serve &

# Run one monitoring cycle
echo "yes" | python3 core/cus_langgraph.py
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
│   ├── workers.py              Three real worker classes (network, log, threat)
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
│   └── audit.py                SHA-256 chain verifier
├── bin/
│   ├── forest-dash             Shell launcher for Streamlit dashboard
│   ├── forest-review           Shell launcher for review tool
│   └── forest-audit            Shell launcher for audit tool
├── ForestSuite/                Blue-team trainer applications (Tkinter, standalone)
└── requirements.txt
```

---

## Architecture

```
Headmaster  →  scan tmux sessions, check for dangerous processes
    ↓
Supervisor  →  HUMAN GATE: operator types "yes" to approve
    ↓
Workers (3, sequential)
    ├─ network_watcher       gather netstat data → LLM analysis
    ├─ log_anomaly_specialist gather system logs → LLM analysis
    └─ threat_pattern_detector gather process list → LLM analysis
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
| `phi3:mini` | 2.2 GB | Log analysis, threat assessment |
| `qwen2:0.5b` | 352 MB | Fast fallback |

All models run locally. No API keys, no cloud calls.

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

MIT — see [LICENSE](LICENSE)
