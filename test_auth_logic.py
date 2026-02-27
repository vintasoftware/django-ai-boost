#!/usr/bin/env python
"""Tests for authentication helpers in server_fastmcp."""

import pytest
from django.conf import settings

from django_ai_boost.server_fastmcp import (
    create_auth_provider,
    get_auth_token,
    is_production_environment,
    validate_and_create_auth,
)


def test_production_detection() -> None:
    assert is_production_environment() is (not settings.DEBUG)


def test_token_precedence(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DJANGO_MCP_AUTH_TOKEN", raising=False)
    assert get_auth_token(None) is None
    assert get_auth_token("cli-token") == "cli-token"

    monkeypatch.setenv("DJANGO_MCP_AUTH_TOKEN", "env-token")
    assert get_auth_token(None) == "env-token"
    assert get_auth_token("cli-token") == "env-token"


def test_auth_provider_creation() -> None:
    provider = create_auth_provider("test-token-123")
    assert provider is not None


def test_validation_logic() -> None:
    assert validate_and_create_auth(None, False, "stdio") is None
    assert validate_and_create_auth(None, False, "sse") is None
    assert validate_and_create_auth("token", True, "sse") is not None
    assert validate_and_create_auth("token", False, "sse") is not None

    with pytest.raises(ValueError, match="Bearer tokens only work with SSE transport"):
        validate_and_create_auth("token", True, "stdio")

    with pytest.raises(ValueError, match="Bearer tokens only work with SSE transport"):
        validate_and_create_auth("token", False, "stdio")

    with pytest.raises(ValueError, match="Production mode detected"):
        validate_and_create_auth(None, True, "sse")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))
