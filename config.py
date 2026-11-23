"""
FinPulse Configuration Module
Supports Development, Testing, and Production environments.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Config:
    """Base configuration with default settings."""
    SECRET_KEY = os.getenv("SECRET_KEY", "finpulse-devops-insecure-secret-key-change-in-prod")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PORT = int(os.getenv("PORT", 5050))
    HOST = os.getenv("HOST", "0.0.0.0")
    APP_NAME = "FinPulse"
    APP_VERSION = "1.2.0"
    ENVIRONMENT = os.getenv("FLASK_ENV", "development")
    CACHE_EXPIRATION_SECONDS = int(os.getenv("CACHE_EXPIRATION_SECONDS", 60))
    PROMETHEUS_METRICS_ENABLED = os.getenv("PROMETHEUS_METRICS_ENABLED", "true").lower() == "true"
    DEFAULT_CURRENCY = os.getenv("DEFAULT_CURRENCY", "USD")

class DevelopmentConfig(Config):
    """Local development configuration."""
    DEBUG = True
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'instance' / 'finpulse_dev.db'}"
    )

class TestingConfig(Config):
    """Test suite configuration using isolated in-memory or temporary database."""
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URL", "sqlite:///:memory:")
    SECRET_KEY = "test-secret-key-for-ci-cd-pipelines"
    CACHE_EXPIRATION_SECONDS = 0

class ProductionConfig(Config):
    """Hardened production configuration."""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'instance' / 'finpulse_prod.db'}"
    )
    # Require production secret key override in real deployment
    SECRET_KEY = os.getenv("SECRET_KEY", "prod-finpulse-super-secret-key-84930219")

config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}

def get_config():
    """Retrieve active configuration object based on environment variable."""
    env = os.getenv("FLASK_ENV", "development").lower()
    return config_by_name.get(env, DevelopmentConfig)
