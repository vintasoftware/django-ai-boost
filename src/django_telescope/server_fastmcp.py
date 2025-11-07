from __future__ import annotations

import logging
import os
import sys
from typing import Any

import django
from asgiref.sync import sync_to_async
from django.apps import apps
from django.conf import settings
from django.core.management import get_commands
from django.db import connection
from django.urls import get_resolver
from fastmcp import FastMCP

logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("Django Telescope Server")


def initialize_django(settings_module: str | None = None) -> None:
    """Initialize Django with the specified settings module."""
    if settings_module is None:
        settings_module = os.environ.get("DJANGO_SETTINGS_MODULE")

    if not settings_module:
        raise ValueError(
            "Django settings module not specified. "
            "Set DJANGO_SETTINGS_MODULE environment variable or pass settings_module parameter."
        )

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)

    # Add the project directory to the Python path if needed
    project_dir = os.getcwd()
    if project_dir not in sys.path:
        sys.path.insert(0, project_dir)

    django.setup()


@mcp.tool()
async def application_info() -> dict[str, Any]:
    """
    Get Django application information including versions, installed apps, and database configuration.

    Returns:
        Dictionary containing Django version, Python version, installed apps, middleware, and database engine.
    """
    import django

    installed_apps = list(settings.INSTALLED_APPS)
    middleware = list(settings.MIDDLEWARE) if hasattr(settings, "MIDDLEWARE") else []

    db_config = settings.DATABASES.get("default", {})
    db_engine = db_config.get("ENGINE", "unknown").split(".")[-1]

    all_models = apps.get_models()

    return {
        "django_version": django.get_version(),
        "python_version": sys.version,
        "installed_apps": installed_apps,
        "middleware": middleware,
        "database_engine": db_engine,
        "models_count": len(all_models),
        "debug_mode": settings.DEBUG,
    }


@mcp.tool()
async def get_setting(key: str) -> Any:
    """
    Get a Django setting value using dot notation.

    Args:
        key: Setting key using dot notation (e.g., "DATABASES.default.ENGINE")

    Returns:
        The setting value or an error message if not found.
    """
    try:
        parts = key.split(".")
        value = settings

        for part in parts:
            if hasattr(value, part):
                value = getattr(value, part)
            elif isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return {"error": f"Setting '{key}' not found"}

        if isinstance(value, (str, int, float, bool, type(None))):
            return {"key": key, "value": value}
        elif isinstance(value, (list, tuple)):
            return {"key": key, "value": list(value)}
        elif isinstance(value, dict):
            return {"key": key, "value": value}
        else:
            return {"key": key, "value": str(value)}

    except Exception as e:
        return {"error": f"Error retrieving setting: {str(e)}"}


@mcp.tool()
async def list_models() -> list[dict[str, Any]]:
    """
    List all Django models with their fields, types, and relationships.

    Returns:
        List of models with detailed field information.
    """
    models_info = []

    for model in apps.get_models():
        app_label = model._meta.app_label
        model_name = model._meta.object_name

        fields = []
        for field in model._meta.get_fields():
            field_info = {
                "name": field.name,
                "type": field.__class__.__name__,
            }

            if hasattr(field, "max_length") and field.max_length:
                field_info["max_length"] = field.max_length

            if hasattr(field, "null"):
                field_info["null"] = field.null

            if hasattr(field, "blank"):
                field_info["blank"] = field.blank

            if hasattr(field, "related_model") and field.related_model:
                field_info["related_model"] = field.related_model._meta.label

            if hasattr(field, "primary_key"):
                field_info["primary_key"] = field.primary_key

            fields.append(field_info)

        models_info.append(
            {
                "app": app_label,
                "model": model_name,
                "db_table": model._meta.db_table,
                "fields": fields,
            }
        )

    return models_info


@mcp.tool()
async def list_urls() -> list[dict[str, Any]]:
    """
    List all URL patterns in the Django project.

    Returns:
        List of URL patterns with names and view handlers.
    """
    url_patterns = []

    def extract_urls(urlpatterns, prefix=""):
        for pattern in urlpatterns:
            pattern_str = str(pattern.pattern)
            full_pattern = prefix + pattern_str

            if hasattr(pattern, "url_patterns"):
                extract_urls(pattern.url_patterns, full_pattern)
            else:
                url_info = {
                    "pattern": full_pattern,
                    "name": pattern.name if hasattr(pattern, "name") else None,
                }

                if hasattr(pattern, "callback"):
                    callback = pattern.callback
                    if callback:
                        if hasattr(callback, "view_class"):
                            # Class-based view
                            url_info["view"] = (
                                f"{callback.view_class.__module__}.{callback.view_class.__name__}"
                            )
                        elif hasattr(callback, "__name__"):
                            # Function-based view
                            url_info["view"] = (
                                f"{callback.__module__}.{callback.__name__}"
                            )
                        else:
                            url_info["view"] = str(callback)

                url_patterns.append(url_info)

    try:
        resolver = get_resolver()
        extract_urls(resolver.url_patterns)
    except Exception as e:
        return [{"error": f"Error extracting URLs: {str(e)}"}]

    return url_patterns


@mcp.tool()
async def database_schema() -> dict[str, Any]:
    """
    Get the complete database schema including tables, columns, indexes, and foreign keys.

    Returns:
        Dictionary containing complete database schema information.
    """

    @sync_to_async
    def get_schema():
        schema_info = {
            "tables": [],
            "database_name": connection.settings_dict.get("NAME"),
            "database_engine": connection.settings_dict.get("ENGINE"),
        }

        with connection.cursor() as cursor:
            tables = connection.introspection.table_names()

            for table_name in tables:
                table_info = {
                    "name": table_name,
                    "columns": [],
                    "indexes": [],
                    "foreign_keys": [],
                }

                table_description = connection.introspection.get_table_description(
                    cursor, table_name
                )
                for column in table_description:
                    column_info = {
                        "name": column.name,
                        "type": str(column.type_code),
                        "internal_size": column.internal_size,
                        "null_ok": column.null_ok,
                    }
                    table_info["columns"].append(column_info)

                indexes = connection.introspection.get_constraints(cursor, table_name)
                for index_name, index_info in indexes.items():
                    if index_info.get("index"):
                        table_info["indexes"].append(
                            {
                                "name": index_name,
                                "columns": index_info.get("columns", []),
                                "unique": index_info.get("unique", False),
                                "primary_key": index_info.get("primary_key", False),
                            }
                        )

                relations = connection.introspection.get_relations(cursor, table_name)
                for column, (related_table, related_column) in relations.items():
                    table_info["foreign_keys"].append(
                        {
                            "column": column,
                            "related_table": related_table,
                            "related_column": related_column,
                        }
                    )

                schema_info["tables"].append(table_info)

        return schema_info

    return await get_schema()


@mcp.tool()
async def list_migrations() -> list[dict[str, Any]]:
    """
    List all migrations and their application status.

    Returns:
        List of migrations per app with their applied status.
    """

    @sync_to_async
    def get_migrations():
        from django.db.migrations.loader import MigrationLoader

        loader = MigrationLoader(connection)

        migrations_info = []

        for app_label in loader.migrated_apps:
            app_migrations = []

            for migration_name in loader.disk_migrations:
                if migration_name[0] == app_label:
                    is_applied = migration_name in loader.applied_migrations
                    app_migrations.append(
                        {
                            "name": migration_name[1],
                            "applied": is_applied,
                        }
                    )

            if app_migrations:
                migrations_info.append(
                    {
                        "app": app_label,
                        "migrations": sorted(app_migrations, key=lambda x: x["name"]),
                    }
                )

        return sorted(migrations_info, key=lambda x: x["app"])

    return await get_migrations()


@mcp.tool()
async def list_management_commands() -> list[dict[str, Any]]:
    """
    List all available Django management commands.

    Returns:
        List of management commands with their app labels.
    """
    commands = get_commands()

    commands_info = []
    for command_name, app_name in sorted(commands.items()):
        commands_info.append(
            {
                "command": command_name,
                "app": app_name,
            }
        )

    return commands_info


@mcp.tool()
async def get_absolute_url(
    app_label: str, model_name: str, pk: int | str
) -> dict[str, Any]:
    """
    Get the absolute URL for a specific model instance.

    Args:
        app_label: The app label (e.g., "blog")
        model_name: The model name (e.g., "Post")
        pk: The primary key of the instance

    Returns:
        Dictionary containing the absolute URL or error message.
    """

    @sync_to_async
    def get_url():
        try:
            model = apps.get_model(app_label, model_name)
        except LookupError:
            return {"error": f"Model '{app_label}.{model_name}' not found"}

        try:
            instance = model.objects.get(pk=pk)
        except model.DoesNotExist:
            return {
                "error": f"Instance with pk={pk} not found in {app_label}.{model_name}"
            }
        except Exception as e:
            return {"error": f"Error fetching instance: {str(e)}"}

        if hasattr(instance, "get_absolute_url") and callable(
            getattr(instance, "get_absolute_url")
        ):
            try:
                url = instance.get_absolute_url()
                return {
                    "app": app_label,
                    "model": model_name,
                    "pk": pk,
                    "url": url,
                }
            except Exception as e:
                return {"error": f"Error calling get_absolute_url(): {str(e)}"}
        else:
            return {
                "error": f"Model {app_label}.{model_name} does not have a get_absolute_url() method"
            }

    return await get_url()


@mcp.tool()
async def reverse_url(
    url_name: str, args: list[Any] | None = None, kwargs: dict[str, Any] | None = None
) -> dict[str, Any]:
    """
    Reverse a URL pattern name to get its URL path.

    Args:
        url_name: The URL pattern name (e.g., "post_detail" or "admin:index")
        args: Optional list of positional arguments for the URL
        kwargs: Optional dictionary of keyword arguments for the URL

    Returns:
        Dictionary containing the reversed URL or error message.
    """
    from django.urls import reverse
    from django.urls.exceptions import NoReverseMatch

    try:
        reverse_args = args if args else []
        reverse_kwargs = kwargs if kwargs else {}

        url = reverse(url_name, args=reverse_args, kwargs=reverse_kwargs)

        return {
            "url_name": url_name,
            "url": url,
            "args": args,
            "kwargs": kwargs,
        }
    except NoReverseMatch as e:
        return {"error": f"No reverse match found for '{url_name}': {str(e)}"}
    except Exception as e:
        return {"error": f"Error reversing URL: {str(e)}"}


def run_server(settings_module: str | None = None, transport: str = "stdio"):
    """
    Run the Django MCP server.

    Args:
        settings_module: Django settings module path
        transport: Transport type (stdio or sse)
    """
    # Initialize Django before starting the server
    initialize_django(settings_module)

    # Run the FastMCP server
    mcp.run(transport=transport)


if __name__ == "__main__":
    run_server()
