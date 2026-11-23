"""
Services package initialization
"""
from app.services.market_data import MarketDataService
from app.services.alert_engine import AlertEngine

market_service = MarketDataService()
alert_engine = AlertEngine(market_service)
