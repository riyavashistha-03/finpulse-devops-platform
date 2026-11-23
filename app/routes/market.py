"""
Market Data API Endpoints
Provides live price quotes, asset historical telemetry, and search functionality.
"""
from flask import Blueprint, request, jsonify
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
