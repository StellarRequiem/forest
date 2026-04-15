# forest-core

![Build](https://github.com/forest-ai/forest-core/workflows/tests/badge.svg)
![Version](https://img.shields.io/badge/version-1.0.0--alpha-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)

**Forest CUS — Credentialed Unified Swarm**

Core orchestration engine for blue-team AI agents. Features human-gated decision-making, cryptographic credentialing, and full decision audit trails.

## Features

- 🎯 **CUS Orchestration**: Headmaster → Supervisor → Level 1 Workers
- 🔒 **Enforcer Gateway**: Constitutional AI policy enforcement
- 🧠 **Forest Brain**: Agent grading and credentialing
- 📋 **Decision Middleware**: Full audit trail of all decisions
- 📊 **Timeline Provider**: Real-time decision visualization
- 🛡️ **Tamper-Evident Logging**: SHA-256 hashed decision chains

## Installation

```bash
pip install forest-core
```

## Quick Start

```python
from forest_core import get_headmaster, get_enforcer, get_brain

# Get singletons
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

## Architecture

```
Headmaster (Tier 4)
  ├─ Decides agent spawning
  ├─ Routes tasks
  └─ Logs all decisions

Supervisor (Tier 3)
  ├─ Approves spawning
  └─ Human gate

Enforcer (Tier 3)
  ├─ Policy enforcement
  ├─ Approves/blocks actions
  └─ Constitutional AI

Level 1 Workers (Tier 1-2)
  ├─ Execute tasks
  ├─ Log decisions
  └─ Report results

Forest Brain (Tier 3)
  ├─ Grade agents
  ├─ Issue credentials
  └─ Manage rewards
```

## Key Modules

- `decision_middleware.py` - Decision logging and querying
- `decision_timeline_provider.py` - Dashboard data aggregation
- `headmaster.py` - CUS orchestration
- `enforcer.py` - Policy gatekeeper
- `brain.py` - Agent grading and credentialing
- `network/` - Network utilities

## Decision Middleware

All decisions are logged with:
- Unique decision ID
- Timestamp
- Agent ID and action
- Reasoning and metadata
- Status (PENDING/APPROVED/EXECUTED/BLOCKED/REVERSED)
- SHA-256 hash for tamper-evidence

```python
from forest_core import get_middleware

middleware = get_middleware()

# Query decisions
decisions = middleware.get_decisions_by_agent("agent-001", limit=50)
blocked = middleware.get_decisions_by_type(DecisionType.BLOCK)
stats = middleware.get_decision_stats()

# Reverse decision
middleware.reverse_decision(decision_id)
```

## Testing

```bash
pytest tests/
pytest --cov=forest_core tests/
```

## Examples

See `examples/` directory for:
- Basic agent orchestration
- Decision middleware queries
- Enforcer policy enforcement
- Brain grading workflow

## Documentation

- [CUS Architecture](docs/architecture.md)
- [Decision Middleware](docs/middleware.md)
- [API Reference](docs/api.md)

## Requirements

- Python 3.10+
- LangChain >= 0.1.0
- LangGraph >= 0.0.20
- Ollama >= 0.1.0

## License

MIT

## Contributing

Pull requests welcome. Please see CONTRIBUTING.md

## Support

- Issues: [GitHub Issues](https://github.com/forest-ai/forest-core/issues)
- Discussions: [GitHub Discussions](https://github.com/forest-ai/forest-core/discussions)
