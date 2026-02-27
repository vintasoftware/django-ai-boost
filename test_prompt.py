#!/usr/bin/env python
"""Tests for prompt registration and content."""

import pytest
from fastmcp import FastMCP
from fastmcp.server.middleware import MiddlewareContext
from mcp.types import ListPromptsRequest

from django_ai_boost.server_fastmcp import register_tools, search_django_docs


@pytest.mark.asyncio
async def test_search_django_docs_prompt_is_registered() -> None:
    mcp_server = FastMCP("test-server")
    register_tools(mcp_server)

    context = MiddlewareContext(message=ListPromptsRequest())
    prompts = await mcp_server._list_prompts(context)
    prompt_names = [prompt.name for prompt in prompts]

    assert "search_django_docs" in prompt_names


@pytest.mark.asyncio
async def test_search_django_docs_prompt_content() -> None:
    result = await search_django_docs("models")

    assert "models" in result
    assert "docs.djangoproject.com" in result
    assert "Current Django version" in result


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))
