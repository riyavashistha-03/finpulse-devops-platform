"""
Market Data API Endpoints
Provides live price quotes, asset historical telemetry, technical indicators,
composite market sentiment, personal watchlists, and search functionality.
"""
from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import WatchlistItem, MarketAuditLog
from app.routes.auth import login_required
from app.services import market_service

market_bp = Blueprint("market", __name__, url_prefix="/api/market")

@market_bp.route("/overview", methods=["GET"])
def get_market_overview():
    """Retrieve complete market snapshot across crypto and equity asset classes."""
    quotes = market_service.get_all_quotes()
    if not quotes:
        return jsonify({"status": "success", "data": [], "summary": {}}), 200

    top_gainer = max(quotes, key=lambda x: x["change_24h"])
    top_loser = min(quotes, key=lambda x: x["change_24h"])

    return jsonify({
        "status": "success",
        "data": quotes,
        "summary": {
            "total_assets_tracked": len(quotes),
            "top_gainer": {"symbol": top_gainer["symbol"], "change": top_gainer["change_24h"]},
            "top_loser": {"symbol": top_loser["symbol"], "change": top_loser["change_24h"]},
            "market_status": "ONLINE"
        }
    }), 200

@market_bp.route("/quote/<symbol>", methods=["GET"])
def get_asset_quote(symbol):
    """Retrieve detailed real-time quote for a specific ticker symbol."""
    force = request.args.get("refresh", "false").lower() == "true"
    quote = market_service.get_quote(symbol, force_refresh=force)
    if not quote:
        return jsonify({"status": "error", "message": f"Asset ticker '{symbol.upper()}' not found"}), 404

    return jsonify({"status": "success", "data": quote}), 200

@market_bp.route("/history/<symbol>", methods=["GET"])
def get_asset_history(symbol):
    """Retrieve historical chart telemetry points."""
    points = int(request.args.get("points", 14))
    history = market_service.get_history(symbol, points=min(points, 48))
    return jsonify({"status": "success", "data": history}), 200

@market_bp.route("/search", methods=["GET"])
def search_assets():
    """Search for supported assets by query keyword."""
    query = request.args.get("q", "")
    if not query:
        return jsonify({"status": "error", "message": "Search parameter 'q' is required"}), 400

    matches = market_service.search_assets(query)
    return jsonify({"status": "success", "query": query, "results": matches}), 200

@market_bp.route("/stats", methods=["GET"])
def get_market_service_stats():
    """Retrieve runtime caching telemetry and market service health."""
    stats = market_service.get_cache_stats()
    return jsonify({"status": "success", "stats": stats}), 200

@market_bp.route("/technical/<symbol>", methods=["GET"])
def get_asset_technical_indicators(symbol):
    """Retrieve quantitative technical indicators: RSI-14, SMA-7, SMA-14, Bollinger Bands, and trading signal."""
    indicators = market_service.get_technical_indicators(symbol)
    if not indicators:
        return jsonify({"status": "error", "message": f"Technical indicators unavailable for '{symbol.upper()}'"}), 404
    return jsonify({"status": "success", "data": indicators}), 200

@market_bp.route("/sentiment", methods=["GET"])
def get_market_sentiment():
    """Retrieve macro Fear & Greed sentiment index and market breadth analysis."""
    sentiment = market_service.get_market_sentiment()
    return jsonify({"status": "success", "sentiment": sentiment}), 200

@market_bp.route("/watchlist", methods=["GET"])
@login_required
def get_user_watchlist(current_user):
    """Retrieve pinned watchlist assets for authenticated user with live telemetry."""
    items = WatchlistItem.query.filter_by(user_id=current_user.id).order_by(WatchlistItem.added_at.desc()).all()
    watchlist_data = []
    for item in items:
        quote = market_service.get_quote(item.asset_symbol)
        tech = market_service.get_technical_indicators(item.asset_symbol)
        entry = item.to_dict()
        entry.update({
            "current_price": quote["price"] if quote else 0.0,
            "change_24h": quote["change_24h"] if quote else 0.0,
            "high_24h": quote["high_24h"] if quote else 0.0,
            "low_24h": quote["low_24h"] if quote else 0.0,
            "technical_signal": tech["signal"] if tech else "HOLD",
            "rsi_14": tech["rsi_14"] if tech else 50.0
        })
        watchlist_data.append(entry)

    return jsonify({
        "status": "success",
        "total_watchlist_items": len(watchlist_data),
        "watchlist": watchlist_data
    }), 200

@market_bp.route("/watchlist", methods=["POST"])
@login_required
def add_to_watchlist(current_user):
    """Add a ticker symbol to the user's pinned watchlist."""
    data = request.get_json() or {}
    symbol = data.get("asset_symbol", "").strip().upper()
    if not symbol:
        return jsonify({"status": "error", "message": "asset_symbol is required"}), 400

    quote = market_service.get_quote(symbol)
    if not quote:
        return jsonify({"status": "error", "message": f"Asset symbol '{symbol}' is not supported"}), 404

    existing = WatchlistItem.query.filter_by(user_id=current_user.id, asset_symbol=symbol).first()
    if existing:
        return jsonify({"status": "error", "message": f"Asset '{symbol}' is already in your watchlist"}), 409

    item = WatchlistItem(
        user_id=current_user.id,
        asset_symbol=symbol,
        asset_name=quote["name"],
        asset_type=quote["type"]
    )
    db.session.add(item)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": f"Asset {symbol} added to watchlist",
        "item": item.to_dict()
    }), 201

@market_bp.route("/watchlist/<symbol>", methods=["DELETE"])
@login_required
def remove_from_watchlist(current_user, symbol):
    """Remove a ticker symbol from user's watchlist."""
    symbol = symbol.strip().upper()
    item = WatchlistItem.query.filter_by(user_id=current_user.id, asset_symbol=symbol).first()
    if not item:
        return jsonify({"status": "error", "message": f"Asset '{symbol}' not found in your watchlist"}), 404

    db.session.delete(item)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": f"Asset '{symbol}' removed from watchlist"
    }), 200
