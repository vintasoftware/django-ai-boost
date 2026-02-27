#!/usr/bin/env python
"""Tests for the read_recent_logs tool."""

import logging
from collections.abc import Callable
from uuid import uuid4

import pytest

from django_ai_boost.server_fastmcp import read_recent_logs


async def test_read_recent_logs_success(
    flush_root_handlers: Callable[[], None],
) -> None:
    marker = f"read_recent_logs_test_{uuid4().hex}"
    logging.getLogger("django_ai_boost.tests").info(marker)
    flush_root_handlers()

    result = await read_recent_logs(lines=200, handler_name="file")

    assert "error" not in result
    assert result["handler_filter"] == "file"
    assert result["returned_lines"] == 200
    assert "file" in result["available_handlers"]
    assert len(result["logs"]) == 1
    assert result["logs"][0]["handler"] == "file"
    assert result["logs"][0]["exists"] is True
    assert any(marker in line for line in result["logs"][0]["lines"])


async def test_read_recent_logs_limit_cap() -> None:
    result = await read_recent_logs(lines=9999, handler_name="file")

    assert "error" not in result
    assert result["requested_lines"] == 9999
    assert result["returned_lines"] == 1000


async def test_read_recent_logs_invalid_inputs() -> None:
    invalid_lines = await read_recent_logs(lines=0)
    invalid_handler = await read_recent_logs(handler_name="missing_handler")

    assert invalid_lines == {"error": "lines must be greater than 0"}
    assert invalid_handler == {
        "error": "Handler 'missing_handler' not found or is not a file-based handler"
    }


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))
