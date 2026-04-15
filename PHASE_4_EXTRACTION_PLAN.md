# Phase 4: GitHub Repository Extraction Plan

## 5 Target Repositories

### 1. forest-core
**Purpose**: CUS orchestration engine, Enforcer, Brain, core decision middleware  
**Modules**:
- `core/decision_middleware.py` → Core decision logging
- `core/decision_timeline_provider.py` → Timeline data
- `agents/core/headmaster_integrated.py` → Orchestration
- `agents/organs/enforcer_integrated.py` → Policy gatekeeper
- `agents/organs/forest_brain_integrated.py` → Agent grading
- `core/network/` → Network utilities
- `core/utils/` → Shared utilities

**Dependencies**: langchain, langgraph, ollama, psutil  
**Entry Points**: CUS orchestration, decision middleware, enforcer gating  

---

### 2. forest-training
**Purpose**: Code generation, validation, training loop, model management  
**Modules**:
- `training/generator/code_generator_v3.py` → Code generation
- `training/generator/code_validator.py` → Validation
- `training/training_loop_codegen.py` → Training loop
- `training/model_manager_codegen.py` → Model management
- `training/scenarios/` → Training scenarios
- `training/critic/` → Critic workers
- `training/grader/` → Grading systems

**Dependencies**: langchain, ollama, pandas  
**Entry Points**: Training pipeline, code generation, model management  
**CI/CD**: GitHub Actions for continuous training

---

### 3. forest-network
**Purpose**: Network monitoring, ARP scanning, device classification  
**Modules**:
- `monitors/network/` → Network monitoring
- `core/network/` → Network utilities
- Device detection, anomaly flagging

**Dependencies**: scapy, psutil, requests  
**Entry Points**: Network scanner, device monitor  
**Deployment**: DaemonSet in K8s (runs on all nodes)

---

### 4. forest-audit
**Purpose**: Compliance logging, Cryptex tamper-evidence, audit trails  
**Modules**:
- `audit/` → Audit core
- `ForestVault/` → Persistent audit storage
- Decision logs, tamper-evident chains

**Dependencies**: None (pure Python)  
**Entry Points**: Audit API, log querying  
**Deployment**: StatefulSet with persistent storage

---

### 5. forest-dashboard
**Purpose**: Streamlit UI for decision visualization, monitoring, reporting  
**Modules**:
- `ui/` → All dashboard code
- `ui/forest_decisions_dashboard.py` → Main dashboard
- Charts, timelines, agent details

**Dependencies**: streamlit, plotly, pandas  
**Entry Points**: Streamlit web UI  
**Deployment**: Service with Ingress

---

## Shared Dependencies (forest-shared)

**Module**: Common utilities used by all repos
- Base agent class
- Middleware client
- Common schemas/types
- Logging utilities

**Published**: PyPI or GitHub Releases  
**Version**: Semantic versioning

---

## Extraction Strategy

1. **Create GitHub repos** (empty)
2. **Extract modules** (copy relevant files)
3. **Create setup.py** for each repo
4. **Write README.md** for each repo
5. **Add CI/CD workflows** (.github/workflows/)
6. **Create examples/** directory for each
7. **Tag as v1.0.0-alpha**
8. **Create monorepo** that imports all 5

---

## File Mappings

### forest-core
```
forest_core/
├── forest_core/
│   ├── __init__.py
│   ├── decision_middleware.py
│   ├── decision_timeline_provider.py
│   ├── headmaster.py
│   ├── enforcer.py
│   ├── brain.py
│   └── network/
├── setup.py
├── README.md
├── .github/workflows/
│   └── test.yml
└── examples/
    └── basic_usage.py
```

### forest-training
```
forest_training/
├── forest_training/
│   ├── __init__.py
│   ├── generator.py
│   ├── validator.py
│   ├── training_loop.py
│   ├── model_manager.py
│   └── scenarios/
├── setup.py
├── README.md
├── .github/workflows/
│   ├── test.yml
│   └── train.yml
└── examples/
    └── train_agent.py
```

### forest-network
```
forest_network/
├── forest_network/
│   ├── __init__.py
│   ├── scanner.py
│   ├── monitor.py
│   └── utils/
├── setup.py
├── README.md
├── .github/workflows/
│   └── test.yml
└── examples/
    └── network_scan.py
```

### forest-audit
```
forest_audit/
├── forest_audit/
│   ├── __init__.py
│   ├── audit_logger.py
│   ├── cryptex.py
│   └── query/
├── setup.py
├── README.md
├── .github/workflows/
│   └── test.yml
└── examples/
    └── query_audit.py
```

### forest-dashboard
```
forest_dashboard/
├── forest_dashboard/
│   ├── __init__.py
│   ├── app.py
│   ├── pages/
│   └── components/
├── setup.py
├── README.md
├── .github/workflows/
│   └── test.yml
├── streamlit_config.toml
└── examples/
    └── run_dashboard.py
```

---

## Next Steps

1. Create each repo skeleton locally
2. Generate setup.py for each
3. Write README.md with usage examples
4. Create GitHub Actions workflows
5. Push to GitHub
6. Tag as v1.0.0-alpha
7. Create forest-monorepo that imports all 5
