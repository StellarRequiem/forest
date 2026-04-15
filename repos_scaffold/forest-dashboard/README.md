# forest-dashboard

![Build](https://github.com/forest-ai/forest-dashboard/workflows/tests/badge.svg)
![Version](https://img.shields.io/badge/version-1.0.0--alpha-blue)

**Forest Dashboard — Real-Time Decision Visualization**

Streamlit-based monitoring dashboard for real-time visualization of agent decisions, enforcer approvals, brain grading, and network activity.

## Features

- 📊 **Live Decision Timeline**: Real-time decision stream
- 🔒 **Enforcer Panel**: Approval/block rates and recent blocks
- 🧠 **Brain Panel**: Agent grading distribution and promotion rates
- 🔀 **Decision Flow**: Sankey diagram of routing decisions
- 📈 **Charts & Metrics**: Plotly-based interactive visualizations
- 🤖 **Agent Details**: Per-agent decision history
- 🎯 **Multi-Tab UI**: Timeline, Enforcer, Brain, Flow, Agents

## Installation

```bash
pip install forest-dashboard
```

## Quick Start

```bash
streamlit run -m forest_dashboard.app
```

Then open: `http://localhost:8501`

## Features

### Timeline Tab
- Real-time decision stream
- Color-coded by status (PENDING, APPROVED, EXECUTED, BLOCKED, REVERSED)
- Sortable and searchable

### Enforcer Tab
- Approval rate gauge
- Approve vs. block pie chart
- Recent blocks list
- Approval statistics

### Brain Tab
- Grading distribution (Promoted/Study/Recycled)
- Agent performance metrics
- Promotion rates
- Recent grades

### Flow Tab
- Decision routing Sankey diagram
- Decision types distribution
- Complete flow visualization

### Agents Tab
- Agent selector
- Per-agent decision history
- Agent statistics (total decisions, success rate)
- Decision timeline per agent

## Deployment

### Docker
```bash
docker build -t forest-dashboard .
docker run -p 8501:8501 forest-dashboard
```

### Kubernetes
```bash
kubectl apply -f k8s/deployment.yaml
```

### Streamlit Cloud
```bash
git push
# Streamlit automatically deploys on push
```

## Configuration

`streamlit_config.toml`:
```toml
[theme]
primaryColor = "#667eea"
backgroundColor = "#0f1419"
secondaryBackgroundColor = "#31333d"

[server]
port = 8501
headless = true
```

## API Integration

Dashboard connects to Forest Core middleware:

```python
from forest_core import get_middleware
from forest_dashboard.providers import DecisionTimelineProvider

middleware = get_middleware()
provider = DecisionTimelineProvider()

# All data flows from middleware
data = provider.get_dashboard_data()
```

## Requirements

- Python 3.10+
- Streamlit >= 1.20.0
- Plotly >= 5.0.0
- forest-core >= 1.0.0-alpha

## Testing

```bash
pytest tests/
streamlit run app.py --logger.level=debug
```

## Documentation

- [UI Guide](docs/ui.md)
- [Customization](docs/customization.md)
- [Deployment](docs/deployment.md)

## License

MIT
