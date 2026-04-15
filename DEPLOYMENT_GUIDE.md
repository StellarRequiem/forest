# Phase 5: Docker & Kubernetes Deployment Guide

## Quick Start

### Local Development with Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f forest-core

# Stop all services
docker-compose down
```

### Build Specific Images

```bash
# Build forest-core
docker build -f docker/Dockerfile.core -t forest-core:1.0.0-alpha .

# Build all
for dockerfile in docker/Dockerfile.*; do
  image=$(basename $dockerfile | sed 's/Dockerfile\.//' | sed 's/.*/forest-&/')
  docker build -f $dockerfile -t $image:1.0.0-alpha .
done
```

---

## Kubernetes Deployment

### Prerequisites

```bash
# Check kubectl
kubectl version --client

# Check cluster
kubectl cluster-info

# Verify DNS
kubectl run -it --rm debug --image=busybox --restart=Never -- nslookup kubernetes.default
```

### Deploy to Kubernetes

```bash
# 1. Create namespace and config
kubectl apply -f k8s/00-namespace-config.yaml

# 2. Deploy infrastructure (Postgres, Redis, Ollama)
kubectl apply -f k8s/01-infrastructure.yaml

# 3. Deploy Forest services
kubectl apply -f k8s/02-forest-services.yaml

# 4. Deploy network and ingress
kubectl apply -f k8s/03-network-and-ingress.yaml

# 5. Deploy monitoring and policies
kubectl apply -f k8s/04-monitoring-and-policies.yaml
```

### Verify Deployment

```bash
# Watch deployment progress
kubectl get pods -n forest -w

# Check service status
kubectl get svc -n forest

# View logs
kubectl logs -n forest -f deployment/forest-core

# Port forward for dashboard
kubectl port-forward -n forest svc/forest-dashboard 8501:8501
# Open http://localhost:8501
```

---

## Service Architecture

### Services & Replicas

| Service | Type | Replicas | Port | Resources |
|---------|------|----------|------|-----------|
| forest-core | Deployment | 3 | 8000 | 512Mi / 1Gi |
| forest-training | Deployment | 1 | 8001 | 1Gi / 2Gi |
| forest-network | DaemonSet | N (one per node) | 9090 | 256Mi / 512Mi |
| forest-audit | StatefulSet | 1 | 8002 | 512Mi / 1Gi |
| forest-dashboard | Deployment | 1 | 8501 | 512Mi / 1Gi |
| postgres | StatefulSet | 1 | 5432 | 256Mi / 512Mi |
| redis | StatefulSet | 1 | 6379 | 128Mi / 256Mi |
| ollama | StatefulSet | 1 | 11434 | 1Gi / 2Gi |

### High Availability

- **forest-core**: 3 replicas with PodAntiAffinity (spread across nodes)
- **forest-dashboard**: 1 replica with HPA (scale 1-3)
- **forest-audit**: 1 replica with persistent volume
- **PodDisruptionBudgets**: Ensure at least 1 forest-core pod always running

### Networking

- **ClusterIP**: forest-core, forest-training, forest-audit (internal only)
- **LoadBalancer**: forest-dashboard (external access)
- **Ingress**: Optional routing to all services
- **NetworkPolicy**: Pod-to-pod and external access control

---

## Storage

### Persistent Volumes

| Volume | Size | Purpose | Type |
|--------|------|---------|------|
| postgres-storage | 10Gi | Database | StatefulSet |
| redis-storage | 5Gi | Cache | StatefulSet |
| ollama-storage | 20Gi | Models | StatefulSet |
| forest-vault-pvc | 5Gi | Shared vault | RWMany |
| audit-logs-pvc | 10Gi | Audit trail | RWOnce |

### Access Modes

- **ReadWriteOnce**: postgres, redis, ollama, audit-logs (StatefulSet)
- **ReadWriteMany**: forest-vault (shared across pods)

---

## Monitoring

### Prometheus Metrics

- Port: 9090 (forest-network exposes metrics)
- ServiceMonitor: Enabled for prometheus-operator
- Scrape interval: 30s

### Health Checks

All pods have:
- **Liveness probes**: Restart if unhealthy
- **Readiness probes**: Remove from service if not ready
- **Startup probes**: Allow time for initialization

### Logs

```bash
# View all logs
kubectl logs -n forest -f deployment/forest-core

# View specific pod
kubectl logs -n forest forest-core-abc123

# Stream all containers
kubectl logs -n forest -f deployment/forest-core --all-containers=true
```

---

## Scaling

### Manual Scaling

```bash
# Scale forest-core to 5 replicas
kubectl scale deployment forest-core -n forest --replicas=5

# Scale forest-training to 2 (for redundancy)
kubectl scale deployment forest-training -n forest --replicas=2
```

### Automatic Scaling (HPA)

```bash
# Check HPA status
kubectl get hpa -n forest

# Describe HPA
kubectl describe hpa forest-core-hpa -n forest

# Watch HPA scaling
watch kubectl get hpa -n forest
```

---

## Troubleshooting

### Pod won't start

```bash
# Check pod status
kubectl describe pod -n forest forest-core-abc123

# View events
kubectl get events -n forest --sort-by='.lastTimestamp'

# Check logs
kubectl logs -n forest forest-core-abc123
```

### Service not accessible

```bash
# Check service
kubectl get svc -n forest
kubectl describe svc forest-core -n forest

# Check endpoints
kubectl get endpoints -n forest

# Test connectivity from pod
kubectl run -it --rm debug --image=busybox --restart=Never -- \
  wget -O- http://forest-core:8000/health
```

### Storage issues

```bash
# Check PVC status
kubectl get pvc -n forest
kubectl describe pvc forest-vault-pvc -n forest

# Check PV status
kubectl get pv

# Check node disk space
kubectl top nodes
```

### Resource issues

```bash
# Check node resources
kubectl top nodes
kubectl describe node <node-name>

# Check pod resources
kubectl top pod -n forest
```

---

## Debugging

### Enable Debug Logging

```bash
# Update ConfigMap
kubectl patch configmap -n forest forest-config -p \
  '{"data":{"LOG_LEVEL":"DEBUG"}}'

# Restart pods
kubectl rollout restart deployment/forest-core -n forest
```

### Port Forwarding

```bash
# Dashboard
kubectl port-forward -n forest svc/forest-dashboard 8501:8501

# Core API
kubectl port-forward -n forest svc/forest-core 8000:8000

# Training API
kubectl port-forward -n forest svc/forest-training 8001:8001
```

### Execute Commands in Pod

```bash
# Shell access
kubectl exec -it -n forest forest-core-abc123 -- /bin/bash

# Run Python command
kubectl exec -n forest forest-core-abc123 -- \
  python -c "from forest_core import get_middleware; m = get_middleware(); print(m.get_stats())"
```

---

## Cleanup

### Delete Deployment

```bash
# Delete all Forest resources
kubectl delete namespace forest

# Or selective delete
kubectl delete deployment forest-core -n forest
kubectl delete statefulset postgres -n forest
```

### Reset Volumes

```bash
# Delete PVC (WARNING: deletes data)
kubectl delete pvc forest-vault-pvc -n forest
```

---

## Production Checklist

- [ ] Images pushed to private registry
- [ ] Secrets managed via vault/sealed-secrets
- [ ] TLS certificates configured (cert-manager)
- [ ] Ingress SSL enabled
- [ ] Resource quotas enforced
- [ ] Network policies active
- [ ] Monitoring/Prometheus configured
- [ ] Backup strategy for PVs
- [ ] Log aggregation (ELK/Loki)
- [ ] Rate limiting/throttling
- [ ] Pod security policies enforced
- [ ] RBAC roles configured

---

## Local Testing with Kind (Kubernetes in Docker)

```bash
# Create cluster
kind create cluster --name forest

# Load images
kind load docker-image forest-core:1.0.0-alpha --name forest
kind load docker-image forest-training:1.0.0-alpha --name forest
# ... repeat for other images

# Deploy
kubectl apply -f k8s/ -n forest

# Cleanup
kind delete cluster --name forest
```

---

## Next Steps

1. **Push images** to registry (Docker Hub, ECR, GHCR)
2. **Configure Ingress** with real domain
3. **Setup Prometheus** for monitoring
4. **Add Loki** for centralized logging
5. **Enable cert-manager** for TLS
6. **Configure autoscaling** policies
7. **Setup backup** for persistent volumes
