#!/usr/bin/env python
"""Regression tests for MCP tool/prompt registration via the FastMCP Client.

These exercise the registration layer through FastMCP's public in-memory
client API rather than calling the underlying Python functions directly.
"""

import pytest
from fastmcp import Client, FastMCP

from django_ai_boost.server_fastmcp import register_tools

EXPECTED_TOOLS = {
    "application_info",
    "get_setting",
    "list_models",
    "list_urls",
    "database_schema",
    "list_migrations",
    "list_management_commands",
    "get_absolute_url",
    "reverse_url",
    "query_model",
    "run_check",
    "read_recent_logs",
}


@pytest.mark.asyncio
async def test_all_tools_are_registered() -> None:
    mcp_server = FastMCP("test-server")
    register_tools(mcp_server)

    async with Client(mcp_server) as client:
        tools = await client.list_tools()

    registered = {tool.name for tool in tools}
    assert EXPECTED_TOOLS <= registered
    assert len(registered) == len(EXPECTED_TOOLS)


@pytest.mark.asyncio
async def test_prompts_are_registered() -> None:
    mcp_server = FastMCP("test-server")
    register_tools(mcp_server)

    async with Client(mcp_server) as client:
        prompts = await client.list_prompts()

    assert {prompt.name for prompt in prompts} == {"search_django_docs"}


@pytest.mark.asyncio
async def test_tool_is_callable_through_client() -> None:
    mcp_server = FastMCP("test-server")
    register_tools(mcp_server)

    async with Client(mcp_server) as client:
        result = await client.call_tool("list_management_commands", {})

    assert result.is_error is False
    commands = {item["command"] for item in result.data}
    assert "migrate" in commands
    assert "runserver" in commands


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))
