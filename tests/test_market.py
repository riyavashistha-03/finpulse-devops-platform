"""
Unit & Integration Tests for Market Data Engine
"""

def test_get_market_overview(client):
    """Verify market overview returns populated list of assets and performance leaders."""
    response = client.get("/api/market/overview")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert len(data["data"]) >= 5
    assert "top_gainer" in data["summary"]
    assert "top_loser" in data["summary"]

def test_get_single_quote_btc(client):
    """Verify quote retrieval for primary asset BTC."""
    response = client.get("/api/market/quote/BTC")
    assert response.status_code == 200
    data = response.get_json()["data"]
    assert data["symbol"] == "BTC"
    assert data["type"] == "crypto"
    assert data["price"] > 1000

def test_get_single_quote_not_found(client):
    """Verify unknown ticker returns 404."""
    response = client.get("/api/market/quote/UNKNOWNXYZ")
    assert response.status_code == 404
    assert "not found" in response.get_json()["message"]

def test_get_asset_history(client):
    """Verify historical timeline returns labels and points for charts."""
    response = client.get("/api/market/history/ETH?points=10")
    assert response.status_code == 200
    data = response.get_json()["data"]
    assert data["symbol"] == "ETH"
    assert len(data["points"]) == 10
    assert len(data["labels"]) == 10

def test_search_assets(client):
    """Verify asset search by ticker and by name."""
    response = client.get("/api/market/search?q=sol")
    assert response.status_code == 200
    results = response.get_json()["results"]
    assert any(item["symbol"] == "SOL" for item in results)

    # Empty query should fail
    empty_resp = client.get("/api/market/search")
    assert empty_resp.status_code == 400
