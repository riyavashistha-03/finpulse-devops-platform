"""
Unit & Integration Tests for Health and Telemetry Observability Probes
"""

def test_health_probe(client):
    """Verify general service health endpoint returns 200 and healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "UP"
    assert data["app"] == "FinPulse"
    assert data["database"] == "CONNECTED"

def test_liveness_probe(client):
    """Verify Kubernetes liveness probe returns 200 ALIVE."""
    response = client.get("/live")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ALIVE"

def test_readiness_probe(client):
    """Verify Kubernetes readiness probe returns 200 READY."""
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.get_json()["status"] == "READY"

def test_prometheus_metrics_endpoint(client):
    """Verify /metrics returns Prometheus formatted telemetry text."""
    # Hit an endpoint first to produce metric records
    client.get("/api/market/overview")
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "finpulse_http_requests_total" in response.text
    assert "finpulse_request_duration_seconds" in response.text
