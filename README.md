# 🌲 Forest CUS — AI Agent Orchestration Framework

![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![Version](https://img.shields.io/badge/Version-v5.0-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Docker](https://img.shields.io/badge/Docker-29.4%2B-blue)
![Kubernetes](https://img.shields.io/badge/Kubernetes-1.28%2B-blue)

**Forest** is a production-grade AI agent orchestration framework with **built-in safety, human gates, and tamper-evident audit chains**. Deploy locally with Docker Compose or at scale on Kubernetes.

---

## ✨ Key Features

### 🎯 Core Engine
- **LangGraph State Machine** — 3-tier hierarchy (Headmaster → Supervisor → Workers)
- **3 Lvl1 Agents per cycle** — Network watcher, anomaly specialist, threat detector
- **Credentialed Swarm** — Per-agent credentials + reward ledger
- **Human Gate** — Supervisor approval before each cycle (or idle mode)

### 🔐 Safety-First
- **Constitution Enforcement** — LLM-as-judge (phi3:mini at temp 0.0) blocks harmful outputs
- **Cryptex Tamper-Evidence** — SHA-256 chained audit log (impossible to alter without cascade)
- **Policy Gating** — Enforcer kills suspicious processes, validates all actions
- **Refusal-First Design** — Defaults to safe, requires explicit approval

### 📊 Production-Ready
- **4-Factor Grading** — Constitution (45%) + Usefulness (30%) + Efficiency (15%) + Novelty (10%)
- **Multi-Path Deployment** — Docker Compose (local), Kubernetes (cloud)
- **High Availability** — 3 replicas, anti-affinity, pod disruption budgets
- **Observable** — 274K+ audit events, health checks, Prometheus metrics

### 🚀 Local LLM
- **Ollama Integration** — 14 local models (qwen2, phi3, redteam-llama3.1, mistral, llama3.1)
- **No Cloud Dependency** — Run entirely offline
- **GPU Support** — CUDA 11.8 for fast inference

---

## 🎬 Quick Start

### Local Development (Docker Compose)

```bash
git clone https://github.com/YOUR_USERNAME/forest.git
cd forest

# Start 8-service stack
docker-compose up -d

# Watch logs
docker-compose logs -f forest-core

# Access dashboard
open http://localhost:8501
```

**Services running**:
- Ollama (11434) — LLM inference
- PostgreSQL (5432) — Audit database
- Redis (6379) — Caching
- forest-core (8000) — CUS orchestration
- forest-dashboard (8501) — UI

### Kubernetes (Local with Kind)

```bash
kind create cluster --name forest

kubectl apply -f k8s/
kubectl get pods -n forest -w

# Port forward dashboard
kubectl port-forward -n forest svc/forest-dashboard 8501:8501
open http://localhost:8501
```

### Kubernetes (Production)

```bash
# 1. Push images to registry
docker build -f docker/Dockerfile.core -t myregistry/forest-core:1.0.0 .
docker push myregistry/forest-core:1.0.0
# (repeat for all 5 images)

# 2. Update K8s manifests
sed -i '' 's|forest-core:latest|myregistry/forest-core:1.0.0|g' k8s/*.yaml

# 3. Deploy
kubectl apply -f k8s/
kubectl get svc -n forest forest-dashboard  # Get LoadBalancer IP
```

---

## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    FOREST CUS SWARM                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  [HEADMASTER] → Enforcer Scan → [SUPERVISOR] ← Human Gate       │
│                                                    ↓ (Approved)   │
│                              [WORKER TIER] (3 Lvl1 Agents)       │
│                                  ├─ network_watcher              │
│                                  ├─ log_anomaly_specialist       │
│                                  └─ threat_pattern_detector      │
│                                    ↓                              │
│                              [GRADING ENGINE]                    │
│                              • Constitution: 45%                 │
│                              • Usefulness: 30%                   │
│                              • Efficiency: 15%                   │
│                              • Novelty: 10%                      │
│                                    ↓                              │
│                          [CRYPTEX CHAIN] (SHA-256)               │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Components

| Component | Version | Purpose |
|-----------|---------|---------|
| **cus_core.py** | v5.0 | CUS orchestration brain |
| **cus_langgraph.py** | v4.0 | LangGraph state machine |
| **enforcer.py** | v3.0 | Constitution gatekeeper |
| **grading_engine.py** | v1.0 | Weighted scoring system |
| **meta_harness_runner.py** | v4.2 | Self-improvement wrapper |
| **forest_brain.py** | v2.2 | Credentialing + rewards |

---

## 📦 Deployment Options

### Docker Compose (8 Services)
- ✅ Local development
- ✅ Standalone production (single host)
- ✅ CI/CD testing
- **File**: `docker-compose.yml`

### Kubernetes (5 Manifests, 33 Resources)
- ✅ Multi-node production
- ✅ High availability
- ✅ Auto-scaling (HPA)
- ✅ Pod disruption budgets
- **Files**: `k8s/00-*.yaml` through `k8s/04-*.yaml`

### GitHub Actions CI/CD
- ✅ Auto-build on push
- ✅ Multi-image matrix (5 images in parallel)
- ✅ Docker Hub / GHCR push
- ✅ Auto-deploy to staging
- **File**: `.github/workflows/docker-build-push.yml`

---

## 🔒 Security

### Constitution Enforcement
```python
# LLM-as-judge blocks harmful outputs
blocks = ["phishing", "malware", "ddos", "jailbreak", "deception"]
# Any match → BLOCKED
# All pass → PROMOTED
```

### Cryptex Tamper-Evidence
```
Entry 1: TIMESTAMP | EVENT_1 | HASH_1
Entry 2: TIMESTAMP | EVENT_2 | HASH_2 (includes HASH_1)
Entry 3: TIMESTAMP | EVENT_3 | HASH_3 (includes HASH_2)
# Impossible to alter Entry 1 without cascading all subsequent hashes
```

### Human Gate
```
Every cycle:
1. Headmaster scans for threats
2. Supervisor requires human approval (or idle)
3. Workers execute only if approved
4. All actions logged to Cryptex
```

---

## 📊 Live Execution Report

**3 cycles executed** (verified production test):

```
✅ Total cycles:        3
✅ Total agents:        9
✅ Promotion rate:      100% (9/9 PROMOTE)
✅ Constitution pass:   100% (0 violations)
✅ Audit events:        274,914+ (tamper-evident)
✅ Cycle time:          ~5-10 seconds
✅ Throughput:          ~18-30 agents/minute
```

See [LIVE_EXECUTION_REPORT.md](LIVE_EXECUTION_REPORT.md) for full details.

---

## 🚀 Deployment Checklist

### Before Deploy
- [ ] Clone repository
- [ ] Install Docker 29.4+
- [ ] Install kubectl 1.28+ (for K8s)
- [ ] Read DEPLOYMENT_GUIDE.md

### Docker Compose
```bash
docker-compose up -d
docker-compose logs -f forest-core
# Verify: curl http://localhost:8000/health
```

### Kubernetes
```bash
kubectl apply -f k8s/
kubectl get pods -n forest -w
kubectl logs -f -n forest deployment/forest-core
# Verify: kubectl describe pod -n forest forest-core-xxx
```

### Post-Deploy
- [ ] Verify all pods running: `kubectl get pods -n forest`
- [ ] Check audit chain: `cat ~/ForestVault/training_chain.json | tail`
- [ ] Test dashboard: `kubectl port-forward svc/forest-dashboard 8501:8501`
- [ ] Monitor metrics: `kubectl top pods -n forest`

---

## 📖 Documentation

| Document | Purpose |
|----------|---------|
| [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) | Setup & troubleshooting |
| [CUS_ARCHITECTURE.md](CUS_ARCHITECTURE.md) | Technical deep-dive |
| [LIVE_EXECUTION_REPORT.md](LIVE_EXECUTION_REPORT.md) | Test results & metrics |
| [PHASE_2_COMPLETE.md](PHASE_2_COMPLETE.md) | Core agents (Phase 2) |
| [PHASE_3_COMPLETE.md](PHASE_3_COMPLETE.md) | Training pipeline (Phase 3) |
| [PHASE_4_COMPLETE.md](PHASE_4_COMPLETE.md) | GitHub repos (Phase 4) |
| [PHASE_5_COMPLETE.md](PHASE_5_COMPLETE.md) | Docker/K8s (Phase 5) |

---

## 🎓 What's Included

### Core Modules (90 KB)
```
core/
  ├── cus_core.py              CUS orchestration brain
  ├── cus_langgraph.py         LangGraph state machine
  ├── enforcer.py              Constitution gatekeeper
  ├── grading_engine.py        Weighted scoring
  ├── meta_harness_runner.py   Self-improvement wrapper
  └── ...
```

### Agents (Swarm)
```
agents/
  ├── organs/                  LLM-based organs (enforcer, brain, etc.)
  ├── generated/               Auto-generated agents
  └── orchestration/           Swarm coordination
```

### Training Pipeline
```
training/
  ├── generator/               Code generation
  ├── critic/                  Output validation
  ├── grader/                  Scoring engine
  └── scenarios/               Test cases
```

### Blue-Team Trainers (10)
```
ForestSuite/
  ├── phishing_trainer_v5.py
  ├── url_risk_scanner_trainer.py
  ├── dynamic_trainer_v6.py
  ├── password_hygiene_trainer.py
  ├── network_log_analyzer_trainer.py
  ├── dns_risk_analyzer_trainer.py
  ├── file_integrity_trainer.py
  ├── incident_response_trainer.py
  ├── red_team_simulation_trainer.py
  └── email_header_analyzer_trainer.py
```

### Deployment (40 KB)
```
docker/                         5 multi-stage Dockerfiles
docker-compose.yml              8-service local stack
k8s/                            5 manifests, 33 resources
.github/workflows/              CI/CD automation
```

---

## 🛠️ Development

### Setup Local Environment
```bash
git clone https://github.com/YOUR_USERNAME/forest.git
cd forest

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Run Tests
```bash
# Unit tests
python -m pytest tests/unit/

# Integration tests
python -m pytest tests/integration/

# Live swarm execution
python -c "from core.cus_langgraph import run_cus_swarm; run_cus_swarm()"
```

### Build Docker Images
```bash
# Single image
docker build -f docker/Dockerfile.core -t forest-core:dev .

# All images
for df in docker/Dockerfile.*; do
  image=$(basename $df | sed 's/Dockerfile\.//' | sed 's/.*/forest-&/')
  docker build -f $df -t $image:dev .
done
```

---

## 📈 Performance

### Per-Cycle
- **Time**: ~5-10 seconds
- **Workers**: 3 (parallel)
- **Grading**: <1s per agent
- **Memory**: ~100MB

### Throughput
- **18-30 agents/minute** (sustained)
- **274K+ audit events** (immutable chain)
- **100% constitution pass rate** (live test)

### System Resources
- **CPU Peak**: 15% (LLM inference)
- **RAM**: 81% (model cache)
- **Disk**: 29.5 MB per 274K events

---

## 🤝 Contributing

Forest is open-source and welcomes contributions!

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -am "Add feature"`
4. Push to branch: `git push origin feature/my-feature`
5. Submit pull request

### Areas for Contribution
- Additional agent types
- More trainer scenarios
- Enhanced monitoring
- Cloud provider integrations (AWS, GCP, Azure)
- Documentation improvements

---

## 📄 License

MIT License — See [LICENSE](LICENSE) for details

---

## 🙏 Acknowledgments

Built with:
- [LangGraph](https://github.com/langchain-ai/langgraph) — Agent orchestration
- [LangChain](https://github.com/langchain-ai/langchain) — LLM framework
- [Ollama](https://ollama.ai) — Local LLM inference
- [Docker](https://docker.com) — Containerization
- [Kubernetes](https://kubernetes.io) — Orchestration

---

## 📞 Support

- **Issues**: [GitHub Issues](../../issues)
- **Discussions**: [GitHub Discussions](../../discussions)
- **Docs**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **Email**: Contact maintainer

---

## 🚀 Getting Started

**Pick your path:**

### 👤 Single User (Local Dev)
```bash
docker-compose up -d
# Runs locally, no cloud needed
```

### 🏢 Small Team (Kubernetes)
```bash
kind create cluster --name forest
kubectl apply -f k8s/
# High-availability setup
```

### 🌐 Enterprise (Production K8s)
```bash
# Push to your registry
docker build -f docker/Dockerfile.core -t myregistry/forest-core:1.0.0 .
docker push myregistry/forest-core:1.0.0

# Deploy to your cluster
kubectl apply -f k8s/
```

---

## ✅ Verification

After deployment, verify everything works:

```bash
# Check pods
kubectl get pods -n forest

# Check services
kubectl get svc -n forest

# Check audit chain
tail -10 ~/ForestVault/training_chain.json

# Run live cycle
python -c "from core.cus_langgraph import run_cus_swarm; run_cus_swarm()"
```

**Expected output**: ✅ All pods running, all workers promoted, 0 violations

---

**🌲 Ready to deploy? Start with [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) 🌲**
