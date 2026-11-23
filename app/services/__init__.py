"""
Services package initialization
"""
from app.services.market_data import MarketDataService
from app.services.alert_engine import AlertEngine
from app.services.circuit_breaker import CircuitBreaker

circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=15.0, name="MarketDataBreaker")
market_service = MarketDataService()
alert_engine = AlertEngine(market_service)
