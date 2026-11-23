"""
FinPulse Application Factory
Configures Flask, database models, blueprints, Prometheus telemetry, and health probes.
"""
import os
import time
from pathlib import Path
from flask import Flask, jsonify, request, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from app.extensions import (
    db,
    HTTP_REQUESTS_TOTAL,
    REQUEST_DURATION_SECONDS,
    ACTIVE_PORTFOLIOS,
    ACTIVE_ALERTS
)
from app.models import User, PortfolioAsset, PriceAlert
from app.routes.auth import auth_bp
from app.routes.market import market_bp
from app.routes.portfolio import portfolio_bp
from app.routes.alerts import alerts_bp
from app.routes.web import web_bp
from config import config_by_name

def create_app(config_name: str = None) -> Flask:
    """Application factory for FinPulse."""
    app = Flask(__name__)

    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development").lower()

    config_class = config_by_name.get(config_name, config_by_name["default"])
    app.config.from_object(config_class)

    # Ensure instance directory exists for SQLite database
    instance_dir = Path(app.root_path).parent / "instance"
    instance_dir.mkdir(parents=True, exist_ok=True)

    # Initialize extensions
    db.init_app(app)

    # Telemetry Request Timing Hooks
    @app.before_request
    def start_timer():
        request._start_time = time.time()

    @app.after_request
    def record_metrics(response):
        if hasattr(request, "_start_time") and request.endpoint != "metrics":
            duration = time.time() - request._start_time
            endpoint = request.endpoint or "unknown"
            method = request.method
            status = str(response.status_code)
            try:
                HTTP_REQUESTS_TOTAL.labels(method=method, endpoint=endpoint, status=status).inc()
                REQUEST_DURATION_SECONDS.labels(endpoint=endpoint).observe(duration)
            except Exception:
                pass
        return response

    # Health & Observability Probes
    @app.route("/health", methods=["GET"])
    def health():
        """General service health probe."""
        db_healthy = True
        try:
            db.session.execute(db.text("SELECT 1"))
        except Exception:
            db_healthy = False

        status_code = 200 if db_healthy else 503
        return jsonify({
            "status": "UP" if db_healthy else "DOWN",
            "app": "FinPulse",
            "version": app.config.get("APP_VERSION", "1.0.0"),
            "database": "CONNECTED" if db_healthy else "UNAVAILABLE",
            "environment": app.config.get("ENVIRONMENT", "unknown")
        }), status_code

    @app.route("/live", methods=["GET"])
    def liveness():
        """Kubernetes liveness probe: indicates whether container is alive."""
        return jsonify({"status": "ALIVE"}), 200

    @app.route("/ready", methods=["GET"])
    def readiness():
        """Kubernetes readiness probe: indicates whether container is ready to accept traffic."""
        try:
            db.session.execute(db.text("SELECT 1"))
            return jsonify({"status": "READY", "traffic_enabled": True}), 200
        except Exception as e:
            return jsonify({"status": "NOT_READY", "error": str(e)}), 503

    @app.route("/metrics", methods=["GET"])
    def metrics():
        """Prometheus metrics scrape target."""
        try:
            # Sync gauges before scrapers read
            with app.app_context():
                users_count = User.query.count()
                alerts_count = PriceAlert.query.filter_by(is_active=True, is_triggered=False).count()
                ACTIVE_PORTFOLIOS.set(users_count)
                ACTIVE_ALERTS.set(alerts_count)
        except Exception:
            pass
        return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(market_bp)
    app.register_blueprint(portfolio_bp)
    app.register_blueprint(alerts_bp)
    app.register_blueprint(web_bp)

    # Global Error Handlers
    @app.errorhandler(400)
    def bad_request(error):
        if request.path.startswith("/api/"):
            return jsonify({"status": "error", "message": "Bad request"}), 400
        return "Bad Request", 400

    @app.errorhandler(404)
    def not_found(error):
        if request.path.startswith("/api/"):
            return jsonify({"status": "error", "message": "Resource not found"}), 404
        return "Page Not Found", 404

    @app.errorhandler(500)
    def server_error(error):
        if request.path.startswith("/api/"):
            return jsonify({"status": "error", "message": "Internal server error"}), 500
        return "Internal Server Error", 500

    # Auto-initialize database tables in dev or testing
    with app.app_context():
        db.create_all()

    return app
