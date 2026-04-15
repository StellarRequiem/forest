# Phase 4: GitHub Repository Extraction Guide

## Status: Repository Scaffolds Complete ✅

All 5 repository scaffolds have been created with:
- ✅ setup.py files with proper dependencies
- ✅ README.md with feature descriptions and examples
- ✅ GitHub Actions workflows (.github/workflows/test.yml)
- ✅ Monorepo setup.py that imports all 5

## Repository Structure

```
repos_scaffold/
├── forest-core/
│   ├── setup.py
│   ├── README.md
│   └── .github/workflows/test.yml
├── forest-training/
│   ├── setup.py
│   ├── README.md
│   └── .github/workflows/test.yml
├── forest-network/
│   ├── setup.py
│   ├── README.md
│   └── .github/workflows/test.yml
├── forest-audit/
│   ├── setup.py
│   ├── README.md
│   └── .github/workflows/test.yml
├── forest-dashboard/
│   ├── setup.py
│   ├── README.md
│   └── .github/workflows/test.yml
└── forest-monorepo/
    ├── setup.py
    └── README.md
```

## Next Steps: Pushing to GitHub

### Prerequisites
1. Create GitHub organization: `forest-ai` (or your username)
2. Have git configured with credentials
3. Have GitHub CLI installed (optional, but helpful)

### Step 1: Create GitHub Repositories

Option A - Using GitHub CLI:
```bash
gh repo create forest-ai/forest-core --public --source=. --remote=origin --push
gh repo create forest-ai/forest-training --public --source=. --remote=origin --push
gh repo create forest-ai/forest-network --public --source=. --remote=origin --push
gh repo create forest-ai/forest-audit --public --source=. --remote=origin --push
gh repo create forest-ai/forest-dashboard --public --source=. --remote=origin --push
gh repo create forest-ai/forest --public --source=. --remote=origin --push
```

Option B - Manual (via GitHub web):
1. Go to https://github.com/new
2. Create each repository with public visibility
3. Add description from README

### Step 2: Initialize & Push Each Repo

```bash
# 1. forest-core
cd ~/Forest/repos_scaffold/forest-core
git init
git add .
git commit -m "Initial commit: CUS orchestration engine

- Decision middleware with full audit trail
- Headmaster, Enforcer, Brain orchestration
- LangGraph integration
- v1.0.0-alpha release"
git branch -M main
git remote add origin https://github.com/forest-ai/forest-core.git
git push -u origin main
git tag -a v1.0.0-alpha -m "Alpha release: CUS orchestration"
git push origin v1.0.0-alpha

# 2. forest-training
cd ~/Forest/repos_scaffold/forest-training
git init
git add .
git commit -m "Initial commit: Code generation & model training

- Automated agent code generation (Ollama + template)
- Code validation (security + quality)
- Training loop with convergence detection
- Model management with versioning
- v1.0.0-alpha release"
git branch -M main
git remote add origin https://github.com/forest-ai/forest-training.git
git push -u origin main
git tag -a v1.0.0-alpha -m "Alpha release: Training pipeline"
git push origin v1.0.0-alpha

# 3. forest-network
cd ~/Forest/repos_scaffold/forest-network
git init
git add .
git commit -m "Initial commit: Network monitoring

- ARP scanning and device discovery
- Device classification
- Anomaly detection
- Prometheus metrics export
- v1.0.0-alpha release"
git branch -M main
git remote add origin https://github.com/forest-ai/forest-network.git
git push -u origin main
git tag -a v1.0.0-alpha -m "Alpha release: Network monitoring"
git push origin v1.0.0-alpha

# 4. forest-audit
cd ~/Forest/repos_scaffold/forest-audit
git init
git add .
git commit -m "Initial commit: Compliance & audit logging

- Cryptex tamper-evident chains
- Append-only audit logs
- SHA-256 hashing
- SOC2-ready compliance
- v1.0.0-alpha release"
git branch -M main
git remote add origin https://github.com/forest-ai/forest-audit.git
git push -u origin main
git tag -a v1.0.0-alpha -m "Alpha release: Audit logging"
git push origin v1.0.0-alpha

# 5. forest-dashboard
cd ~/Forest/repos_scaffold/forest-dashboard
git init
git add .
git commit -m "Initial commit: Decision visualization dashboard

- Real-time decision timeline
- Enforcer approval metrics
- Brain grading distribution
- Decision flow diagrams
- Streamlit UI
- v1.0.0-alpha release"
git branch -M main
git remote add origin https://github.com/forest-ai/forest-dashboard.git
git push -u origin main
git tag -a v1.0.0-alpha -m "Alpha release: Dashboard"
git push origin v1.0.0-alpha

# 6. forest-monorepo
cd ~/Forest/repos_scaffold/forest-monorepo
git init
git add .
git commit -m "Initial commit: Forest metapackage

- Pulls all 5 core components
- Single pip install
- v1.0.0-alpha release"
git branch -M main
git remote add origin https://github.com/forest-ai/forest.git
git push -u origin main
git tag -a v1.0.0-alpha -m "Alpha release: Complete platform"
git push origin v1.0.0-alpha
```

### Step 3: Create Release on GitHub

For each repo, create a GitHub Release:

```bash
# Example for forest-core
gh release create v1.0.0-alpha --title "Forest Core v1.0.0-alpha" \
  --notes "Initial alpha release of Forest CUS orchestration engine

## Features
- Decision middleware with full audit trail
- Headmaster, Enforcer, Brain
- LangGraph orchestration
- SHA-256 hashed decisions

## Installation
\`\`\`
pip install forest-core
\`\`\`

## Quick Start
See README.md for examples"
```

### Step 4: Configure PyPI Publishing (Optional)

Create `~/.pypirc`:
```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-AgE...

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-AgE...
```

Publish to PyPI:
```bash
cd ~/Forest/repos_scaffold/forest-core
python -m build
python -m twine upload dist/*
```

### Step 5: Verify Installation

```bash
# Test installation from GitHub
pip install git+https://github.com/forest-ai/forest-core.git@v1.0.0-alpha

# Test monorepo
pip install git+https://github.com/forest-ai/forest.git@v1.0.0-alpha

# Verify imports
python -c "from forest_core import get_middleware; print('✅ forest-core installed')"
python -c "from forest_training import CodeGenerator; print('✅ forest-training installed')"
```

## Complete File Listing

### forest-core/
- setup.py
- README.md
- .github/workflows/test.yml
- forest_core/
  - __init__.py
  - decision_middleware.py (from core/)
  - decision_timeline_provider.py (from core/)
  - headmaster.py (from agents/core/)
  - enforcer.py (from agents/organs/)
  - brain.py (from agents/organs/)

### forest-training/
- setup.py
- README.md
- .github/workflows/test.yml
- forest_training/
  - __init__.py
  - generator.py (from training/generator/)
  - validator.py (from training/generator/)
  - training_loop.py (from training/)
  - model_manager.py (from training/)

### forest-network/
- setup.py
- README.md
- .github/workflows/test.yml
- forest_network/
  - __init__.py
  - scanner.py (from monitors/network/)
  - monitor.py
  - utils/

### forest-audit/
- setup.py
- README.md
- .github/workflows/test.yml
- forest_audit/
  - __init__.py
  - audit_logger.py
  - cryptex.py (from audit/)

### forest-dashboard/
- setup.py
- README.md
- .github/workflows/test.yml
- forest_dashboard/
  - __init__.py
  - app.py (from ui/)
  - pages/
  - components/

### forest-monorepo/
- setup.py
- README.md
- Pulls all 5 repos

## Dependencies Graph

```
forest (monorepo)
├─ forest-core
│  ├─ langchain
│  ├─ langgraph
│  └─ ollama
├─ forest-training
│  ├─ forest-core
│  ├─ langchain
│  └─ ollama
├─ forest-network
│  ├─ forest-core
│  ├─ scapy
│  └─ psutil
├─ forest-audit
│  └─ forest-core
└─ forest-dashboard
   ├─ forest-core
   ├─ streamlit
   └─ plotly
```

## Troubleshooting

### Git remote already exists
```bash
git remote remove origin
git remote add origin https://github.com/forest-ai/forest-core.git
```

### Authentication failed
```bash
# Use personal access token
git config --global credential.helper store
# Then paste token when prompted
```

### PyPI upload fails
```bash
# Check credentials
pip install twine keyring
twine upload --repository pypi dist/*
```

## Next: Phase 5

After pushing all repos to GitHub:

**Phase 5: Docker & Kubernetes** (7-10 days)
- Multi-stage Dockerfiles for each service
- docker-compose.yml for local development
- Kubernetes manifests (Deployments, Services, StatefulSets)
- CI/CD workflows for image build and K8s deployment

## Summary

✅ 5 repositories created locally with:
- Complete setup.py configurations
- Detailed README.md files
- GitHub Actions workflows
- Ready for immediate push to GitHub
- Tagged as v1.0.0-alpha

All scaffolds are in: `~/Forest/repos_scaffold/`

Ready for Phase 5: Docker + Kubernetes deployment!
