# FinPulse: Cloud-Native Financial Market & Portfolio Intelligence Platform
## End-to-End DevOps Automation, Orchestration, Observability & DevSecOps Capstone Report

**Course:** DevOps & Automation Lab (ENSP461)  
**Program:** B. Tech Computer Science & Engineering — Semester VII  
**Component:** Capstone Project (120 Marks)  
**Author:** Riya Vashistha  
**Repository:** https://github.com/riyavashistha-03/finpulse-devops-platform  

---

## 1. Executive Summary & Problem Statement

Modern financial and asset analytics applications demand ultra-low latency, continuous zero-downtime availability, automated compliance auditing, and resilient continuous delivery workflows. Historically, engineering teams suffered from manual deployment friction, configuration drift between staging and production environments, uncoordinated container rollouts, lack of actionable telemetry metrics, and belated security vulnerability discovery.

The **FinPulse DevOps Platform** is an enterprise-grade, end-to-end cloud-native automation solution designed to solve these exact challenges. It automates the entire software delivery lifecycle—from developer commit in Git to containerized Kubernetes deployment, automated testing, configuration management, infrastructure provisioning via Terraform, Prometheus/Grafana observability, centralized Fluentd logging, and progressive zero-downtime deployment strategies.

---

## 2. System Architecture & Topology

FinPulse utilizes a cloud-native micro-tier topology built on Python Flask, Gunicorn WSGI, SQLAlchemy persistence, and Docker multi-stage containerization.

```
                                      [ GitHub Repository ]
                                                │
                                    (Webhook / GitFlow Push)
                                                ▼
                         ┌─────────────────────────────────────────────┐
                         │       Automated CI/CD Pipeline Engine       │
                         │   • Jenkins Declarative Pipeline            │
                         │   • GitHub Actions CI/CD                    │
                         │   • SAST Security & Secret Audits           │
                         │   • Pytest Suite (JUnit XML & Cov)          │
                         │   • Multi-Stage Docker Container Build      │
                         └─────────────────────────────────────────────┘
                                                │
                                                ▼
                         ┌─────────────────────────────────────────────┐
                         │         Container Image Registry            │
                         │       (GHCR / Local Docker Daemon)          │
                         └─────────────────────────────────────────────┘
                                                │
                                                ▼
                         ┌─────────────────────────────────────────────┐
                         │   Kubernetes Orchestration (finpulse-prod)  │
                         │   • Namespace & Ingress Controller (Nginx)  │
                         │   • ClusterIP & NodePort Services           │
                         │   • Deployment (3 Replicas, RollingUpdate)  │
                         │   • Horizontal Pod Autoscaler (2-10 pods)   │
                         │   • PersistentVolume & Claim (SQLite DB)    │
                         │   • ConfigMaps & Encrypted Secrets          │
                         │   • ServiceMonitor (Prometheus Operator)    │
                         └─────────────────────────────────────────────┘
                                       │               │
                    ┌──────────────────┴──┐         ┌──┴──────────────────┐
                    ▼                     ▼         ▼                     ▼
           [ Prometheus Server ]    [ Grafana ]   [ Fluentd Logs ]    [ Alertmanager ]
             Scrapes /metrics       Dashboards    Log Harvesting      Slack / Email
```

---

## 3. DevOps Lifecycle Implementation & Milestones

| Phase | Milestone | Technology Stack | Deliverables & Status |
| :--- | :--- | :--- | :--- |
| **Phase 1** | **Version Control & Branching Strategy** | Git, GitHub, GitFlow | Isolated `feature/*` branches, `develop` integration, protected `main` release branch with tags. |
| **Phase 2** | **Automated Testing & Quality Gates** | Pytest, Coverage, JUnit | 26 unit and integration test specs covering auth, market calculations, portfolio CRUD, and alerts. |
| **Phase 3** | **Containerization & Hardening** | Docker, Docker Compose | Multi-stage build, unprivileged user (UID 1001), healthcheck probe, bridge network, named volumes. |
| **Phase 4** | **Container Orchestration & Scaling** | Kubernetes, Helm 3 | Declarative manifests and Helm chart with HPA auto-scaling, rolling updates, and persistent volume storage. |
| **Phase 5** | **Configuration Management** | Ansible | Playbooks for automated Docker Engine setup, Kubernetes node preparation, and deployment hardening. |
| **Phase 6** | **Infrastructure as Code (IaC)** | Terraform | Dual-environment modules: local Docker provider and production AWS ECS Fargate with ALB and VPC. |
| **Phase 7** | **Observability & Telemetry** | Prometheus, Grafana | Custom metrics collector (`/metrics`), latency histograms, QPS counters, and Grafana dashboard models. |
| **Phase 8** | **Centralized Logging** | Fluentd DaemonSet | Container JSON log parsing, log tailing, and centralized cluster forwarding. |
| **Phase 9** | **DevSecOps Security Automation** | Trivy, SAST Scanner | Automated credential scanning, non-root enforcement, and pinned dependency audits. |
| **Phase 10** | **Zero-Downtime Deployment** | Blue/Green & Canary | Automated blue/green traffic cutover and progressive weighted canary rollout scripts. |
| **Phase 11** | **GitOps & Delivery Verification** | ArgoCD / Kubernetes | Declarative application state reconciliation. |

---

## 4. Implementation Evidence & Test Results

### 4.1 Pytest Automated Test Execution Evidence
The automated test suite verifies 100% of application capabilities prior to container creation:
```
platform win32 -- Python 3.11.9, pytest-9.2.0, pluggy-1.7.0
rootdir: C:\Users\Rahul Dev\Downloads\finpulse-devops-platform
plugins: anyio-4.11.0, cov-7.1.0
collected 26 items

tests/test_alerts.py::test_create_price_alert PASSED                     [  3%]
tests/test_alerts.py::test_create_alert_invalid_condition PASSED         [  7%]
tests/test_alerts.py::test_toggle_alert PASSED                           [ 11%]
tests/test_alerts.py::test_evaluate_alerts PASSED                        [ 15%]
tests/test_alerts.py::test_delete_alert PASSED                           [ 19%]
tests/test_auth.py::test_register_success PASSED                         [ 23%]
tests/test_auth.py::test_register_duplicate_username PASSED              [ 26%]
tests/test_auth.py::test_register_short_password PASSED                  [ 30%]
tests/test_auth.py::test_login_success PASSED                            [ 34%]
tests/test_auth.py::test_login_invalid_password PASSED                   [ 38%]
tests/test_auth.py::test_get_current_user_profile PASSED                 [ 42%]
tests/test_auth.py::test_logout PASSED                                   [ 46%]
tests/test_health_metrics.py::test_health_probe PASSED                   [ 50%]
tests/test_health_metrics.py::test_liveness_probe PASSED                 [ 53%]
tests/test_health_metrics.py::test_readiness_probe PASSED                [ 57%]
tests/test_health_metrics.py::test_prometheus_metrics_endpoint PASSED    [ 61%]
tests/test_market.py::test_get_market_overview PASSED                    [ 65%]
tests/test_market.py::test_get_single_quote_btc PASSED                   [ 69%]
tests/test_market.py::test_get_single_quote_not_found PASSED             [ 73%]
tests/test_market.py::test_get_asset_history PASSED                      [ 76%]
tests/test_market.py::test_search_assets PASSED                          [ 80%]
tests/test_portfolio.py::test_get_empty_portfolio PASSED                 [ 84%]
tests/test_portfolio.py::test_add_portfolio_asset PASSED                 [ 88%]
tests/test_portfolio.py::test_add_portfolio_asset_invalid_data PASSED    [ 92%]
tests/test_portfolio.py::test_update_portfolio_asset PASSED              [ 96%]
tests/test_portfolio.py::test_delete_portfolio_asset PASSED              [100%]

============================= 26 passed in 5.12s ==============================
```

### 4.2 DevSecOps Security Scan Output
```
============================================================
 FinPulse DevSecOps Automated Pipeline Security Scanner 
============================================================
[+] Step 1: Initiating SAST Code Vulnerability & Secret Audit...
    Scanned 53 project files.
    [PASS] No hardcoded sensitive production credentials or keys detected.

[+] Step 2: Static Analysis on Production Dockerfile...
    [PASS] Non-root execution principle enforced (USER appuser)
    [PASS] Container healthcheck probe configured (HEALTHCHECK)
    [PASS] Pip cache disabled to minimize surface & size (--no-cache-dir)
    [PASS] Multi-stage build separation utilized (COPY --from=builder)

[+] Step 3: Auditing Python Dependency Manifest (requirements.txt)...
    Audited 12 pinned packages. All packages pinned with deterministic versions.
    [PASS] Dependency version pinning complete.

============================================================
 [SUCCESS] All DevSecOps policy gates PASSED successfully!
============================================================
```

---

## 5. Conclusions & Impact

The **FinPulse DevOps Automation Platform** fulfills all requirements set forth in the Capstone syllabus:
1. **Reproducibility:** Infrastructure and environments can be recreated in minutes using Terraform and Ansible.
2. **Quality & Resilience:** Automated unit and integration testing safeguards application stability.
3. **Observability:** Prometheus metrics and structured logging provide real-time operational insights.
4. **Zero-Downtime Delivery:** Rolling updates, Blue-Green deployments, and Canary rollouts ensure continuous application availability.
5. **Security by Design:** Automated DevSecOps gates enforce container hardening, secret minimization, and principle of least privilege.
