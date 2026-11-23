# FinPulse REST API Reference Manual

The **FinPulse** platform exposes standardized RESTful JSON endpoints for authentication, asset market queries, portfolio management, alert rule configurations, and container observability.

---

## Base URLs
- **Local Development:** `http://localhost:5050`
- **Kubernetes NodePort:** `http://<node-ip>:30050`
- **Production Ingress:** `http://finpulse.local`

---

## 1. Observability & Health Probes

### `GET /health`
Returns service status, database connectivity, and active version.
```json
{
  "app": "FinPulse",
  "database": "CONNECTED",
  "environment": "production",
  "status": "UP",
  "version": "1.0.0"
}
```

### `GET /live`
Kubernetes liveness probe.
```json
{ "status": "ALIVE" }
```

### `GET /ready`
Kubernetes readiness probe.
```json
{ "status": "READY", "traffic_enabled": true }
```

### `GET /metrics`
Prometheus text-formatted operational metrics. Exposes request throughput counters, latency histograms, and alert gauges.

### `GET /api/system/info`
Returns platform release version (v1.2.0), environment runtime, active feature flags, author credits, and SRE Circuit Breaker state.

---

## 2. Authentication API (`/api/auth`)

### `POST /api/auth/register`
Creates a new user profile.
- **Payload:**
  ```json
  {
    "username": "trader_riya",
    "email": "riya@example.com",
    "password": "SecurePassword123"
  }
  ```
- **Response (201 Created):**
  ```json
  {
    "status": "success",
    "message": "User registered successfully",
    "user": {
      "id": 1,
      "username": "trader_riya",
      "email": "riya@example.com"
    }
  }
  ```

### `POST /api/auth/login`
Authenticates credentials and establishes session cookie.
- **Payload:**
  ```json
  {
    "username": "trader_riya",
    "password": "SecurePassword123"
  }
  ```

### `POST /api/auth/logout`
Terminates current session.

### `GET /api/auth/me`
Retrieves currently logged-in user details.

---

## 3. Market Intelligence API (`/api/market`)

### `GET /api/market/overview`
Retrieves all asset quotes and 24h market performance metrics.

### `GET /api/market/quote/<symbol>`
Fetches detailed real-time quote for specified asset ticker (e.g. `BTC`, `ETH`, `AAPL`).

### `GET /api/market/history/<symbol>?points=14`
Returns time-series telemetry points for chart visualization.

### `GET /api/market/search?q=<query>`
Searches supported crypto and stock catalog.

### `GET /api/market/stats`
Returns operational caching telemetry, total supported asset counts, cache hit ratio, and service uptime.

### `GET /api/market/technical/<symbol>`
Calculates real-time quantitative technical indicators:
- `rsi_14`: 14-period Relative Strength Index.
- `sma_7` & `sma_14`: 7-day and 14-day Simple Moving Averages.
- `bollinger_upper`, `bollinger_middle`, `bollinger_lower`: Volatility bands.
- `signal`: Trading action recommendation (`BUY`, `SELL`, `HOLD`, `STRONG_BUY`, `STRONG_SELL`).

### `GET /api/market/sentiment`
Returns macro Fear & Greed composite sentiment index (0-100), market breadth ratios, and top bullish/bearish market movers.

### `GET /api/market/watchlist`
*Requires authentication.* Retrieves user's pinned watchlist with real-time pricing and technical signals.

### `POST /api/market/watchlist`
*Requires authentication.* Adds a ticker to the user's personal watchlist.

### `DELETE /api/market/watchlist/<symbol>`
*Requires authentication.* Removes a ticker from user's watchlist.

---

## 4. Portfolio Management API (`/api/portfolio`)
*Requires active user authentication.*

### `GET /api/portfolio`
Returns all portfolio asset holdings with live valuations, cost basis, and unrealized profit/loss.

### `POST /api/portfolio`
Adds an asset holding to portfolio.
- **Payload:**
  ```json
  {
    "asset_symbol": "BTC",
    "quantity": 0.5,
    "buy_price": 62500.0,
    "notes": "DCA dip acquisition"
  }
  ```

### `GET /api/portfolio/<id>`
Retrieves single asset details with profit/loss metrics.

### `PUT /api/portfolio/<id>`
Updates holding quantity or purchase price.

### `DELETE /api/portfolio/<id>`
Deletes asset from portfolio.

### `GET /api/portfolio/analytics`
Computes deep portfolio analytics:
- Asset class allocation percentages (`crypto` vs `stock`).
- Asset holding weights and concentration.
- Top performing and worst performing holdings.
- Diversification risk rating (`WELL_DIVERSIFIED`, `MODERATELY_DIVERSIFIED`, `HIGHLY_CONCENTRATED`).

### `GET /api/portfolio/export?format=json|csv`
Exports portfolio holdings in machine-readable JSON or downloadable CSV format.

### `POST /api/portfolio/transaction`
Executes and logs an asset trade (`BUY` or `SELL`):
- `BUY`: Automatically recalculates weighted average cost-basis of portfolio holdings.
- `SELL`: Verifies holding sufficiency, deducts quantity, and calculates net realized profit/loss.
- **Payload:**
  ```json
  {
    "asset_symbol": "BTC",
    "transaction_type": "BUY",
    "quantity": 0.5,
    "price": 68000.0,
    "notes": "Dip accumulation"
  }
  ```

### `GET /api/portfolio/transactions`
Retrieves the immutable transaction ledger with cumulative buy volume, sell volume, and net realized P&L.

---

## 5. Alerts Engine API (`/api/alerts`)
*Requires active user authentication.*

### `GET /api/alerts`
Lists user configured price alert monitoring rules.

### `POST /api/alerts`
Creates new threshold rule.
- **Payload:**
  ```json
  {
    "asset_symbol": "ETH",
    "target_price": 3800.0,
    "condition": "above"
  }
  ```

### `POST /api/alerts/<id>/toggle`
Toggles alert between active and paused.

### `POST /api/alerts/evaluate`
Triggers manual evaluation across user alerts and records triggered status.

### `DELETE /api/alerts/<id>`
Deletes alert rule.
