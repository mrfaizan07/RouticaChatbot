"""Unit tests for Argon2 password hashing and JWT token handling."""

import pytest
from app.core.exceptions import UnauthorizedException
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_argon2_hashing_and_verification():
    raw_password = "SecurePassword2026!"
    hashed = hash_password(raw_password)
    assert hashed != raw_password
    assert hashed.startswith("$argon2id$")
    assert verify_password(raw_password, hashed) is True
    assert verify_password("IncorrectPassword", hashed) is False


def test_jwt_token_flow():
    token = create_access_token(subject="user_admin_01", role="admin")
    payload = decode_access_token(token)
    assert payload["sub"] == "user_admin_01"
    assert payload["role"] == "admin"
    assert "exp" in payload


def test_invalid_jwt_token_rejection():
    with pytest.raises(UnauthorizedException):
        decode_access_token("malformed.jwt.token")

