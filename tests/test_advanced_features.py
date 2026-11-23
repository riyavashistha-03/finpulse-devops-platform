"""
Comprehensive Tests for Advanced Platform Features (v1.2.0):
- Technical Indicators (RSI, SMA, Bollinger Bands)
- Market Sentiment (Composite Fear & Greed Index)
- User Watchlist Pinning & Telemetry
- Portfolio Transactions & Realized P&L Ledger
- SRE Circuit Breaker Resilience
- System Info & Metadata
"""
import pytest
from app.services.circuit_breaker import CircuitBreaker, CircuitBreakerOpenException

def test_technical_indicators_success(client):
    """Verify quantitative indicators calculation and trade signal generation."""
    response = client.get("/api/market/technical/BTC")
    assert response.status_code == 200
    data = response.get_json()["data"]
    assert data["symbol"] == "BTC"
    assert 0 <= data["rsi_14"] <= 100
    assert data["sma_7"] > 0
    assert data["sma_14"] > 0
    assert data["bollinger_upper"] >= data["bollinger_middle"] >= data["bollinger_lower"]
    assert data["signal"] in ["STRONG_BUY", "BUY", "HOLD", "SELL", "STRONG_SELL"]
    assert len(data["signal_rationale"]) > 0

def test_technical_indicators_not_found(client):
    """Verify 404 response for unknown assets."""
    response = client.get("/api/market/technical/UNKNOWNXYZ")
    assert response.status_code == 404

def test_market_sentiment_engine(client):
    """Verify macro Fear & Greed composite sentiment index across all assets."""
    response = client.get("/api/market/sentiment")
    assert response.status_code == 200
    s = response.get_json()["sentiment"]
    assert 0 <= s["sentiment_score"] <= 100
    assert s["classification"] in ["Extreme Greed", "Greed", "Neutral", "Fear", "Extreme Fear"]
    assert s["total_assets_analyzed"] >= 16
    assert s["bullish_assets_count"] + s["bearish_assets_count"] <= s["total_assets_analyzed"]
    assert "top_bullish_asset" in s
    assert "top_bearish_asset" in s

def test_watchlist_lifecycle(auth_client):
    """Verify user can view, pin, and remove assets from their watchlist."""
    # 1. Initial watchlist is empty
    res = auth_client.get("/api/market/watchlist")
    assert res.status_code == 200
    assert res.get_json()["total_watchlist_items"] == 0

    # 2. Add BTC to watchlist
    res = auth_client.post("/api/market/watchlist", json={"asset_symbol": "BTC"})
    assert res.status_code == 201
    assert res.get_json()["item"]["asset_symbol"] == "BTC"

    # 3. Duplicate add returns 409 Conflict
    res = auth_client.post("/api/market/watchlist", json={"asset_symbol": "BTC"})
    assert res.status_code == 409

    # 4. View populated watchlist with live telemetry
    res = auth_client.get("/api/market/watchlist")
    assert res.status_code == 200
    items = res.get_json()["watchlist"]
    assert len(items) == 1
    assert items[0]["asset_symbol"] == "BTC"
    assert items[0]["current_price"] > 0
    assert "technical_signal" in items[0]

    # 5. Remove from watchlist
    res = auth_client.delete("/api/market/watchlist/BTC")
    assert res.status_code == 200

    # 6. Removing non-existent returns 404
    res = auth_client.delete("/api/market/watchlist/ETH")
    assert res.status_code == 404

def test_portfolio_transaction_buy_and_average_price(auth_client):
    """Verify BUY transaction automatically updates holdings with weighted average cost basis."""
    # First purchase: 1.0 SOL at $100
    res1 = auth_client.post("/api/portfolio/transaction", json={
        "asset_symbol": "SOL",
        "transaction_type": "BUY",
        "quantity": 1.0,
        "price": 100.0,
        "notes": "First accumulation"
    })
    assert res1.status_code == 201
    tx1 = res1.get_json()["transaction"]
    assert tx1["transaction_type"] == "BUY"
    assert tx1["realized_pnl"] == 0.0

    # Second purchase: 1.0 SOL at $200 (average should be $150)
    res2 = auth_client.post("/api/portfolio/transaction", json={
        "asset_symbol": "SOL",
        "transaction_type": "BUY",
        "quantity": 1.0,
        "price": 200.0,
        "notes": "Second accumulation"
    })
    assert res2.status_code == 201

    # Check resulting portfolio holding
    p_res = auth_client.get("/api/portfolio")
    holding = p_res.get_json()["portfolio"]["items"][0]
    assert holding["asset_symbol"] == "SOL"
    assert holding["quantity"] == 2.0
    assert holding["buy_price"] == 150.0

def test_portfolio_transaction_sell_and_realized_pnl(auth_client):
    """Verify SELL transaction calculates realized P&L and reduces/deletes holdings."""
    # Buy 2.0 ETH at $3000
    auth_client.post("/api/portfolio/transaction", json={
        "asset_symbol": "ETH",
        "transaction_type": "BUY",
        "quantity": 2.0,
        "price": 3000.0
    })

    # Sell 1.0 ETH at $4000 (gain = $1000)
    sell_res = auth_client.post("/api/portfolio/transaction", json={
        "asset_symbol": "ETH",
        "transaction_type": "SELL",
        "quantity": 1.0,
        "price": 4000.0
    })
    assert sell_res.status_code == 201
    tx = sell_res.get_json()["transaction"]
    assert tx["realized_pnl"] == 1000.0

    # Attempting to sell more than owned (2.0 ETH when only 1.0 remains) -> 400
    excess_res = auth_client.post("/api/portfolio/transaction", json={
        "asset_symbol": "ETH",
        "transaction_type": "SELL",
        "quantity": 2.0,
        "price": 4000.0
    })
    assert excess_res.status_code == 400

    # Sell remaining 1.0 ETH at $3500 (gain = $500)
    final_sell = auth_client.post("/api/portfolio/transaction", json={
        "asset_symbol": "ETH",
        "transaction_type": "SELL",
        "quantity": 1.0,
        "price": 3500.0
    })
    assert final_sell.status_code == 201
    assert final_sell.get_json()["transaction"]["realized_pnl"] == 500.0

    # Query transaction ledger summary
    ledger_res = auth_client.get("/api/portfolio/transactions")
    assert ledger_res.status_code == 200
    summary = ledger_res.get_json()["summary"]
    assert summary["total_transactions"] == 3
    assert summary["net_realized_pnl"] == 1500.0

def test_circuit_breaker_resilience():
    """Verify CircuitBreaker state transitions: CLOSED -> OPEN on repeated failures."""
    cb = CircuitBreaker(failure_threshold=3, recovery_timeout=5.0, name="TestBreaker")
    assert cb.state == "CLOSED"

    def faulty_call():
        raise ConnectionError("Upstream timeout")

    # Trigger 3 failures
    for _ in range(3):
        with pytest.raises(ConnectionError):
            cb.call(faulty_call)

    # 4th call should fast-fail with CircuitBreakerOpenException without invoking upstream
    assert cb.state == "OPEN"
    with pytest.raises(CircuitBreakerOpenException):
        cb.call(faulty_call)

    status = cb.get_status()
    assert status["state"] == "OPEN"
    assert status["failure_count"] == 3

def test_system_info_endpoint(client):
    """Verify /api/system/info returns metadata, runtime telemetry, and authors."""
    response = client.get("/api/system/info")
    assert response.status_code == 200
    info = response.get_json()
    assert info["status"] == "success"
    assert info["service"] == "FinPulse DevOps Platform"
    assert info["version"] == "1.2.0"
    authors = [a["name"] for a in info["authors"]]
    assert "Vivek Rana" in authors
    assert "portfolio_transaction_ledger" in info["active_features"]
    assert "circuit_breaker" in info
