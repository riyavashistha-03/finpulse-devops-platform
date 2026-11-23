"""
Alerts API Endpoints
Provides price threshold configuration, status tracking, and trigger evaluation.
"""
from flask import Blueprint, request, jsonify
from app.extensions import db, ACTIVE_ALERTS
from app.models import PriceAlert, MarketAuditLog
from app.routes.auth import login_required
from app.services import alert_engine, market_service

alerts_bp = Blueprint("alerts", __name__, url_prefix="/api/alerts")

@alerts_bp.route("", methods=["GET"])
@login_required
def get_alerts(current_user):
    """Retrieve all price alerts configured by current user."""
    alerts = PriceAlert.query.filter_by(user_id=current_user.id).order_by(PriceAlert.created_at.desc()).all()
    results = []
    for a in alerts:
        quote = market_service.get_quote(a.asset_symbol)
        item = a.to_dict()
        item["current_price"] = quote["price"] if quote else None
        results.append(item)

    return jsonify({"status": "success", "alerts": results}), 200

@alerts_bp.route("", methods=["POST"])
@login_required
def create_alert(current_user):
    """Create a new price threshold monitoring rule."""
    data = request.get_json() or {}
    symbol = data.get("asset_symbol", "").strip().upper()
    target_price = data.get("target_price")
    condition = data.get("condition", "above").strip().lower()

    if not symbol or target_price is None:
        return jsonify({"status": "error", "message": "asset_symbol and target_price are required"}), 400

    if condition not in ["above", "below"]:
        return jsonify({"status": "error", "message": "Condition must be 'above' or 'below'"}), 400

    try:
        target_price = float(target_price)
        if target_price <= 0:
            return jsonify({"status": "error", "message": "target_price must be greater than zero"}), 400
    except (ValueError, TypeError):
        return jsonify({"status": "error", "message": "target_price must be numeric"}), 400

    alert = PriceAlert(
        user_id=current_user.id,
        asset_symbol=symbol,
        target_price=target_price,
        condition=condition,
        is_triggered=False,
        is_active=True
    )
    db.session.add(alert)
    db.session.commit()

    log = MarketAuditLog(
        user_id=current_user.id,
        action="ALERT_CREATED",
        details=f"Created alert on {symbol}: notify when {condition} ${target_price}"
    )
    db.session.add(log)
    db.session.commit()

    try:
        total = PriceAlert.query.filter_by(is_active=True, is_triggered=False).count()
        ACTIVE_ALERTS.set(total)
    except Exception:
        pass

    return jsonify({
        "status": "success",
        "message": "Alert created successfully",
        "alert": alert.to_dict()
    }), 201

@alerts_bp.route("/<int:alert_id>/toggle", methods=["POST"])
@login_required
def toggle_alert(current_user, alert_id):
    """Toggle active state or reset triggered alert."""
    alert = PriceAlert.query.filter_by(id=alert_id, user_id=current_user.id).first()
    if not alert:
        return jsonify({"status": "error", "message": "Alert not found"}), 404

    alert.is_active = not alert.is_active
    if alert.is_active:
        alert.is_triggered = False
        alert.triggered_at = None

    db.session.commit()

    return jsonify({
        "status": "success",
        "message": f"Alert is now {'active' if alert.is_active else 'inactive'}",
        "alert": alert.to_dict()
    }), 200

@alerts_bp.route("/<int:alert_id>", methods=["DELETE"])
@login_required
def delete_alert(current_user, alert_id):
    """Delete a price alert rule."""
    alert = PriceAlert.query.filter_by(id=alert_id, user_id=current_user.id).first()
    if not alert:
        return jsonify({"status": "error", "message": "Alert not found"}), 404

    db.session.delete(alert)
    db.session.commit()

    return jsonify({"status": "success", "message": "Alert deleted successfully"}), 200

@alerts_bp.route("/evaluate", methods=["POST"])
@login_required
def evaluate_alerts(current_user):
    """Manually evaluate all alerts for current user."""
    triggered = alert_engine.evaluate_user_alerts(current_user.id)
    return jsonify({
        "status": "success",
        "evaluated_at": alert_engine.market_service.get_all_quotes()[0]["last_updated"] if alert_engine.market_service.get_all_quotes() else None,
        "triggered_count": len(triggered),
        "triggered_alerts": triggered
    }), 200
