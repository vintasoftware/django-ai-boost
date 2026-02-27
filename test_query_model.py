#!/usr/bin/env python
"""Tests for the query_model MCP tool."""

import pytest

from django_ai_boost.server_fastmcp import query_model


@pytest.mark.asyncio
async def test_query_model_returns_posts() -> None:
    result = await query_model(app_label="blog", model_name="Post")

    assert "error" not in result
    assert result["app"] == "blog"
    assert result["model"] == "Post"
    assert result["filters"] == {}
    assert result["order_by"] == []
    assert result["returned_count"] <= result["limit"]
    assert result["total_count"] >= result["returned_count"]
    assert isinstance(result["results"], list)


@pytest.mark.asyncio
async def test_query_model_applies_filters() -> None:
    result = await query_model(
        app_label="blog",
        model_name="Post",
        filters={"status": "published"},
    )

    assert "error" not in result
    assert result["filters"] == {"status": "published"}
    assert all(post["status"] == "published" for post in result["results"])


@pytest.mark.asyncio
async def test_query_model_applies_ordering() -> None:
    result = await query_model(
        app_label="blog",
        model_name="Post",
        order_by=["title"],
        limit=5,
    )

    assert "error" not in result
    assert result["order_by"] == ["title"]
    titles = [post["title"] for post in result["results"]]
    assert titles == sorted(titles)


@pytest.mark.asyncio
async def test_query_model_caps_limit() -> None:
    result = await query_model(app_label="blog", model_name="Post", limit=9999)

    assert "error" not in result
    assert result["limit"] == 1000
    assert result["returned_count"] <= 1000


@pytest.mark.asyncio
async def test_query_model_invalid_model_returns_error() -> None:
    result = await query_model(app_label="blog", model_name="NonExistent")

    assert "error" in result
    assert "not found" in result["error"]


@pytest.mark.asyncio
async def test_query_model_invalid_filter_returns_error() -> None:
    result = await query_model(
        app_label="blog",
        model_name="Post",
        filters={"invalid_field": "value"},
    )

    assert "error" in result
    assert "Invalid filter parameters" in result["error"]


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))
