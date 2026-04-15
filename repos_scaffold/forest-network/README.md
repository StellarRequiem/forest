# forest-network

![Build](https://github.com/forest-ai/forest-network/workflows/tests/badge.svg)
![Version](https://img.shields.io/badge/version-1.0.0--alpha-blue)

**Forest Network — Blue-Team Network Monitoring**

Network scanning, device classification, and anomaly detection for blue-team security monitoring. Integrates with Forest Core for decision logging.

## Features

- 🔍 **ARP Scanning**: Discover devices on network
- 📊 **Device Classification**: Identify device types (server, workstation, IoT, etc.)
- 🚨 **Anomaly Detection**: Flag unusual network activity
- 📈 **Prometheus Metrics**: Export metrics for monitoring
- 🛡️ **Safe Operations**: Read-only, no network modifications
- 📋 **Decision Logging**: All scans logged via Forest middleware

## Installation

```bash
pip install forest-network
```

## Quick Start

```python
from forest_network import NetworkScanner, DeviceMonitor

# Scan network
scanner = NetworkScanner()
devices = scanner.scan_subnet("192.168.1.0/24")

for device in devices:
    print(f"Device: {device['ip']} ({device['mac']})")
    print(f"  Type: {device['device_type']}")
    print(f"  Status: {device['status']}")

# Monitor for anomalies
monitor = DeviceMonitor()
anomalies = monitor.detect_anomalies(devices)

for anomaly in anomalies:
    print(f"⚠️ {anomaly['type']}: {anomaly['description']}")
```

## Architecture

- **NetworkScanner**: ARP scanning and device discovery
- **DeviceClassifier**: Machine learning device type classification
- **AnomalyDetector**: Statistical anomaly detection
- **MetricsExporter**: Prometheus metrics export

## Integration with Forest Core

All network operations are logged:

```python
from forest_core import get_middleware

middleware = get_middleware()
decisions = middleware.get_decisions_by_agent("network_monitor")
```

## Deployment

### Docker
```bash
docker build -t forest-network .
docker run -it --network host forest-network
```

### Kubernetes
```bash
kubectl apply -f k8s/daemonset.yaml
# Runs on all nodes for comprehensive monitoring
```

## Requirements

- Python 3.10+
- forest-core >= 1.0.0-alpha
- scapy >= 2.5.0
- psutil >= 5.9.0

## Testing

```bash
pytest tests/
```

## License

MIT
