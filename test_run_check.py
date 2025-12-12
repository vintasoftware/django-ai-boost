#!/usr/bin/env python
"""
Test script for the run_check MCP tool.
"""

import asyncio
import os
import sys

# Add the fixtures/testproject to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "fixtures", "testproject"))

# Set Django settings before importing Django modules
os.environ["DJANGO_SETTINGS_MODULE"] = "testproject.settings"

from src.django_ai_boost import server_fastmcp

initialize_django = server_fastmcp.initialize_django


async def test_run_check():
    """Test the run_check tool with various parameters."""
    print("Testing run_check tool...")
    print("=" * 80)

    # Initialize Django
    initialize_django("testproject.settings")

    # Get the actual function from the FastMCP tool
    run_check_fn = server_fastmcp.run_check.fn

    # Test 1: Run all checks
    print("\n1. Testing run_check with default parameters (all checks)...")
    result = await run_check_fn()
    print(f"   Success: {result.get('success')}")
    print(f"   Total issues: {result.get('total_issues')}")
    print(f"   Summary: {result.get('summary')}")
    if result.get("errors"):
        print(f"   Errors: {result['errors']}")
    if result.get("warnings"):
        print(f"   Warnings: {result['warnings']}")

    # Test 2: Run checks for specific app
    print("\n2. Testing run_check for 'blog' app only...")
    result = await run_check_fn(app_labels=["blog"])
    print(f"   Success: {result.get('success')}")
    print(f"   Checked apps: {result.get('checked_apps')}")
    print(f"   Total issues: {result.get('total_issues')}")
    print(f"   Summary: {result.get('summary')}")

    # Test 3: Run checks with specific tags
    print("\n3. Testing run_check with 'models' tag...")
    result = await run_check_fn(tags=["models"])
    print(f"   Success: {result.get('success')}")
    print(f"   Tags: {result.get('tags')}")
    print(f"   Total issues: {result.get('total_issues')}")
    print(f"   Summary: {result.get('summary')}")

    # Test 4: Run checks with multiple tags
    print("\n4. Testing run_check with multiple tags ['models', 'urls']...")
    result = await run_check_fn(tags=["models", "urls"])
    print(f"   Success: {result.get('success')}")
    print(f"   Tags: {result.get('tags')}")
    print(f"   Total issues: {result.get('total_issues')}")
    print(f"   Summary: {result.get('summary')}")

    # Test 5: Run deployment checks
    print("\n5. Testing run_check with deploy=True...")
    result = await run_check_fn(deploy=True)
    print(f"   Success: {result.get('success')}")
    print(f"   Deploy checks: {result.get('deploy_checks')}")
    print(f"   Total issues: {result.get('total_issues')}")
    print(f"   Summary: {result.get('summary')}")
    if result.get("warnings"):
        print(f"   Sample warnings (first 3):")
        for warning in result["warnings"][:3]:
            print(f"     - {warning['id']}: {warning['message']}")

    # Test 6: Run checks with WARNING fail level
    print("\n6. Testing run_check with fail_level='WARNING'...")
    result = await run_check_fn(fail_level="WARNING")
    print(f"   Success: {result.get('success')}")
    print(f"   Fail level: {result.get('fail_level')}")
    print(f"   Total issues: {result.get('total_issues')}")
    print(f"   Summary: {result.get('summary')}")

    # Test 7: Run checks with database parameter
    print("\n7. Testing run_check with databases=['default']...")
    result = await run_check_fn(databases=["default"])
    print(f"   Success: {result.get('success')}")
    print(f"   Total issues: {result.get('total_issues')}")
    print(f"   Summary: {result.get('summary')}")

    # Test 8: Test error handling - invalid app
    print("\n8. Testing run_check with invalid app label...")
    result = await run_check_fn(app_labels=["nonexistent_app"])
    if "error" in result:
        print(f"   ✓ Error handling works: {result['error']}")
    else:
        print(f"   ✗ Expected error, got: {result}")

    print("\n" + "=" * 80)
    print("✓ All run_check tests completed!")


if __name__ == "__main__":
    asyncio.run(test_run_check())
