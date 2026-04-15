# 🌲 Forest Project — Execution Roadmap (Phases 2–5)
**Status**: Active  
**Target Completion**: 3-4 weeks  
**Last Updated**: 2026-04-14  

---

## CURRENT STATE ANALYSIS

### ✅ Completed (Phase 0-1)
- **Project restructure**: 8 modular projects (P1-P8) organized
- **Decision middleware**: `core/decision_middleware.py` fully built ✅
- **Timeline provider**: `core/decision_timeline_provider.py` fully built ✅
- **Training scaffold**: `training/{generator,critic,grader,scenarios}` exist
- **CUS orchestration**: `cus_langgraph.py`, `enforcer.py`, `forest_brain.py` operational
- **Network monitoring**: P3 complete with LVL1 workers

### 🟡 In Progress (70% Complete)
- **Phase 2**: Decision middleware middleware **built but not integrated** into all agents
  - ✅ Middleware: written & tested
  - ✅ Timeline provider: written & tested
  - ❌ Agent integration: `Headmaster`, `Enforcer`, `ForestBrain` need hooks
  - ❌ Dashboard: needs data feed from middleware
  
### ❌ Not Started
- **Phase 3**: Code generation for training pipeline
- **Phase 4**: GitHub repository extraction (mono → 5 separate repos)
- **Phase 5**: Docker + Kubernetes distributed deployment

---

## PHASE 2: DECISION MIDDLEWARE INTEGRATION (3-5 days)
**Goal**: Wire decision middleware into all agents; make every agent decision auditable & reversible

### What's Already Done ✅
```
✅ core/decision_middleware.py       (Decision recording, queries, reversals)
✅ core/decision_timeline_provider.py (Dashboard data aggregation)
✅ test_phase2_integration.py         (Integration test suite)
```

### What Needs to Be Done ❌

#### 2.1: Integrate Headmaster (1 day)
- [ ] Create `agents/core/headmaster_integrated.py`
  - Import middleware, call `middleware.record_spawn_decision()` on agent spawn
  - Call `middleware.record_cus_route()` on task routing
  - Hook into human gate approval
- [ ] Update imports in `cus_langgraph.py` to use integrated Headmaster
- [ ] Test with `python test_phase2_integration.py`

#### 2.2: Integrate Enforcer Gateway (1 day)
- [ ] Create `agents/organs/enforcer_integrated.py`
  - Import middleware, call `middleware.record_enforcer_approval()` on gate decisions
  - Log all blocks/approvals with reasoning
  - Add decision reversal API for overriding blocked actions
- [ ] Update `cus_langgraph.py` to use integrated Enforcer
- [ ] Test enforcer blocks and approvals

#### 2.3: Integrate Forest Brain (1 day)
- [ ] Create `agents/organs/forest_brain_integrated.py`
  - Import middleware, call `middleware.record_brain_grade()` on grading
  - Log PROMOTE/STUDY/RECYCLE decisions
  - Feed grading scores into decision record
- [ ] Update auto-runner to use integrated Brain
- [ ] Test grading workflow

#### 2.4: Build Decision Dashboard (1-2 days)
- [ ] Create `ui/forest_decisions_dashboard.py` (Streamlit)
  - Real-time decision timeline
  - Enforcer approval rate gauge
  - Brain grading distribution
  - Agent decision history
  - Sankey flow diagram
  - Recent blocks/reversals
- [ ] Connect to middleware via `DecisionTimelineProvider`
- [ ] Deploy to `localhost:8501`
- [ ] Test with live agent execution

#### 2.5: Verification (1 day)
- [ ] Run full integration test: `python test_phase2_integration.py`
- [ ] Verify all decision types are logged
- [ ] Verify decision reversal works end-to-end
- [ ] Dashboard shows live data
- [ ] All queries return correct results

### Deliverables
- ✅ 3 integrated agent modules (`Headmaster`, `Enforcer`, `ForestBrain`)
- ✅ Decision dashboard (Streamlit)
- ✅ End-to-end middleware integration test
- ✅ Decision audit trail (persisted to `ForestVault/decision_log.json`)

### Timeline
- Start: Immediately
- Duration: 3-5 days
- Exit Criteria: Integration test passes, dashboard shows live data

---

## PHASE 3: TRAINING PIPELINE COMPLETION (5-7 days)
**Goal**: Build code generation system; train models to generate safe agent code

### What's Already Done ✅
```
✅ training/scenarios/              (Scenario definitions)
✅ training/generator/              (Code generation scaffold)
✅ training/critic/                 (Criticism/feedback system)
✅ training/grader/                 (Solution evaluation)
```

### What Needs to Be Done ❌

#### 3.1: Code Generation Engine (2 days)
- [ ] Create `training/generator/code_gen.py`
  - Takes scenario + previous attempts
  - Calls Ollama to generate agent code
  - Parses output into executable Python
  - Validates syntax and imports
- [ ] Create `training/generator/validator.py`
  - Static analysis on generated code
  - Security checks (no dangerous imports)
  - Type checking
- [ ] Test generation with 5 scenarios

#### 3.2: Training Loop with Code Generation (2 days)
- [ ] Create `training/training_loop_codegen.py`
  - Load scenario
  - Generate → Validate → Test → Criticize → Improve
  - Track convergence (is code getting better?)
  - Save model checkpoints
- [ ] Implement incremental improvement (next iteration uses previous code)
- [ ] Add convergence detection (stop if no improvement 3 rounds)

#### 3.3: Model Versioning & Deployment (1 day)
- [ ] Create `training/model_manager_codegen.py`
  - Save trained models to `training/models/v1/agent_code.py`
  - Version incrementing
  - Model comparison tools
  - Deployment registry
- [ ] Add model compatibility checker

#### 3.4: CI/CD Integration for Training (1-2 days)
- [ ] Create `.github/workflows/train_agents.yml`
  - Trigger on tag: `train-*`
  - Run training pipeline
  - Upload trained model to releases
  - Notify on completion
- [ ] Create `scripts/train_all_scenarios.sh`
  - Orchestrate training for all 5 scenarios in parallel
  - Collect results and metrics
- [ ] Local testing with `./scripts/train_all_scenarios.sh`

### Deliverables
- ✅ Code generation engine (Ollama-based)
- ✅ Validator module (syntax + security)
- ✅ Full training loop with convergence detection
- ✅ Model versioning system
- ✅ GitHub Actions training workflow

### Timeline
- Start: After Phase 2 complete
- Duration: 5-7 days
- Exit Criteria: Train 3 models end-to-end, models converge, CI/CD workflow operational

---

## PHASE 4: GITHUB REPOSITORY EXTRACTION (3-4 days)
**Goal**: Split monorepo into 5 production-ready GitHub repositories

### Repositories to Extract

1. **forest-core** (CUS orchestration, Enforcer, Brain)
   - `Forest/core/`, `Forest/agents/`, `Forest/cus_*.py`
   - ~2,000 lines
   - Dependencies: LangGraph, Ollama, psutil

2. **forest-training** (Training pipeline, code generation)
   - `Forest/training/`
   - ~3,000 lines
   - Dependencies: LangChain, Ollama, datasets

3. **forest-network** (Network monitor, ARP scanning)
   - `Forest/monitors/network/`, network utilities
   - ~1,500 lines
   - Dependencies: scapy, psutil

4. **forest-audit** (Cryptex, logging, compliance)
   - `Forest/audit/`, `ForestVault/`
   - ~1,200 lines
   - Dependencies: None (pure Python)

5. **forest-dashboard** (Streamlit UI, decision visualization)
   - `Forest/ui/`
   - ~2,000 lines
   - Dependencies: Streamlit, pandas

### What Needs to Be Done ❌

#### 4.1: Prepare & Document (1 day)
- [ ] Create repo extraction plan: `REPO_EXTRACTION_PLAN.md`
- [ ] Identify module dependencies between repos
- [ ] Create shared utilities library (`forest-shared`)
- [ ] Define version constraints (semver)

#### 4.2: Extract Each Repository (2 days)
For each of the 5 repos:
- [ ] Create new GitHub repo
- [ ] Copy files + create `__init__.py` for imports
- [ ] Write `setup.py` with dependencies
- [ ] Create minimal `README.md`
- [ ] Create `.github/workflows/test.yml` for each
- [ ] Create `/examples` with sample usage
- [ ] Tag as `v1.0.0-alpha`

#### 4.3: Link Repositories (1 day)
- [ ] Create `forest-monorepo` (meta-repo that imports all 5)
  - `pyproject.toml` with all 5 as dependencies
  - Script to clone all 5 repos
  - Unified CI/CD that tests all together
- [ ] Update `Forest/` to use monorepo reference
- [ ] Document dependency graph

### Deliverables
- ✅ 5 GitHub repositories (forest-core, forest-training, forest-network, forest-audit, forest-dashboard)
- ✅ Shared utilities package (forest-shared)
- ✅ Meta-monorepo that pulls all 5
- ✅ CI/CD workflows for each repo
- ✅ Documentation of dependencies

### Timeline
- Start: After Phase 3 complete
- Duration: 3-4 days
- Exit Criteria: All 5 repos pushed to GitHub, CI/CD green, can install via `pip install forest-core`

---

## PHASE 5: DISTRIBUTED DEPLOYMENT (7-10 days)
**Goal**: Containerize all services; deploy to Kubernetes cluster

### Services to Containerize

1. **forest-cus** (CUS orchestration engine)
   - Base: `python:3.10-slim`
   - Exposes: gRPC API, metrics endpoint
   - Depends on: Ollama, Redis

2. **forest-training** (Training pipeline worker)
   - Base: `python:3.10`
   - Exposes: HTTP training API
   - Depends on: Ollama, MinIO (model storage)

3. **forest-network** (Network monitor)
   - Base: `python:3.10-slim`
   - Exposes: Prometheus metrics
   - Depends on: Vault (credentials)

4. **forest-audit** (Audit logger)
   - Base: `python:3.10-slim`
   - Exposes: HTTP audit API
   - Depends on: PostgreSQL, S3

5. **forest-dashboard** (Streamlit UI)
   - Base: `python:3.10`
   - Exposes: HTTP port 8501
   - Depends on: Redis (state), all other services

### What Needs to Be Done ❌

#### 5.1: Docker Multi-Stage Builds (2 days)
- [ ] Create `docker/Dockerfile.cus` (multi-stage: builder → runtime)
- [ ] Create `docker/Dockerfile.training` (multi-stage)
- [ ] Create `docker/Dockerfile.network` (multi-stage, DHI variant)
- [ ] Create `docker/Dockerfile.audit` (multi-stage)
- [ ] Create `docker/Dockerfile.dashboard` (multi-stage)
- [ ] Build & test all images locally
- [ ] Push to Docker registry (Docker Hub / ECR)

#### 5.2: Docker Compose for Local Development (1 day)
- [ ] Create `docker-compose.yml` with all 5 services
- [ ] Add supporting services: PostgreSQL, Redis, Ollama, MinIO
- [ ] Define volumes for persistence
- [ ] Create `.env` template
- [ ] Test full stack: `docker compose up`

#### 5.3: Kubernetes Manifests (2 days)
- [ ] Create `k8s/namespace.yaml` (forest-system)
- [ ] Create `k8s/configmap.yaml` (configuration)
- [ ] Create `k8s/secret.yaml` (credentials template)
- [ ] Create `k8s/deployment-cus.yaml` (3 replicas, requests/limits)
- [ ] Create `k8s/deployment-training.yaml` (1 replica, GPU support)
- [ ] Create `k8s/deployment-network.yaml` (DaemonSet, runs on all nodes)
- [ ] Create `k8s/deployment-audit.yaml` (1 replica, persistent volume)
- [ ] Create `k8s/deployment-dashboard.yaml` (1 replica)
- [ ] Create `k8s/service-*.yaml` for each deployment (ClusterIP or LoadBalancer)
- [ ] Create `k8s/ingress.yaml` (routes /api/cus, /training, /audit, /dashboard)

#### 5.4: Persistent Storage & StatefulSets (1-2 days)
- [ ] Create `k8s/pvc-audit.yaml` (audit logs)
- [ ] Create `k8s/pvc-models.yaml` (trained models)
- [ ] Create `k8s/statefulset-audit.yaml` (ordered startup)
- [ ] Create `k8s/statefulset-training.yaml` (persistent working directory)
- [ ] Create external PostgreSQL secret reference
- [ ] Create external Ollama service reference

#### 5.5: Monitoring & Observability (1-2 days)
- [ ] Create `k8s/servicemonitor.yaml` (Prometheus scraping)
- [ ] Create `k8s/grafana-dashboard.yaml` (Grafana dashboard)
- [ ] Export metrics from all services (Prometheus format)
- [ ] Create health check endpoints in all services
- [ ] Define resource requests/limits for all deployments

#### 5.6: CI/CD for Deployment (1-2 days)
- [ ] Create `.github/workflows/build-push-images.yml`
  - Build all 5 Docker images
  - Push to registry on tags
  - Update K8s manifests with new image versions
- [ ] Create `.github/workflows/deploy-k8s.yml`
  - Deploy to staging on PR
  - Deploy to production on tag
  - Run smoke tests post-deploy
- [ ] Create deployment verification script

### Deliverables
- ✅ 5 Dockerfiles (multi-stage, optimized)
- ✅ `docker-compose.yml` for local development
- ✅ Complete Kubernetes manifests (12+ YAML files)
- ✅ Persistent volume setup
- ✅ Monitoring & observability setup
- ✅ CI/CD workflows for image build and K8s deployment

### Timeline
- Start: After Phase 4 complete
- Duration: 7-10 days
- Exit Criteria: Full stack deployable with `kubectl apply -f k8s/`, all services healthy, dashboard accessible

---

## EXECUTION TIMELINE (Summary)

| Phase | Duration | Start | End | Status |
|-------|----------|-------|-----|--------|
| **P2**: Middleware Integration | 3-5 days | NOW | Apr 21-23 | 🟡 70% |
| **P3**: Training Code Gen | 5-7 days | Apr 23 | Apr 28-30 | ❌ 0% |
| **P4**: GitHub Repos | 3-4 days | Apr 30 | May 3-4 | ❌ 0% |
| **P5**: Docker + K8s | 7-10 days | May 4 | May 11-14 | ❌ 0% |
| **TOTAL** | **19-27 days** | **Apr 14** | **May 11-14** | **🟡 In Progress** |

---

## SUCCESS CRITERIA

### Phase 2 ✅
- [ ] Integration test passes: `python test_phase2_integration.py`
- [ ] Dashboard shows live decision data
- [ ] Decision reversal works end-to-end
- [ ] All agent types (Headmaster, Enforcer, Brain) log decisions

### Phase 3 ✅
- [ ] Train 3 models successfully
- [ ] Models show convergence (loss decreasing)
- [ ] Generated code passes validation
- [ ] GitHub Actions workflow completes successfully

### Phase 4 ✅
- [ ] All 5 repos on GitHub
- [ ] Each repo has working CI/CD
- [ ] Monorepo can import all 5
- [ ] Each repo installable via pip

### Phase 5 ✅
- [ ] Full stack runs locally with `docker compose up`
- [ ] Full stack deploys to K8s with `kubectl apply`
- [ ] All services healthy and inter-connected
- [ ] Dashboard accessible at `http://localhost:8501`
- [ ] Prometheus metrics collected
- [ ] Graceful shutdown and restart

---

## QUICK START (Next Actions)

### RIGHT NOW: Start Phase 2
```bash
cd ~/Forest

# 1. Create integrated Headmaster
cat > agents/core/headmaster_integrated.py << 'EOF'
# [See template below]
EOF

# 2. Create integrated Enforcer
cat > agents/organs/enforcer_integrated.py << 'EOF'
# [See template below]
EOF

# 3. Create integrated Brain
cat > agents/organs/forest_brain_integrated.py << 'EOF'
# [See template below]
EOF

# 4. Run integration test
python test_phase2_integration.py

# 5. Build dashboard
streamlit run ui/forest_decisions_dashboard.py
```

### Success = Integration test passes ✅

---

## DEPENDENCIES & CONSTRAINTS

### Required External Services
- **Ollama** (local LLM inference)
- **PostgreSQL** (audit database)
- **Redis** (caching/state)
- **MinIO** (model storage for Phase 3)
- **Docker** + **Docker Compose** (Phase 5)
- **Kubernetes** cluster (Phase 5)

### Python Dependencies
```
langchain>=0.1.0
langgraph>=0.0.20
ollama>=0.1.0
psutil>=5.9.0
rich>=13.0.0
streamlit>=1.20.0
sqlalchemy>=2.0.0
pydantic>=2.0.0
```

### Environment Variables
```
FOREST_PATH=/home/user/Forest
VAULT_PATH=/home/user/ForestVault
OLLAMA_HOST=http://localhost:11434
DATABASE_URL=postgresql://user:pass@localhost/forest_audit
REDIS_URL=redis://localhost:6379
```

---

## NOTES & RISKS

### High Priority
1. **Decision middleware** is 70% done — Phase 2 will unblock Phases 3-5
2. **Training pipeline** needs code generation; Phase 3 is critical path
3. **GitHub extraction** is mechanical but tedious — allocate full day for testing
4. **Kubernetes manifests** are boilerplate-heavy — use Helm charts next iteration

### Known Issues
- None at this time (project state recovered and verified)

### Recommendations
1. Complete Phase 2 before starting Phase 3 (no dependency)
2. Test locally with Docker Compose before K8s (Phase 5)
3. Commit to git after each phase completion
4. Set up GitHub Actions early (Phase 4) so Phase 5 CI/CD is smooth

---

## ROLLBACK PLAN

If any phase breaks:
1. Git revert to last known good state
2. Use backup (Forest_Archive_20260413)
3. Contact support with logs

---

**Next Action**: Start Phase 2 → Create `agents/core/headmaster_integrated.py`

**Owner**: You  
**Updated**: 2026-04-14 20:45 UTC
