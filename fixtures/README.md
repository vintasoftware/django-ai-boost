# Test Fixtures

This directory contains a simple Django test project for testing the django-telescope server.

## Test Project Structure

The `testproject/` directory contains a minimal Django application with:

- **Django Project**: `testproject/` - Settings, URLs, WSGI config
- **Blog App**: `blog/` - A sample app with models demonstrating:
  - `Category` - Blog post categories
  - `Post` - Blog posts with status, author, category relationships
  - `Comment` - Comments on posts
  - `Tag` - Tags with many-to-many relationship to posts
- **Database**: SQLite database (`db.sqlite3`)
- **Migrations**: All migrations are applied and ready

## Running Tests

From the project root directory:

```bash
# Run the test script
uv run python test_server.py
```

This will test all 8 MCP tools:
1. `application_info` - Get Django/Python versions and configuration
2. `get_setting` - Retrieve settings using dot notation
3. `list_models` - List all models with fields
4. `database_schema` - Get complete database schema
5. `list_migrations` - Show migration status
6. `list_management_commands` - List available manage.py commands

## Using the MCP Server with the Test Project

To run the actual MCP server with this test project:

```bash
# From the project root
uv run django-telescope --settings testproject.settings
```

Make sure to add the fixtures/testproject directory to your Python path when using it in production:

```bash
export PYTHONPATH="${PYTHONPATH}:./fixtures/testproject"
uv run django-telescope --settings testproject.settings
```

## Database

The SQLite database is created automatically when you run migrations. To reset it:

```bash
rm fixtures/testproject/db.sqlite3
DJANGO_SETTINGS_MODULE=testproject.settings uv run python fixtures/testproject/manage.py migrate
```

## Models Overview

The blog app demonstrates various Django model features:

- **Foreign Keys**: Post → Author (User), Post → Category
- **Many-to-Many**: Tag ↔ Post
- **Choices**: Post.status (draft/published/archived)
- **Indexes**: On published_at and status fields
- **Auto timestamps**: created_at, updated_at
- **Custom methods**: Post.publish()

This provides a realistic test case for the MCP server's introspection capabilities.
