"""Unit tests for configuration validation and environment settings."""

import pytest
from app.config import Settings
from app.core.exceptions import ConfigurationError


def test_settings_default_values():
    """Validates default settings in testing mode."""
    s = Settings()
    assert s.APP_NAME == "Routica AI Assistant"
    assert s.API_V1_PREFIX == "/api/v1"
    assert s.EMBEDDING_DIMENSIONS == 768
    assert "routica.com" in s.scrape_allowed_domains_list


def test_production_mode_rejects_insecure_secrets():
    """Ensures production configuration fails if default secret keys are used."""
    with pytest.raises(ConfigurationError):
        Settings(
            APP_ENV="production",
            SECRET_KEY="dev-secret-key-too-short",
            JWT_SECRET_KEY="dev-jwt-secret-key-too-short",
            MONGODB_URI="mongodb://localhost:27017",
        )


def test_allowed_origins_parsing():
    """Validates comma-separated origin parsing."""
    s = Settings(ALLOWED_ORIGINS="http://localhost:5173, https://routica.com")
    assert s.allowed_origins_list == ["http://localhost:5173", "https://routica.com"]

