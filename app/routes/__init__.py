"""
Routes Blueprint Registry
"""
from app.routes.auth import auth_bp
from app.routes.market import market_bp
from app.routes.portfolio import portfolio_bp
from app.routes.alerts import alerts_bp
from app.routes.web import web_bp

__all__ = ["auth_bp", "market_bp", "portfolio_bp", "alerts_bp", "web_bp"]
