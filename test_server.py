#!/usr/bin/env python
"""Integration tests for core django-ai-boost tools."""

import pytest

from django_ai_boost.server_fastmcp import (
    application_info,
    database_schema,
    get_absolute_url,
    get_setting,
    list_management_commands,
    list_migrations,
    list_models,
    reverse_url,
)


@pytest.mark.asyncio
async def test_application_info() -> None:
    result = await application_info()

    assert "django_version" in result
    assert "python_version" in result
    assert result["database_engine"] == "sqlite3"
    assert isinstance(result["installed_apps"], list)
    assert result["models_count"] > 0


@pytest.mark.asyncio
async def test_get_setting() -> None:
    debug_result = await get_setting("DEBUG")
    db_engine_result = await get_setting("DATABASES.default.ENGINE")
    missing_result = await get_setting("DOES.NOT.EXIST")

    assert debug_result["key"] == "DEBUG"
    assert isinstance(debug_result["value"], bool)
    assert db_engine_result["value"] == "django.db.backends.sqlite3"
    assert "error" in missing_result


@pytest.mark.asyncio
async def test_list_models() -> None:
    all_models = await list_models()
    blog_models = await list_models(app_labels=["blog"])

    assert all_models["total_count"] >= blog_models["total_count"]
    assert blog_models["app_filter"] == ["blog"]
    assert blog_models["total_count"] > 0
    assert all(model["app"] == "blog" for model in blog_models["models"])


@pytest.mark.asyncio
async def test_database_schema() -> None:
    result = await database_schema()

    assert result["database_engine"].endswith("sqlite3")
    assert isinstance(result["tables"], list)
    assert len(result["tables"]) > 0
    assert "name" in result["tables"][0]
    assert "columns" in result["tables"][0]


@pytest.mark.asyncio
async def test_list_migrations() -> None:
    result = await list_migrations()

    assert isinstance(result, list)
    assert len(result) > 0
    assert "app" in result[0]
    assert "migrations" in result[0]


@pytest.mark.asyncio
async def test_list_management_commands() -> None:
    result = await list_management_commands()

    commands = {item["command"] for item in result}
    assert "migrate" in commands
    assert "runserver" in commands


@pytest.mark.asyncio
async def test_get_absolute_url() -> None:
    valid_result = await get_absolute_url("blog", "Post", 1)
    invalid_model_result = await get_absolute_url("blog", "Unknown", 1)
    invalid_pk_result = await get_absolute_url("blog", "Post", 999999)

    assert "error" not in valid_result
    assert valid_result["app"] == "blog"
    assert valid_result["model"] == "Post"
    assert valid_result["url"].startswith("/post/")
    assert "error" in invalid_model_result
    assert "error" in invalid_pk_result


@pytest.mark.asyncio
async def test_reverse_url() -> None:
    post_list = await reverse_url("post_list")
    post_detail = await reverse_url("post_detail", kwargs={"pk": 1})
    admin_index = await reverse_url("admin:index")
    invalid = await reverse_url("does_not_exist")

    assert post_list["url"] == "/"
    assert post_detail["url"] == "/post/1/"
    assert admin_index["url"].startswith("/admin")
    assert "error" in invalid


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))
