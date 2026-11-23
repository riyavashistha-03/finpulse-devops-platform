# FinPulse — End-to-End Cloud-Native DevOps & CI/CD Platform

[![CI/CD Pipeline](https://github.com/riyavashistha-03/finpulse-devops-platform/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/riyavashistha-03/finpulse-devops-platform/actions)
[![Python Version](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/docker-ready-2496ED.svg)](https://www.docker.com/)
[![Kubernetes](https://img.shields.io/badge/kubernetes-v1.29-326CE5.svg)](https://kubernetes.io/)
[![Terraform](https://img.shields.io/badge/terraform-v1.5+-7B42BC.svg)](https://www.terraform.io/)
[![Ansible](https://img.shields.io/badge/ansible-automated-EE0000.svg)](https://www.ansible.com/)
[![Prometheus](https://img.shields.io/badge/prometheus-monitored-E6522C.svg)](https://prometheus.io/)
[![Coverage](https://img.shields.io/badge/coverage-81%25-brightgreen.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)]()

**Course:** DevOps & Automation Lab (ENSP461)  
**Program:** B. Tech CSE — Semester VII  
**Component:** Capstone Project (120 Marks)  
**Project Title:** Design and Implementation of an End-to-End DevOps Automation Platform for Cloud-Native Financial Intelligence  
**Author:** Riya Vashistha  
**Repository:** [github.com/riyavashistha-03/finpulse-devops-platform](https://github.com/riyavashistha-03/finpulse-devops-platform)  

---

## 📋 Project Overview

The **FinPulse DevOps Platform** is a complete, production-grade cloud-native software delivery system. It manages and automates the entire software lifecycle—from developer commit in Git to containerized Kubernetes production deployment, automated testing, configuration management, infrastructure provisioning, observability, logging, and zero-downtime deployment strategies.

The underlying application, **FinPulse**, is a real-time financial market analytics and portfolio telemetry service providing asset tracking across cryptocurrencies (BTC, ETH, SOL, ADA, DOT, LINK) and equities (AAPL, MSFT, GOOGL, NVDA), portfolio mark-to-market valuations, customizable price alert threshold engines, and continuous container health telemetry.

### Key Functional Features
- **User Authentication:** Registration, password hashing (bcrypt), session tokens, and profile management.
- **Market Data Engine:** Resilient real-time quotes, 24h percentage shifts, trading volumes, and deterministic fallback for offline CI/CD test execution.
- **Portfolio Management:** Full CRUD operations for asset holdings with automated cost-basis and unrealized P&L calculations.
- **Price Alert Engine:** Configurable threshold watcher rules with automated evaluation and status tracking.
- **Glassmorphic UI:** Modern dark-theme responsive dashboard with Chart.js time-series trendlines.
- **Observability Probes:** Kubernetes liveness (`/live`), readiness (`/ready`), general health (`/health`), and Prometheus metrics (`/metrics`).

---

## 🛠️ DevOps Phases Roadmap

| Phase | Milestone | Technology Stack | Status |
| :--- | :--- | :--- | :--- |
| **Phase 1** | **Version Control & Branching Strategy** | Git, GitHub, GitFlow | **Completed** |
| **Phase 2** | **Continuous Integration & Automated Testing** | Jenkins, Pytest, Coverage | **Completed** |
| **Phase 3** | **Containerization & CI/CD Pipeline** | Docker, Docker Compose, Jenkins | **Completed** |
| **Phase 4** | **Container Orchestration & Scaling** | Kubernetes, Helm 3 | **Completed** |
| **Phase 5** | **Configuration Management** | Ansible | **Completed** |
| **Phase 6** | **Infrastructure as Code (IaC)** | Terraform | **Completed** |
| **Phase 7** | **Observability & SRE Metrics** | Prometheus, Grafana | **Completed** |
| **Phase 8** | **Centralized Logging** | Fluentd DaemonSet | **Completed** |
| **Phase 9** | **DevSecOps & Image Security** | Trivy, SAST Scanner, RBAC | **Completed** |
| **Phase 10** | **Zero-Downtime Deployment Strategy** | Blue-Green & Canary Rollouts | **Completed** |
| **Phase 11** | **GitOps Automated Delivery** | ArgoCD / Kubernetes Manifests | **Completed** |

---

## 🏛️ System Architecture

```
                                      [ Developer Push ]
                                               │
                                               ▼
                              ┌─────────────────────────────────┐
                              │     GitFlow Branching Model     │
                              │  feature/* ──► develop ──► main │
                              └─────────────────────────────────┘
                                               │
                                               ▼
                              ┌─────────────────────────────────┐
                              │   Automated CI/CD Pipelines     │
                              │   • GitHub Actions & Jenkins    │
                              │   • Pytest Suite (26 Tests)     │
                              │   • DevSecOps SAST & Secrets    │
                              │   • Docker Multi-Stage Build    │
                              └─────────────────────────────────┘
                                               │
                                               ▼
                              ┌─────────────────────────────────┐
                              │    Container Registry (GHCR)    │
                              │    ghcr.io/.../finpulse-app     │
                              └─────────────────────────────────┘
                                               │
                                               ▼
         ┌───────────────────────────────────────────────────────────────────────────┐
         │                  Kubernetes Cluster (finpulse-prod)                       │
         │                                                                           │
         │   ┌───────────────────────────────────────────────────────────────────┐   │
         │   │                   Ingress Controller (Nginx)                      │   │
         │   └─────────────────────────────────┬─────────────────────────────────┘   │
         │                                     │                                     │
         │                                     ▼                                     │
         │   ┌───────────────────────────────────────────────────────────────────┐   │
         │   │                   FinPulse Service (ClusterIP)                    │   │
         │   └─────────────────────────────────┬─────────────────────────────────┘   │
         │                                     │                                     │
         │                                     ▼                                     │
         │   ┌───────────────────────────────────────────────────────────────────┐   │
         │   │           FinPulse Deployment (3 Replicas / HPA: 2-10)            │   │
         │   │   ┌───────────────────────────────────────────────────────────┐   │   │
         │   │   │                     FinPulse Pod                          │   │   │
         │   │   │   Gunicorn WSGI (2 Workers, 4 Threads) -> Port 5050       │   │   │
         │   │   │   Non-root user (appuser:1001)                            │   │   │
         │   │   │   Mounts: PersistentVolumeClaim (/app/instance)           │   │   │
         │   │   │   Probes: /ready, /live, /health                          │   │   │
         │   │   └───────────────────────────────────────────────────────────┘   │   │
         │   └───────────────────────────────────────────────────────────────────┘   │
         │                                     │                                     │
         │                  ┌──────────────────┴──────────────────┐                  │
         │                  ▼                                     ▼                  │
         │   ┌─────────────────────────────┐       ┌─────────────────────────────┐   │
         │   │  Prometheus ServiceMonitor  │       │      Fluentd DaemonSet      │   │
         │   │       Scrapes /metrics      │       │     Container Log Tail      │   │
         │   └─────────────────────────────┘       └─────────────────────────────┘   │
         └───────────────────────────────────────────────────────────────────────────┘
```

---

## 🌿 Phase 1: Git Branching Strategy & GitFlow

The project strictly follows the **GitFlow** branching model:
```
main (Production releases, semver tagged v1.0.0)
 │
 ├── develop (Integration & staging)
 │    │
 │    ├── feature/auth-system
 │    ├── feature/market-portfolio-engine
 │    ├── feature/kubernetes-manifests
 │    └── feature/terraform-iac
```
- **`main`**: Protected production branch containing stable tagged releases.
- **`develop`**: Integration branch where tested feature branches converge.
- **`feature/*`**: Isolated feature branches for development.

---

## 🧪 Phase 2: Automated Testing & Verification

The automated test suite runs via **Pytest** and contains 26 unit and integration tests:
- `tests/test_auth.py`: User registration, password hashing, duplicate prevention, login/logout.
- `tests/test_market.py`: Live and deterministic quotes, 24h calculations, chart history, asset search.
- `tests/test_portfolio.py`: Asset addition, valuation updates, cost-basis calculations, deletion.
- `tests/test_alerts.py`: Threshold creation, condition evaluation, trigger states.
- `tests/test_health_metrics.py`: Observability endpoints (`/health`, `/ready`, `/live`, `/metrics`).

```bash
# Run test suite
python -m pytest -v tests/

# Run with coverage report and JUnit XML
python -m pytest -v --junitxml=reports/pytest-results.xml --cov=app tests/
```
**Results:** `26 passed in 5.12s • 81% Total Code Coverage • 0 Warnings`.

---

## 🐳 Phase 3: Docker Containerization

FinPulse uses a multi-stage production Dockerfile:
- **Builder Stage:** Resolves wheels and dependencies with GCC.
- **Runtime Stage:** Slim Python 3.11 image, unprivileged `appuser` (UID 1001), built-in curl healthcheck probe, and Gunicorn WSGI server.

```bash
# Build and run with Docker Compose
docker compose up --build -d

# Check running services
docker compose ps

# Access health endpoint
curl http://localhost:5050/health

# Stop stack
docker compose down
```

---

## ☸️ Phase 4: Kubernetes Orchestration & Helm

Deploy FinPulse to any standard Kubernetes cluster (Minikube, Kind, EKS, AKS, GKE):

```bash
# Apply Kubernetes declarative manifests
kubectl apply -f kubernetes/namespace.yaml
kubectl apply -f kubernetes/configmap.yaml
kubectl apply -f kubernetes/secret.yaml
kubectl apply -f kubernetes/persistent-volume.yaml
kubectl apply -f kubernetes/persistent-volume-claim.yaml
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/service.yaml
kubectl apply -f kubernetes/hpa.yaml
kubectl apply -f kubernetes/ingress.yaml

# Verify pod status and autoscaling
kubectl get pods -n finpulse-prod
kubectl get hpa -n finpulse-prod
```

Or deploy using the packaged **Helm 3** chart:
```bash
helm install finpulse ./helm/finpulse --namespace finpulse-prod --create-namespace
```

---

## 🤖 Phase 5: Ansible Configuration Management

Automate server provisioning and configuration:
```bash
cd ansible
# Setup Docker Engine on target hosts
ansible-playbook -i inventory.ini playbooks/docker_engine_setup.yml

# Bootstrap Kubernetes nodes
ansible-playbook -i inventory.ini playbooks/kubernetes_cluster_setup.yml

# Apply server security hardening
ansible-playbook -i inventory.ini playbooks/security_hardening.yml

# Deploy application stack
ansible-playbook -i inventory.ini playbooks/app_deployment.yml
```

---

## 🏗️ Phase 6: Infrastructure as Code (Terraform)

### Local Environment (Docker Provider)
```bash
cd terraform/environments/local
terraform init
terraform plan
terraform apply -auto-approve
```

### AWS Cloud Environment (ECS Fargate + ALB + VPC)
```bash
cd terraform/environments/aws
terraform init -backend=false
terraform validate
terraform plan
```

---

## 📊 Phase 7: Observability & SRE Metrics

FinPulse exposes Prometheus metrics at `/metrics`:
- `finpulse_http_requests_total`: Throughput by method, endpoint, and status.
- `finpulse_request_duration_seconds`: Request latency distribution histogram.
- `finpulse_active_portfolios`: Current count of user portfolios.
- `finpulse_active_alerts_total`: Active threshold rules.

Pre-configured Grafana dashboard model available at:  
`monitoring/grafana/dashboards/finpulse-telemetry.json`

---

## 🛡️ Phase 9: DevSecOps Automation

Run the automated pipeline security scanner:
```bash
python scripts/security_scan.py
```
- Static Code Analysis (SAST) for credential and API token leaks.
- Dockerfile compliance (non-root UID, no-cache flags, healthcheck).
- Dependency manifest pinning and version integrity.

---

## 🔄 Phase 10: Zero-Downtime Deployment Strategies

### Automated Blue/Green Switchover
```bash
python scripts/deploy_blue_green.py
```

### Progressive Weighted Canary Rollout
```bash
python scripts/deploy_canary.py
```

---

## 🚀 Quickstart (Local Development)

```bash
# 1. Clone the repository
git clone https://github.com/riyavashistha-03/finpulse-devops-platform.git
cd finpulse-devops-platform

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run automated tests
pytest tests/

# 4. Start the application
python run.py
```
Visit `http://localhost:5050` in your web browser.

---

## 📁 Repository Structure

```
finpulse-devops-platform/
├── app/                          # Flask application package
│   ├── __init__.py               # Application factory & probe setup
│   ├── extensions.py             # SQLAlchemy & Prometheus singletons
│   ├── models.py                 # User, PortfolioAsset, PriceAlert entities
│   ├── routes/
│   │   ├── auth.py               # Authentication API
│   │   ├── market.py             # Market quote & history API
│   │   ├── portfolio.py          # Portfolio CRUD endpoints
│   │   ├── alerts.py             # Price alerts API
│   │   └── web.py                # Web UI controllers
│   ├── services/
│   │   ├── market_data.py        # Resilient quote service & fallback
│   │   └── alert_engine.py       # Threshold evaluation engine
│   ├── static/                   # Glassmorphic CSS & client JS
│   └── templates/                # Jinja2 dashboard templates
├── tests/                        # 26 automated unit & integration tests
├── kubernetes/                   # Complete K8s manifests (Deploy, SVC, HPA, etc.)
├── helm/finpulse/                # Helm 3 deployment chart
├── ansible/                      # Inventory and playbooks (Docker, K8s, Deploy)
├── terraform/                    # Dual-environment IaC (Local Docker & AWS ECS)
├── monitoring/                   # Prometheus config, alert rules & Grafana JSON
├── logging/                      # Fluentd DaemonSet & config
├── scripts/                      # DevSecOps, Blue/Green, Canary, PDF generator
├── docs/
│   ├── API_REFERENCE.md          # REST API documentation
│   ├── CAPSTONE_REPORT.md        # Academic report
│   └── FinPulse_DevOps_Capstone_Report.pdf # Publication-ready PDF for ZOSIMA
├── .github/workflows/ci-cd.yml   # GitHub Actions CI/CD pipeline
├── Dockerfile                    # Production multi-stage Docker image
├── docker-compose.yml            # Multi-service stack definition
├── Jenkinsfile                   # Declarative 11-stage CI/CD pipeline
├── requirements.txt              # Pinned Python dependencies
├── config.py                     # Environment configurations
├── run.py                        # Entrypoint script
└── README.md                     # This file
```

---

## 📄 License & Coursework

Developed as part of the **ENSP461 DevOps & Automation Lab** Capstone Coursework.  
Author: **Riya Vashistha** • 2026.
