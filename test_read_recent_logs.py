#!/usr/bin/env python
"""Tests for the read_recent_logs tool."""

import asyncio
import logging
import os
import sys
from pathlib import Path
from uuid import uuid4

# Add fixtures/testproject to path
fixtures_path = Path(__file__).parent / "fixtures" / "testproject"
sys.path.insert(0, str(fixtures_path))

# Set up Django settings to use the test project
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "testproject.settings")

import django

from django_ai_boost.server_fastmcp import read_recent_logs

django.setup()


def _flush_root_handlers() -> None:
    for handler in logging.getLogger().handlers:
        flush = getattr(handler, "flush", None)
        if callable(flush):
            flush()


async def test_read_recent_logs_success() -> None:
    marker = f"read_recent_logs_test_{uuid4().hex}"
    logging.getLogger("django_ai_boost.tests").info(marker)
    _flush_root_handlers()

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


async def main() -> None:
    await test_read_recent_logs_success()
    await test_read_recent_logs_limit_cap()
    await test_read_recent_logs_invalid_inputs()
    print("All read_recent_logs tests passed! ✓")


if __name__ == "__main__":
    asyncio.run(main())
