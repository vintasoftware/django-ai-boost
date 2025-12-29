#!/usr/bin/env python
"""
Quick test to verify authentication logic works correctly.
"""
import os
import sys
from pathlib import Path

# Add fixtures to path
fixtures_path = Path(__file__).parent / "fixtures" / "testproject"
sys.path.insert(0, str(fixtures_path))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "testproject.settings")

import django
django.setup()

from django_ai_boost.server_fastmcp import (
    is_production_environment,
    get_auth_token,
    create_auth_provider,
    validate_and_create_auth,
)

def test_production_detection():
    """Test production environment detection."""
    from django.conf import settings
    print(f"\n1. Testing production detection:")
    print(f"   DEBUG={settings.DEBUG}")
    is_prod = is_production_environment()
    print(f"   is_production={is_prod}")
    print(f"   ✓ Expected: is_production={not settings.DEBUG}")
    assert is_prod == (not settings.DEBUG), "Production detection failed!"

def test_token_precedence():
    """Test token resolution with precedence."""
    print(f"\n2. Testing token precedence:")

    # No token
    os.environ.pop("DJANGO_MCP_AUTH_TOKEN", None)
    token = get_auth_token(None)
    print(f"   No env, no CLI: {token}")
    assert token is None, "Expected None when no token provided"

    # CLI only
    token = get_auth_token("cli-token")
    print(f"   No env, CLI='cli-token': {token}")
    assert token == "cli-token", "Expected CLI token"

    # Env only
    os.environ["DJANGO_MCP_AUTH_TOKEN"] = "env-token"
    token = get_auth_token(None)
    print(f"   Env='env-token', no CLI: {token}")
    assert token == "env-token", "Expected env token"

    # Both (env wins)
    token = get_auth_token("cli-token")
    print(f"   Env='env-token', CLI='cli-token': {token}")
    assert token == "env-token", "Expected env token to take precedence"

    # Cleanup
    os.environ.pop("DJANGO_MCP_AUTH_TOKEN", None)
    print("   ✓ All precedence tests passed")

def test_auth_provider_creation():
    """Test auth provider creation."""
    print(f"\n3. Testing auth provider creation:")
    provider = create_auth_provider("test-token-123")
    print(f"   Created: {type(provider).__name__}")
    assert provider is not None, "Provider should not be None"
    print("   ✓ Auth provider created successfully")

def test_validation_logic():
    """Test auth validation logic."""
    print(f"\n4. Testing validation logic:")

    # Dev mode, no token, stdio - OK
    result = validate_and_create_auth(None, False, "stdio")
    print(f"   Dev+stdio+no token: {result}")
    assert result is None, "Should return None (no auth needed)"

    # Dev mode, no token, SSE - OK
    result = validate_and_create_auth(None, False, "sse")
    print(f"   Dev+SSE+no token: {result}")
    assert result is None, "Should return None (no auth needed in dev)"

    # Prod mode, token, SSE - OK (creates provider)
    result = validate_and_create_auth("token", True, "sse")
    print(f"   Prod+SSE+token: {type(result).__name__ if result else None}")
    assert result is not None, "Should create auth provider"

    # Prod mode, token, stdio - Warning but OK
    result = validate_and_create_auth("token", True, "stdio")
    print(f"   Prod+stdio+token: {result} (should warn)")
    assert result is None, "Should return None (auth doesn't work with stdio)"

    # Prod mode, no token, SSE - ERROR
    try:
        result = validate_and_create_auth(None, True, "sse")
        print(f"   Prod+SSE+no token: Should have raised error!")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        print(f"   Prod+SSE+no token: Raised ValueError ✓")
        assert "Production mode detected" in str(e), "Error message should mention production mode"

    print("   ✓ All validation tests passed")

if __name__ == "__main__":
    try:
        test_production_detection()
        test_token_precedence()
        test_auth_provider_creation()
        test_validation_logic()
        print("\n" + "="*60)
        print("✅ All authentication logic tests passed!")
        print("="*60)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
