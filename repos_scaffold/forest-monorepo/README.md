# Forest — Complete Blue-Team AI Agent Orchestration

![Version](https://img.shields.io/badge/version-1.0.0--alpha-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)
![License](https://img.shields.io/badge/license-MIT-purple)

**Forest** is a complete, production-ready blue-team AI agent orchestration platform with human-gated decision-making, automated code generation, and comprehensive monitoring.

## Quick Start

### Installation

```bash
pip install forest
```

Or install individual components:
```bash
pip install forest-core          # CUS orchestration
pip install forest-training      # Code generation & training
pip install forest-network       # Network monitoring
pip install forest-audit         # Compliance logging
pip install forest-dashboard     # Real-time visualization
```

### Basic Usage

```python
from forest_core import get_headmaster, get_enforcer, get_brain

# Initialize
headmaster = get_headmaster()
enforcer = get_enforcer()
brain = get_brain()

# Spawn agents
agents = headmaster.spawn_agent(tier=2, role="scanner", count=3)

# Approve actions
for agent_id in agents:
    result = enforcer.approve_action(agent_id, "scan network")
    print(f"Approved: {result['approved']}")

# Grade agents
for agent_id in agents:
    grade = brain.grade_agent(agent_id, task_score=85)
    print(f"Grade: {grade['action']}")
```

## Components

### 1. forest-core
**CUS Orchestration Engine**
- Headmaster (tier 4) - orchestration
- Enforcer (tier 3) - policy enforcement
- Brain (tier 3) - grading and credentialing
- Level 1 Workers - task execution
- Decision middleware with full audit trail

[Repository](https://github.com/forest-ai/forest-core) | [Docs](./forest-core/README.md)

### 2. forest-training
**Automated Code Generation & Model Management**
- Code generator (Ollama + template fallback)
- Code validator (security + quality checks)
- Training loop (with convergence detection)
- Model manager (registry + versioning)
- GitHub Actions CI/CD

[Repository](https://github.com/forest-ai/forest-training) | [Docs](./forest-training/README.md)

### 3. forest-network
**Network Monitoring & Anomaly Detection**
- ARP scanning and device discovery
- Device classification
- Anomaly detection
- Prometheus metrics export

[Repository](https://github.com/forest-ai/forest-network) | [Docs](./forest-network/README.md)

### 4. forest-audit
**Compliance & Tamper-Evidence Logging**
- Cryptex chains (SHA-256 hashing)
- Append-only audit logs
- Tamper-evidence validation
- SOC2-ready compliance

[Repository](https://github.com/forest-ai/forest-audit) | [Docs](./forest-audit/README.md)

### 5. forest-dashboard
**Real-Time Decision Visualization**
- Live decision timeline
- Enforcer approval metrics
- Brain grading distribution
- Decision flow diagrams
- Agent-level details

[Repository](https://github.com/forest-ai/forest-dashboard) | [Docs](./forest-dashboard/README.md)

## Architecture

```
Forest Platform
├── Core Layer (forest-core)
│   ├── Decision Middleware
│   ├── CUS Orchestration
│   ├── Enforcer Gateway
│   └── Brain (Grading)
├── Training Layer (forest-training)
│   ├── Code Generation
│   ├── Validation
│   ├── Training Loop
│   └── Model Management
├── Monitoring Layer (forest-network + forest-audit)
│   ├── Network Scanner
│   ├── Anomaly Detection
│   └── Audit Logging
└── UI Layer (forest-dashboard)
    └── Streamlit Dashboard
```

## Key Features

- 🎯 **Human-Gated**: All agent spawning requires approval
- 🤖 **Automated Code Gen**: Generate agent code from specs
- 📊 **Full Audit Trail**: Every decision logged and queryable
- 🔒 **Tamper-Evidence**: SHA-256 hashed decision chains
- 📈 **Real-Time Monitoring**: Live dashboard with metrics
- 🚀 **CI/CD Ready**: GitHub Actions integration
- 📦 **Model Management**: Versioning and deployment tracking
- 🛡️ **Security First**: Validation, policy enforcement, read-only ops

## Quick Links

- [Documentation](./docs/)
- [Examples](./examples/)
- [API Reference](./docs/api.md)
- [Contributing](./CONTRIBUTING.md)

## Installation Options

### Option 1: Full Platform
```bash
pip install forest
```

### Option 2: Custom Selection
```bash
pip install forest-core forest-dashboard
```

### Option 3: Development
```bash
git clone https://github.com/forest-ai/forest.git
cd forest
pip install -e ".[dev]"
```

## Usage Examples

### Example 1: Basic Orchestration
```python
from forest_core import get_headmaster, get_enforcer

headmaster = get_headmaster()
enforcer = get_enforcer()

# Spawn agents
agents = headmaster.spawn_agent(tier=2, role="scanner", count=3)

# Approve actions
for agent in agents:
    enforcer.approve_action(agent, "scan network 10.0.0.0/8")
```

### Example 2: Generate & Train Agents
```python
from forest_training import CodeGenerator, TrainingLoop

gen = CodeGenerator()
spec = {
    'name': 'threat_detector',
    'tier': 2,
    'role': 'threat detection',
    'capabilities': ['scan', 'classify', 'alert'],
    'behavior': 'Detect threats',
    'constraints': ['Read-only']
}

result = gen.generate_from_spec(spec)
training = TrainingLoop('threat_detector')
training_result = training.run(spec)
```

### Example 3: Monitor & Visualize
```bash
streamlit run -m forest_dashboard.app
# Open http://localhost:8501
```

## Requirements

- Python 3.10+
- LangChain >= 0.1.0
- Ollama >= 0.1.0 (optional)
- Streamlit >= 1.20.0

## Testing

```bash
# Test all components
pytest tests/

# Test individual packages
pip install forest-core
pytest $(python -c "import forest_core; print(forest_core.__path__[0])")
```

## Deployment

### Docker
```bash
docker-compose up
```

### Kubernetes
```bash
kubectl apply -f k8s/
```

### Streamlit Cloud
```bash
git push
```

## Support & Community

- 📖 [Documentation](https://forest-ai.dev)
- 💬 [GitHub Discussions](https://github.com/forest-ai/forest/discussions)
- 🐛 [Issue Tracker](https://github.com/forest-ai/forest/issues)
- 📧 [Email](mailto:forest@example.com)

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](./CONTRIBUTING.md)

## License

MIT - See [LICENSE](./LICENSE)

## Roadmap

- ✅ Phase 1: Core architecture & middleware
- ✅ Phase 2: Decision middleware integration
- ✅ Phase 3: Code generation & training pipeline
- ✅ Phase 4: Repository extraction & packaging
- ⏳ Phase 5: Docker & Kubernetes deployment
- 🔮 Phase 6: Advanced monitoring & ML integration
- 🔮 Phase 7: Red-team module (offensive capabilities)

## Citation

If you use Forest in your research or production system, please cite:

```bibtex
@software{forest2026,
  title={Forest: Blue-Team AI Agent Orchestration},
  author={Forest AI Contributors},
  year={2026},
  url={https://github.com/forest-ai/forest}
}
```

---

**Built with ❤️ for blue-team security automation**
