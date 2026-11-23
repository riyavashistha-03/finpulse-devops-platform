"""
Unit & Integration Tests for Portfolio Management
"""

def test_get_empty_portfolio(auth_client):
    """Verify empty portfolio returns initial zero balances."""
    response = auth_client.get("/api/portfolio")
    assert response.status_code == 200
    p = response.get_json()["portfolio"]
    assert p["total_items"] == 0
    assert p["total_invested"] == 0.0
    assert p["total_current_value"] == 0.0

def test_add_portfolio_asset(auth_client):
    """Verify adding an asset computes cost basis and responds 201."""
    payload = {
        "asset_symbol": "BTC",
        "quantity": 0.5,
        "buy_price": 60000.0,
        "notes": "Purchased during pullback"
    }
    response = auth_client.post("/api/portfolio", json=payload)
    assert response.status_code == 201
    asset = response.get_json()["asset"]
    assert asset["asset_symbol"] == "BTC"
    assert asset["quantity"] == 0.5
    assert asset["total_cost"] == 30000.0

def test_add_portfolio_asset_invalid_data(auth_client):
    """Verify validation handles negative quantities or prices."""
    payload = {
        "asset_symbol": "ETH",
        "quantity": -2,
        "buy_price": 3000.0
    }
    response = auth_client.post("/api/portfolio", json=payload)
    assert response.status_code == 400

def test_update_portfolio_asset(auth_client):
    """Verify updating holding quantity and notes."""
    # Add initial asset
    add_resp = auth_client.post("/api/portfolio", json={
        "asset_symbol": "SOL",
        "quantity": 10,
        "buy_price": 150.0
    })
    asset_id = add_resp.get_json()["asset"]["id"]

    # Update asset
    update_resp = auth_client.put(f"/api/portfolio/{asset_id}", json={
        "quantity": 15,
        "notes": "Added 5 more tokens"
    })
    assert update_resp.status_code == 200
    updated = update_resp.get_json()["asset"]
    assert updated["quantity"] == 15.0
    assert updated["notes"] == "Added 5 more tokens"

def test_delete_portfolio_asset(auth_client):
    """Verify deleting asset removes holding from portfolio."""
    add_resp = auth_client.post("/api/portfolio", json={
        "asset_symbol": "LINK",
        "quantity": 100,
        "buy_price": 14.0
    })
    asset_id = add_resp.get_json()["asset"]["id"]

    del_resp = auth_client.delete(f"/api/portfolio/{asset_id}")
    assert del_resp.status_code == 200

    # Ensure it no longer exists
    get_resp = auth_client.get(f"/api/portfolio/{asset_id}")
    assert get_resp.status_code == 404
