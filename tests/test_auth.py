"""
Unit & Integration Tests for Authentication
"""
import json

def test_register_success(client):
    """Verify user registration succeeds with valid credentials."""
    payload = {
        "username": "alex_investor",
        "email": "alex@finpulse.io",
        "password": "Password789!"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["status"] == "success"
    assert data["user"]["username"] == "alex_investor"
    assert "password" not in data["user"]

def test_register_duplicate_username(client, registered_user):
    """Verify duplicate username returns conflict status 409."""
    payload = {
        "username": registered_user.username,
        "email": "another@finpulse.io",
        "password": "Password789!"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 409
    data = response.get_json()
    assert "already registered" in data["message"]

def test_register_short_password(client):
    """Verify registration fails when password length is below 6 characters."""
    payload = {
        "username": "shorty",
        "email": "short@finpulse.io",
        "password": "123"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 400
    assert "at least 6 characters" in response.get_json()["message"]

def test_login_success(client, registered_user):
    """Verify successful authentication with valid credentials."""
    payload = {
        "username": registered_user.username,
        "password": "securePassword123"
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert data["user"]["username"] == registered_user.username

def test_login_invalid_password(client, registered_user):
    """Verify invalid password returns 401 unauthorized."""
    payload = {
        "username": registered_user.username,
        "password": "WrongPassword999"
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 401
    assert "Invalid username or password" in response.get_json()["message"]

def test_get_current_user_profile(auth_client, registered_user):
    """Verify authenticated user can retrieve profile details."""
    response = auth_client.get("/api/auth/me")
    assert response.status_code == 200
    data = response.get_json()
    assert data["user"]["username"] == registered_user.username
    assert data["user"]["email"] == registered_user.email

def test_logout(auth_client):
    """Verify session termination on logout."""
    response = auth_client.post("/api/auth/logout")
    assert response.status_code == 200
    assert response.get_json()["status"] == "success"
