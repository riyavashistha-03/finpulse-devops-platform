"""
Pytest Fixtures and Global Test Configuration
"""
import pytest
from app import create_app
from app.extensions import db
from app.models import User, PortfolioAsset, PriceAlert

@pytest.fixture(scope="session")
def app():
    """Create isolated application instance configured for testing."""
    _app = create_app("testing")
    with _app.app_context():
        db.create_all()
        yield _app
        db.drop_all()

@pytest.fixture(scope="function")
def client(app):
    """Test client with isolated database transaction per test."""
    with app.app_context():
        # Clear tables between tests
        db.session.query(PriceAlert).delete()
        db.session.query(PortfolioAsset).delete()
        db.session.query(User).delete()
        db.session.commit()
        
        with app.test_client() as test_client:
            yield test_client

@pytest.fixture(scope="function")
def registered_user(app):
    """Fixture to create and return a test user in DB."""
    with app.app_context():
        user = User(username="trader_riya", email="riya@finpulse.io")
        user.set_password("securePassword123")
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        return user

@pytest.fixture(scope="function")
def auth_client(client, registered_user):
    """Test client pre-authenticated with registered_user session."""
    with client.session_transaction() as sess:
        sess["user_id"] = registered_user.id
        sess["username"] = registered_user.username
    return client
