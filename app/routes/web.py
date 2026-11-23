"""
Web UI Routes
Renders Jinja2 HTML templates for interactive browser dashboard.
"""
from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from app.models import User
from app.services import market_service

web_bp = Blueprint("web", __name__)

def get_current_user():
    """Retrieve logged in user from session if present."""
    user_id = session.get("user_id")
    if user_id:
        from app.extensions import db
        return db.session.get(User, user_id)
    return None

@web_bp.route("/")
def dashboard():
    """Render main market telemetry dashboard."""
    user = get_current_user()
    quotes = market_service.get_all_quotes()
    top_gainer = max(quotes, key=lambda x: x["change_24h"]) if quotes else None
    top_loser = min(quotes, key=lambda x: x["change_24h"]) if quotes else None
    return render_template(
        "dashboard.html",
        user=user,
        quotes=quotes,
        top_gainer=top_gainer,
        top_loser=top_loser
    )

@web_bp.route("/portfolio")
def portfolio():
    """Render portfolio management screen."""
    user = get_current_user()
    if not user:
        flash("Please log in to access your portfolio.", "warning")
        return redirect(url_for("web.login"))
    return render_template("portfolio.html", user=user)

@web_bp.route("/alerts")
def alerts():
    """Render price alerts screen."""
    user = get_current_user()
    if not user:
        flash("Please log in to manage your alerts.", "warning")
        return redirect(url_for("web.login"))
    return render_template("alerts.html", user=user)

@web_bp.route("/login")
def login():
    """Render user login view."""
    if get_current_user():
        return redirect(url_for("web.dashboard"))
    return render_template("login.html")

@web_bp.route("/register")
def register():
    """Render user registration view."""
    if get_current_user():
        return redirect(url_for("web.dashboard"))
    return render_template("register.html")

@web_bp.route("/logout")
def logout():
    """Clear session and redirect to dashboard."""
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("web.login"))
