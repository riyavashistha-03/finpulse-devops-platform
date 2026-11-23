"""
Portfolio API Endpoints
Provides full CRUD operations for user assets and live profit/loss calculations.
"""
from flask import Blueprint, request, jsonify
from app.extensions import db, ACTIVE_PORTFOLIOS
from app.models import PortfolioAsset, MarketAuditLog
from app.routes.auth import login_required
from app.services import market_service

portfolio_bp = Blueprint("portfolio", __name__, url_prefix="/api/portfolio")

@portfolio_bp.route("", methods=["GET"])
@login_required
def get_portfolio(current_user):
    """Retrieve all portfolio assets for current user with live valuations and P&L."""
    assets = PortfolioAsset.query.filter_by(user_id=current_user.id).all()
    portfolio_items = []
    total_cost_basis = 0.0
    total_current_value = 0.0

    for asset in assets:
        quote = market_service.get_quote(asset.asset_symbol)
        current_price = quote["price"] if quote else asset.buy_price

        cost = asset.quantity * asset.buy_price
        val = asset.quantity * current_price
        pnl = val - cost
        pnl_pct = (pnl / cost * 100) if cost > 0 else 0.0

        total_cost_basis += cost
        total_current_value += val

        item_data = asset.to_dict()
        item_data.update({
            "current_price": round(current_price, 2),
            "current_value": round(val, 2),
            "unrealized_pnl": round(pnl, 2),
            "pnl_percentage": round(pnl_pct, 2)
        })
        portfolio_items.append(item_data)

    total_pnl = total_current_value - total_cost_basis
    total_pnl_pct = (total_pnl / total_cost_basis * 100) if total_cost_basis > 0 else 0.0

    return jsonify({
        "status": "success",
        "portfolio": {
            "items": portfolio_items,
            "total_items": len(portfolio_items),
            "total_invested": round(total_cost_basis, 2),
            "total_current_value": round(total_current_value, 2),
            "total_pnl": round(total_pnl, 2),
            "total_pnl_percentage": round(total_pnl_pct, 2)
        }
    }), 200

@portfolio_bp.route("", methods=["POST"])
@login_required
def add_portfolio_asset(current_user):
    """Add a new asset holding to user's portfolio."""
    data = request.get_json() or {}
    symbol = data.get("asset_symbol", "").strip().upper()
    quantity = data.get("quantity")
    buy_price = data.get("buy_price")
    notes = data.get("notes", "").strip()

    if not symbol or quantity is None or buy_price is None:
        return jsonify({"status": "error", "message": "asset_symbol, quantity, and buy_price are required"}), 400

    try:
        quantity = float(quantity)
        buy_price = float(buy_price)
        if quantity <= 0 or buy_price < 0:
            return jsonify({"status": "error", "message": "Quantity must be positive and buy_price cannot be negative"}), 400
    except (ValueError, TypeError):
        return jsonify({"status": "error", "message": "Quantity and buy_price must be numeric"}), 400

    quote = market_service.get_quote(symbol)
    asset_name = quote["name"] if quote else symbol
    asset_type = quote["type"] if quote else "crypto"

    asset = PortfolioAsset(
        user_id=current_user.id,
        asset_symbol=symbol,
        asset_name=asset_name,
        asset_type=asset_type,
        quantity=quantity,
        buy_price=buy_price,
        notes=notes
    )
    db.session.add(asset)
    db.session.commit()

    log = MarketAuditLog(
        user_id=current_user.id,
        action="PORTFOLIO_ASSET_ADDED",
        details=f"Added {quantity} {symbol} at ${buy_price}"
    )
    db.session.add(log)
    db.session.commit()

    try:
        distinct_users = db.session.query(PortfolioAsset.user_id).distinct().count()
        ACTIVE_PORTFOLIOS.set(distinct_users)
    except Exception:
        pass

    return jsonify({
        "status": "success",
        "message": "Asset added to portfolio",
        "asset": asset.to_dict()
    }), 201

@portfolio_bp.route("/<int:asset_id>", methods=["GET"])
@login_required
def get_single_asset(current_user, asset_id):
    """Retrieve details for a single portfolio asset."""
    asset = PortfolioAsset.query.filter_by(id=asset_id, user_id=current_user.id).first()
    if not asset:
        return jsonify({"status": "error", "message": "Portfolio asset not found"}), 404

    quote = market_service.get_quote(asset.asset_symbol)
    current_price = quote["price"] if quote else asset.buy_price
    cost = asset.quantity * asset.buy_price
    val = asset.quantity * current_price

    res = asset.to_dict()
    res.update({
        "current_price": round(current_price, 2),
        "current_value": round(val, 2),
        "unrealized_pnl": round(val - cost, 2),
        "pnl_percentage": round(((val - cost) / cost * 100) if cost > 0 else 0.0, 2)
    })

    return jsonify({"status": "success", "asset": res}), 200

@portfolio_bp.route("/<int:asset_id>", methods=["PUT"])
@login_required
def update_portfolio_asset(current_user, asset_id):
    """Update holdings quantity, buy price, or notes for an asset."""
    asset = PortfolioAsset.query.filter_by(id=asset_id, user_id=current_user.id).first()
    if not asset:
        return jsonify({"status": "error", "message": "Portfolio asset not found"}), 404

    data = request.get_json() or {}
    if "quantity" in data:
        try:
            q = float(data["quantity"])
            if q <= 0:
                return jsonify({"status": "error", "message": "Quantity must be positive"}), 400
            asset.quantity = q
        except (ValueError, TypeError):
            return jsonify({"status": "error", "message": "Quantity must be numeric"}), 400

    if "buy_price" in data:
        try:
            p = float(data["buy_price"])
            if p < 0:
                return jsonify({"status": "error", "message": "buy_price cannot be negative"}), 400
            asset.buy_price = p
        except (ValueError, TypeError):
            return jsonify({"status": "error", "message": "buy_price must be numeric"}), 400

    if "notes" in data:
        asset.notes = str(data["notes"]).strip()

    db.session.commit()

    log = MarketAuditLog(
        user_id=current_user.id,
        action="PORTFOLIO_ASSET_UPDATED",
        details=f"Updated asset #{asset.id} ({asset.asset_symbol})"
    )
    db.session.add(log)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Asset updated successfully",
        "asset": asset.to_dict()
    }), 200

@portfolio_bp.route("/<int:asset_id>", methods=["DELETE"])
@login_required
def delete_portfolio_asset(current_user, asset_id):
    """Delete an asset from user portfolio."""
    asset = PortfolioAsset.query.filter_by(id=asset_id, user_id=current_user.id).first()
    if not asset:
        return jsonify({"status": "error", "message": "Portfolio asset not found"}), 404

    symbol = asset.asset_symbol
    db.session.delete(asset)
    db.session.commit()

    log = MarketAuditLog(
        user_id=current_user.id,
        action="PORTFOLIO_ASSET_DELETED",
        details=f"Removed {symbol} from portfolio"
    )
    db.session.add(log)
    db.session.commit()

    return jsonify({"status": "success", "message": f"Asset {symbol} deleted successfully"}), 200
