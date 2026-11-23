"""
Unit & Integration Tests for Alerts Engine
"""

def test_create_price_alert(auth_client):
    """Verify alert creation with threshold price and condition."""
    payload = {
        "asset_symbol": "BTC",
        "target_price": 75000.0,
        "condition": "above"
    }
    response = auth_client.post("/api/alerts", json=payload)
    assert response.status_code == 201
    alert = response.get_json()["alert"]
    assert alert["asset_symbol"] == "BTC"
    assert alert["target_price"] == 75000.0
    assert alert["is_active"] is True
    assert alert["is_triggered"] is False

def test_create_alert_invalid_condition(auth_client):
    """Verify invalid condition rejects with 400."""
    payload = {
        "asset_symbol": "ETH",
        "target_price": 4000.0,
        "condition": "near"
    }
    response = auth_client.post("/api/alerts", json=payload)
    assert response.status_code == 400
    assert "Condition must be 'above' or 'below'" in response.get_json()["message"]

def test_toggle_alert(auth_client):
    """Verify toggling alert between active and paused."""
    create_resp = auth_client.post("/api/alerts", json={
        "asset_symbol": "SOL",
        "target_price": 200.0,
        "condition": "above"
    })
    alert_id = create_resp.get_json()["alert"]["id"]

    toggle_resp = auth_client.post(f"/api/alerts/{alert_id}/toggle")
    assert toggle_resp.status_code == 200
    assert toggle_resp.get_json()["alert"]["is_active"] is False

def test_evaluate_alerts(auth_client):
    """Verify evaluate triggers when condition threshold is exceeded."""
    # Create an alert with very low target price that is guaranteed to trigger
    auth_client.post("/api/alerts", json={
        "asset_symbol": "BTC",
        "target_price": 1000.0, # BTC is ~68,000, which is definitely above 1,000
        "condition": "above"
    })

    eval_resp = auth_client.post("/api/alerts/evaluate")
    assert eval_resp.status_code == 200
    data = eval_resp.get_json()
    assert data["triggered_count"] >= 1
    assert data["triggered_alerts"][0]["symbol"] == "BTC"

def test_delete_alert(auth_client):
    """Verify alert deletion."""
    create_resp = auth_client.post("/api/alerts", json={
        "asset_symbol": "ADA",
        "target_price": 1.0,
        "condition": "above"
    })
    alert_id = create_resp.get_json()["alert"]["id"]

    del_resp = auth_client.delete(f"/api/alerts/{alert_id}")
    assert del_resp.status_code == 200
