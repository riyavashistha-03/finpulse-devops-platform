"""
SQLAlchemy Data Models for FinPulse
Includes User, PortfolioAsset, PriceAlert, and MarketAuditLog entities.
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db

class User(db.Model):
    """User account entity with secure password hashing and relationship cascade."""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    portfolio_assets = db.relationship("PortfolioAsset", backref="user", cascade="all, delete-orphan", lazy="dynamic")
    alerts = db.relationship("PriceAlert", backref="user", cascade="all, delete-orphan", lazy="dynamic")
    audit_logs = db.relationship("MarketAuditLog", backref="user", cascade="all, delete-orphan", lazy="dynamic")

    def set_password(self, password: str):
        """Hash and persist user password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify plain password against stored cryptographic hash."""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Serialize user profile."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class PortfolioAsset(db.Model):
    """Portfolio holding record representing crypto or stock assets held by a user."""
    __tablename__ = "portfolio_assets"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    asset_symbol = db.Column(db.String(12), nullable=False, index=True)
    asset_name = db.Column(db.String(64), nullable=False)
    asset_type = db.Column(db.String(16), default="crypto", nullable=False) # 'crypto' or 'stock'
    quantity = db.Column(db.Float, nullable=False)
    buy_price = db.Column(db.Float, nullable=False)
    notes = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        """Serialize portfolio asset with cost basis."""
        total_cost = round(self.quantity * self.buy_price, 2)
        return {
            "id": self.id,
            "user_id": self.user_id,
            "asset_symbol": self.asset_symbol.upper(),
            "asset_name": self.asset_name,
            "asset_type": self.asset_type,
            "quantity": float(self.quantity),
            "buy_price": float(self.buy_price),
            "total_cost": total_cost,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class PriceAlert(db.Model):
    """User-configured price alert rule for automated monitoring."""
    __tablename__ = "price_alerts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    asset_symbol = db.Column(db.String(12), nullable=False, index=True)
    target_price = db.Column(db.Float, nullable=False)
    condition = db.Column(db.String(8), nullable=False) # 'above' or 'below'
    is_triggered = db.Column(db.Boolean, default=False, nullable=False)
    triggered_at = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        """Serialize alert rule."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "asset_symbol": self.asset_symbol.upper(),
            "target_price": float(self.target_price),
            "condition": self.condition,
            "is_triggered": self.is_triggered,
            "triggered_at": self.triggered_at.isoformat() if self.triggered_at else None,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class MarketAuditLog(db.Model):
    """Audit log tracking system operations, order executions, and alerts."""
    __tablename__ = "market_audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = db.Column(db.String(64), nullable=False)
    details = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "action": self.action,
            "details": self.details,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }
