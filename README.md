# Django Telescope

A Model Context Protocol (MCP) server for Django applications, inspired by [Laravel Boost](https://github.com/laravel/boost). This server exposes Django project information through MCP tools, enabling AI assistants to better understand and interact with Django codebases.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
  - [For End Users](#for-end-users)
  - [For Development](#for-development)
- [Usage](#usage)
- [AI Tools Setup](#ai-tools-setup)
  - [Claude Desktop](#claude-desktop)
  - [Claude Code (VS Code)](#claude-code-vs-code-extension)
  - [OpenAI ChatGPT Desktop](#openai-chatgpt-desktop-with-mcp)
  - [Cline (VS Code)](#cline-vs-code-extension)
  - [Zed Editor](#zed-editor)
  - [Generic MCP Client](#generic-mcp-client)
- [Available Tools](#available-tools)
- [Example Usage](#example-usage-with-ai-assistants)
- [Development & Testing](#development--testing)
- [Troubleshooting](#troubleshooting)
- [Requirements](#requirements)
- [Contributing](#contributing)
- [License](#license)

## Features

 **Project Discovery**: List models, URLs, and management commands
- **Database Introspection**: View schema, migrations, and relationships
- **Configuration Access**: Query Django settings with dot notation
- **Log Reading**: Access recent application logs with filtering
- **Read-Only**: All tools are safe, read-only operations
- **Fast**: Built on [FastMCP](https://gofastmcp.com/) for efficient async operations

## Installation

### For End Users

```bash
# Using uv (recommended)
uv pip install django-telescope

# Or with pip
pip install django-telescope
```

### For Development

If you want to contribute or run the latest development version:

```bash
# Clone the repository
git clone https://github.com/vinta/django-telescope.git
cd django-telescope

# Install uv if you haven't already
# On macOS/Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows:
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Install dependencies (creates virtual environment automatically)
uv sync --dev

# Verify installation
uv run django-telescope --help
```

## Usage

### Running the Server

The server requires access to your Django project's settings:

```bash
# Set the Django settings module
export DJANGO_SETTINGS_MODULE=myproject.settings
django-telescope

# Or specify settings directly
django-telescope --settings myproject.settings

# Run with SSE transport (default is stdio)
django-telescope --settings myproject.settings --transport sse
```

## AI Tools Setup

### Claude Desktop

Add to your Claude Desktop configuration:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "django": {
      "command": "django-telescope",
      "args": ["--settings", "myproject.settings"],
      "env": {
        "DJANGO_SETTINGS_MODULE": "myproject.settings",
        "PYTHONPATH": "/path/to/your/django/project"
      }
    }
  }
}
```

**Note**: Make sure to replace `/path/to/your/django/project` with the actual path to your Django project root directory.

### Claude Code (VS Code Extension)

1. Install the Claude Code extension from VS Code marketplace
2. Create or edit `.mcp.json` in your Django project root:

```json
{
  "mcpServers": {
    "django-telescope": {
      "command": "uv",
      "args": ["run", "django-telescope", "--settings", "myproject.settings"],
      "env": {
        "DJANGO_SETTINGS_MODULE": "myproject.settings"
      }
    }
  }
}
```

3. Restart VS Code or reload the Claude Code extension
4. Claude Code will automatically connect to the MCP server when you start a conversation

### OpenAI ChatGPT Desktop with MCP

OpenAI ChatGPT Desktop supports MCP servers. Add to your configuration file:
- **macOS**: `~/Library/Application Support/OpenAI/ChatGPT/config.json`
- **Windows**: `%APPDATA%\OpenAI\ChatGPT\config.json`

```json
{
  "mcpServers": {
    "django": {
      "command": "django-telescope",
      "args": ["--settings", "myproject.settings"],
      "env": {
        "DJANGO_SETTINGS_MODULE": "myproject.settings"
      }
    }
  }
}
```

### Cline (VS Code Extension)

1. Install the Cline extension from VS Code marketplace
2. Open Cline settings (Cmd/Ctrl + Shift + P → "Cline: Open Settings")
3. Add MCP server configuration in the MCP Servers section:

```json
{
  "django": {
    "command": "django-telescope",
    "args": ["--settings", "myproject.settings"],
    "env": {
      "DJANGO_SETTINGS_MODULE": "myproject.settings"
    }
  }
}
```

### Zed Editor

Add to your Zed MCP configuration (`~/.config/zed/mcp.json`):

```json
{
  "servers": {
    "django": {
      "command": "django-telescope",
      "args": ["--settings", "myproject.settings"],
      "env": {
        "DJANGO_SETTINGS_MODULE": "myproject.settings"
      }
    }
  }
}
```

### Generic MCP Client

For any MCP-compatible client, you can run the server manually:

```bash
# Standard I/O transport (default)
django-telescope --settings myproject.settings

# Server-Sent Events transport
django-telescope --settings myproject.settings --transport sse
```

## Available Tools

### 1. `application_info`
Get Django and Python versions, installed apps, middleware, database engine, and debug mode status.

### 2. `get_setting`
Retrieve any Django setting using dot notation (e.g., `DATABASES.default.ENGINE`).

### 3. `list_models`
List all Django models with fields, types, max_length, null/blank status, and relationships.

### 4. `list_urls`
Show all URL patterns with names, patterns, and view handlers (including nested includes).

### 5. `database_schema`
Get complete database schema including tables, columns, types, indexes, and foreign keys.

### 6. `list_migrations`
View all migrations per app with their applied/unapplied status.

### 7. `list_management_commands`
List all available `manage.py` commands with their source apps.

### 8. `get_absolute_url`
Get the absolute URL for a specific model instance. Requires the model to have a `get_absolute_url()` method defined.

**Arguments:**
- `app_label`: The Django app label (e.g., "blog")
- `model_name`: The model name (e.g., "Post")
- `pk`: The primary key of the instance

### 9. `reverse_url`
Reverse a named URL pattern to get its actual URL path. Supports both positional args and keyword arguments.

**Arguments:**
- `url_name`: The URL pattern name (e.g., "post_detail", "admin:index")
- `args`: Optional list of positional arguments
- `kwargs`: Optional dict of keyword arguments

### 10. `read_recent_logs`
Read recent log entries with optional filtering by log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).

## Example Usage with AI Assistants

Once configured, you can ask your AI assistant questions like:

- "What models are in this Django project?"
- "Show me all URL patterns"
- "What's the database schema for the users table?"
- "Are there any unapplied migrations?"
- "What's the value of the DEBUG setting?"
- "What's the URL for blog post with ID 5?"
- "Reverse the 'post_detail' URL pattern with pk=10"
- "Show me recent error logs"

## Development & Testing

The project includes a comprehensive test suite and a fixture Django project for development:

```bash
# Test the MCP server with the fixture project
uv run python test_server.py

# Run the MCP server with the test project
export PYTHONPATH="${PYTHONPATH}:./fixtures/testproject"
uv run django-telescope --settings testproject.settings

# Run linter
uv run ruff check .

# Auto-fix linting issues
uv run ruff check --fix .

# Format code
uv run ruff format .
```

The [fixtures/testproject/](fixtures/testproject/) directory contains a complete Django application for testing all MCP tools. See [fixtures/README.md](fixtures/README.md) for details about the test project structure.

## Troubleshooting

### "Django is not configured" Error

Make sure you've set the `DJANGO_SETTINGS_MODULE` environment variable or used the `--settings` flag:

```bash
export DJANGO_SETTINGS_MODULE=myproject.settings
django-telescope
```

### PYTHONPATH Issues

If Django can't find your project modules, add your project directory to PYTHONPATH:

```bash
export PYTHONPATH="${PYTHONPATH}:/path/to/your/project"
django-telescope --settings myproject.settings
```

Or in your MCP client configuration:

```json
{
  "env": {
    "PYTHONPATH": "/path/to/your/project",
    "DJANGO_SETTINGS_MODULE": "myproject.settings"
  }
}
```

### MCP Server Not Connecting

1. Check that the `django-telescope` command is accessible in your PATH
2. Verify your MCP client configuration file syntax is valid JSON
3. Check the logs in your AI tool (usually in settings or help menu)
4. Try running the server manually to see any error messages:
   ```bash
   django-telescope --settings myproject.settings
   ```

### Database Connection Issues

Ensure your Django database is properly configured and accessible. The MCP server needs the same database access as your Django application.

## Requirements

- Python 3.12+
- Django 4.2+
- FastMCP 2.12.4+

## License

MIT License - see LICENSE file for details.

## Inspiration

This project is inspired by [Laravel Boost](https://github.com/laravel/boost), which provides similar MCP functionality for Laravel applications.

## Contributing

We welcome contributions from the community! Whether it's bug fixes, new features, documentation improvements, or bug reports, your help is appreciated.

### Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/django-telescope.git
   cd django-telescope
   ```
3. **Install development dependencies**:
   ```bash
   uv sync --dev
   ```
4. **Create a new branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

### Development Workflow

1. **Make your changes** in your feature branch
2. **Follow code style**:
   ```bash
   # Check code style
   uv run ruff check .

   # Auto-fix style issues
   uv run ruff check --fix .

   # Format code
   uv run ruff format .
   ```
3. **Test your changes**:
   ```bash
   # Run the test suite
   uv run python test_server.py

   # Test with the fixture project
   export PYTHONPATH="${PYTHONPATH}:./fixtures/testproject"
   uv run django-telescope --settings testproject.settings
   ```
4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add new feature" # or "fix: resolve bug"
   ```

   We follow [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat:` for new features
   - `fix:` for bug fixes
   - `docs:` for documentation changes
   - `chore:` for maintenance tasks
   - `test:` for test changes
   - `refactor:` for code refactoring

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```
6. **Create a Pull Request** on GitHub from your fork to the main repository

### Contribution Guidelines

- **Code Quality**: Ensure your code passes linting (`ruff check`) and formatting (`ruff format`)
- **Testing**: Add tests for new features and ensure existing tests pass
- **Documentation**: Update the README and relevant documentation for new features
- **Commits**: Use clear, descriptive commit messages following Conventional Commits
- **Pull Requests**: Provide a clear description of what your PR does and why
- **Issues**: Check existing issues before creating a new one

### What to Contribute

We're especially interested in:

- **New MCP Tools**: Add new tools to expose more Django functionality
- **Bug Fixes**: Fix issues reported in GitHub Issues
- **Documentation**: Improve setup guides, add examples, or clarify existing docs
- **Tests**: Expand test coverage for existing features
- **Performance**: Optimize slow operations or reduce memory usage
- **Compatibility**: Ensure compatibility with different Django versions

### Need Help?

- Look at existing code for examples
- Open a GitHub Issue for questions or discussions
- Review closed PRs to see how others have contributed

### Code of Conduct

Please be respectful and constructive in all interactions. We aim to maintain a welcoming and inclusive community.
