"""
Alert Evaluation Engine
Evaluates configured price threshold conditions against active market quotes.
"""
from datetime import datetime, timezone
from typing import List, Dict, Any
from app.extensions import db, ACTIVE_ALERTS
from app.models import PriceAlert, MarketAuditLog

def utc_now():
    return datetime.now(timezone.utc)

class AlertEngine:
    def __init__(self, market_service):
        self.market_service = market_service

    def evaluate_user_alerts(self, user_id: int) -> List[Dict[str, Any]]:
        """Evaluate all active alerts belonging to a specific user."""
        alerts = PriceAlert.query.filter_by(user_id=user_id, is_active=True).all()
        triggered_events = []

        for alert in alerts:
            quote = self.market_service.get_quote(alert.asset_symbol)
            if not quote:
                continue

            current_price = quote["price"]
            triggered = False

            if alert.condition == "above" and current_price >= alert.target_price:
                triggered = True
            elif alert.condition == "below" and current_price <= alert.target_price:
                triggered = True

            if triggered and not alert.is_triggered:
                alert.is_triggered = True
                alert.triggered_at = utc_now()
                db.session.add(alert)

                log = MarketAuditLog(
                    user_id=user_id,
                    action="ALERT_TRIGGERED",
                    details=f"Alert #{alert.id} triggered: {alert.asset_symbol} is {current_price} ({alert.condition} {alert.target_price})"
                )
                db.session.add(log)

                triggered_events.append({
                    "alert_id": alert.id,
                    "symbol": alert.asset_symbol,
                    "target_price": alert.target_price,
                    "current_price": current_price,
                    "condition": alert.condition,
                    "triggered_at": alert.triggered_at.isoformat()
                })

        if triggered_events:
            db.session.commit()

        # Update metrics gauge
        try:
            total_active = PriceAlert.query.filter_by(is_active=True, is_triggered=False).count()
            ACTIVE_ALERTS.set(total_active)
        except Exception:
            pass

        return triggered_events
