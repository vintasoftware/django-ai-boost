#!/usr/bin/env python
"""Tests for the run_check MCP tool."""

import pytest

from django_ai_boost.server_fastmcp import run_check


@pytest.mark.asyncio
async def test_run_check_defaults() -> None:
    result = await run_check()

    assert "error" not in result
    assert result["success"] is True
    assert result["fail_level"] == "ERROR"
    assert isinstance(result["summary"], dict)
    assert result["total_issues"] == sum(result["summary"].values())


@pytest.mark.asyncio
async def test_run_check_with_app_labels() -> None:
    result = await run_check(app_labels=["blog"])

    assert "error" not in result
    assert result["success"] is True
    assert result["checked_apps"] == ["blog"]


@pytest.mark.asyncio
async def test_run_check_with_tags() -> None:
    result = await run_check(tags=["models", "urls"])

    assert "error" not in result
    assert result["success"] is True
    assert result["tags"] == ["models", "urls"]


@pytest.mark.asyncio
async def test_run_check_with_deploy_and_databases() -> None:
    result = await run_check(deploy=True, databases=["default"])

    assert "error" not in result
    assert result["success"] is True
    assert result["deploy_checks"] is True


@pytest.mark.asyncio
async def test_run_check_with_warning_fail_level() -> None:
    result = await run_check(fail_level="WARNING")

    assert "error" not in result
    assert result["success"] is True
    assert result["fail_level"] == "WARNING"


@pytest.mark.asyncio
async def test_run_check_invalid_app_returns_error() -> None:
    result = await run_check(app_labels=["nonexistent_app"])

    assert "error" in result
    assert "App not found" in result["error"]


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))
