"""
Authentication API Endpoints
Provides registration, login, logout, and session profile inspection.
"""
from functools import wraps
from flask import Blueprint, request, jsonify, session
from app.extensions import db
from app.models import User, MarketAuditLog

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"status": "error", "message": "Authentication required"}), 401
        current_user = db.session.get(User, user_id)
        if not current_user:
            session.clear()
            return jsonify({"status": "error", "message": "User not found"}), 401
        return f(current_user, *args, **kwargs)
    return decorated_function

@auth_bp.route("/register", methods=["POST"])
def register():
    """Register a new user account."""
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not username or not email or not password:
        return jsonify({"status": "error", "message": "Username, email, and password are required"}), 400

    if len(password) < 6:
        return jsonify({"status": "error", "message": "Password must be at least 6 characters"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"status": "error", "message": "Username is already registered"}), 409

    if User.query.filter_by(email=email).first():
        return jsonify({"status": "error", "message": "Email is already registered"}), 409

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    log = MarketAuditLog(user_id=user.id, action="USER_REGISTERED", details=f"User {username} registered")
    db.session.add(log)
    db.session.commit()

    # Automatically log the user in
    session["user_id"] = user.id
    session["username"] = user.username

    return jsonify({
        "status": "success",
        "message": "User registered successfully",
        "user": user.to_dict()
    }), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    """Authenticate existing user credentials and establish session."""
    data = request.get_json() or {}
    identifier = data.get("username", "").strip()
    password = data.get("password", "")

    if not identifier or not password:
        return jsonify({"status": "error", "message": "Username/email and password are required"}), 400

    user = User.query.filter(
        (User.username == identifier) | (User.email == identifier.lower())
    ).first()

    if not user or not user.check_password(password):
        return jsonify({"status": "error", "message": "Invalid username or password"}), 401

    session["user_id"] = user.id
    session["username"] = user.username

    log = MarketAuditLog(user_id=user.id, action="USER_LOGIN", details=f"User {user.username} logged in")
    db.session.add(log)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Login successful",
        "user": user.to_dict()
    }), 200

@auth_bp.route("/logout", methods=["POST"])
def logout():
    """Terminate current user session."""
    user_id = session.pop("user_id", None)
    session.pop("username", None)

    if user_id:
        log = MarketAuditLog(user_id=user_id, action="USER_LOGOUT", details="Session terminated")
        db.session.add(log)
        db.session.commit()

    return jsonify({"status": "success", "message": "Logged out successfully"}), 200

@auth_bp.route("/me", methods=["GET"])
@login_required
def get_current_user(current_user):
    """Retrieve profile of currently authenticated user."""
    return jsonify({
        "status": "success",
        "user": current_user.to_dict()
    }), 200
