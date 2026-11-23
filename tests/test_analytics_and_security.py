"""
Unit and Integration Tests for Portfolio Analytics, Export, Market Stats, and Security Controls.
"""
import pytest
from app.models import User, PortfolioAsset

def test_market_stats_endpoint(client):
    """Verify /api/market/stats returns accurate caching telemetry."""
    # Warm up cache
    client.get("/api/market/quote/BTC")
    client.get("/api/market/quote/BTC")
    response = client.get("/api/market/stats")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    stats = data["stats"]
    assert stats["total_supported_assets"] >= 16
    assert stats["cache_ttl_seconds"] == 60
    assert stats["cached_entries"] >= 1
    assert "hit_ratio_percentage" in stats

def test_expanded_assets_availability(client):
    """Verify newly added crypto and stock assets are reachable."""
    symbols = ["BNB", "XRP", "AVAX", "TSLA", "AMZN", "META"]
    for sym in symbols:
        res = client.get(f"/api/market/quote/{sym}")
        assert res.status_code == 200
        quote = res.get_json()["data"]
        assert quote["symbol"] == sym
        assert quote["price"] > 0
        assert "type" in quote

def test_security_headers_applied(client):
    """Verify DevSecOps security response headers are present on all HTTP responses."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "SAMEORIGIN"
    assert response.headers.get("X-XSS-Protection") == "1; mode=block"
    assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"

def test_portfolio_analytics_empty(auth_client):
    """Verify analytics endpoint on empty portfolio."""
    response = auth_client.get("/api/portfolio/analytics")
    assert response.status_code == 200
    analytics = response.get_json()["analytics"]
    assert analytics["total_assets"] == 0
    assert analytics["total_invested"] == 0.0
    assert analytics["diversification_status"] == "EMPTY"

def test_portfolio_analytics_with_holdings(auth_client):
    """Verify analytics computes accurate class allocation, asset percentages, and performers."""
    # Add crypto asset
    auth_client.post("/api/portfolio", json={
        "asset_symbol": "BTC",
        "quantity": 1.0,
        "buy_price": 50000.0,
        "notes": "Crypto holding"
    })
    # Add stock asset
    auth_client.post("/api/portfolio", json={
        "asset_symbol": "AAPL",
        "quantity": 10.0,
        "buy_price": 200.0,
        "notes": "Stock holding"
    })

    response = auth_client.get("/api/portfolio/analytics")
    assert response.status_code == 200
    data = response.get_json()["analytics"]
    assert data["total_assets"] == 2
    assert data["total_invested"] == 52000.0
    assert data["total_current_value"] > 0
    assert "crypto" in data["allocation_by_class"]
    assert "stock" in data["allocation_by_class"]
    assert len(data["allocation_by_asset"]) == 2
    assert data["top_performer"] is not None
    assert data["worst_performer"] is not None
    assert data["diversification_status"] in ["HIGHLY_CONCENTRATED", "MODERATELY_DIVERSIFIED", "WELL_DIVERSIFIED"]

def test_portfolio_export_json(auth_client):
    """Verify JSON export delivers structured holdings."""
    auth_client.post("/api/portfolio", json={
        "asset_symbol": "ETH",
        "quantity": 2.5,
        "buy_price": 3000.0
    })
    response = auth_client.get("/api/portfolio/export?format=json")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert data["exported_items_count"] == 1
    assert data["holdings"][0]["symbol"] == "ETH"
    assert data["holdings"][0]["quantity"] == 2.5

def test_portfolio_export_csv(auth_client):
    """Verify CSV export delivers valid CSV stream with content headers."""
    auth_client.post("/api/portfolio", json={
        "asset_symbol": "MSFT",
        "quantity": 5.0,
        "buy_price": 400.0
    })
    response = auth_client.get("/api/portfolio/export?format=csv")
    assert response.status_code == 200
    assert "text/csv" in response.headers.get("Content-Type", "")
    assert "attachment" in response.headers.get("Content-Disposition", "")
    content = response.data.decode("utf-8")
    assert "symbol,name,type,quantity" in content
    assert "MSFT" in content
