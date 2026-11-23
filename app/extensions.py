"""
Flask Extensions and Global Singletons
"""
from flask_sqlalchemy import SQLAlchemy
from prometheus_client import Counter, Histogram, Gauge

db = SQLAlchemy()

# Prometheus Metrics Definitions
HTTP_REQUESTS_TOTAL = Counter(
    "finpulse_http_requests_total",
    "Total HTTP Requests handled by FinPulse",
    ["method", "endpoint", "status"]
)

REQUEST_DURATION_SECONDS = Histogram(
    "finpulse_request_duration_seconds",
    "HTTP Request latency distribution in seconds",
    ["endpoint"]
)

ACTIVE_PORTFOLIOS = Gauge(
    "finpulse_active_portfolios",
    "Current number of registered user portfolios"
)

ACTIVE_ALERTS = Gauge(
    "finpulse_active_alerts_total",
    "Total number of active price alerts monitored"
)

MARKET_PRICE_FETCHES = Counter(
    "finpulse_market_price_fetches_total",
    "Total market price retrieval operations",
    ["symbol", "source"]
)
