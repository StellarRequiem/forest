# forest-audit

![Build](https://github.com/forest-ai/forest-audit/workflows/tests/badge.svg)
![Version](https://img.shields.io/badge/version-1.0.0--alpha-blue)

**Forest Audit — Tamper-Evident Compliance Logging**

Cryptex-based tamper-evident audit logging with append-only decision chains, SHA-256 hashing, and compliance query APIs.

## Features

- 🔗 **Cryptex Chains**: SHA-256 hashed decision chains
- 📋 **Append-Only Logs**: Immutable audit trail
- 🔐 **Tamper-Evidence**: Detect log tampering
- 📊 **Query APIs**: Flexible audit log querying
- 📈 **Metrics Export**: Audit statistics and compliance metrics
- ✅ **SOC2 Ready**: Full compliance audit trail

## Installation

```bash
pip install forest-audit
```

## Quick Start

```python
from forest_audit import AuditLogger, Cryptex

# Initialize
logger = AuditLogger()
cryptex = Cryptex()

# Log decision
entry = logger.log_decision(
    agent_id="agent-001",
    action="scan network",
    status="APPROVED",
    hash=cryptex.compute_hash(data)
)

# Verify chain
is_valid = cryptex.verify_chain(entries)
print(f"Chain valid: {is_valid}")

# Query logs
entries = logger.query(agent_id="agent-001", limit=100)
for entry in entries:
    print(f"{entry['timestamp']}: {entry['action']} ({entry['hash']})")
```

## Cryptex Tamper-Evidence

Validates decision chain integrity:

```python
cryptex = Cryptex()

# Each entry includes SHA-256 hash
# Next entry includes hash of previous
# If any entry modified, chain breaks

is_tampered = cryptex.detect_tamper(entries)
if is_tampered:
    print("⚠️ Audit log has been tampered with!")
```

## Deployment

### Docker
```bash
docker build -t forest-audit .
docker run -v /audit:/data forest-audit
```

### Kubernetes
```bash
kubectl apply -f k8s/statefulset.yaml
# Persists audit logs to PVC
```

## Requirements

- Python 3.10+
- forest-core >= 1.0.0-alpha
- No external dependencies (pure Python)

## Testing

```bash
pytest tests/
```

## License

MIT
