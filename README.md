# Django AI Boost

<!-- mcp-name: io.github.vintasoftware/django-ai-boost -->

A Model Context Protocol (MCP) server for developing Django applications, inspired by [Laravel Boost](https://github.com/laravel/boost). This server exposes Django project information through MCP tools, enabling AI assistants to better understand and interact with Django codebases.

## Table of Contents

- [Features](#features)
- [Screenshots](#screenshots)
- [Installation](#installation)
  - [For End Users](#for-end-users)
  - [For Development](#for-development)
- [Usage](#usage)
  - [Running the Server](#running-the-server)
  - [Authentication](#authentication)
- [AI Tools Setup](#ai-tools-setup)
  - [Cursor](#cursor)
  - [Claude Desktop](#claude-desktop)
  - [Github Copilot (VS Code)](#github-copilot-vs-code-extension)
  - [Claude Code (VS Code)](#claude-code-vs-code-extension)
  - [OpenAI ChatGPT Desktop](#openai-chatgpt-desktop-with-mcp)
  - [Cline (VS Code)](#cline-vs-code-extension)
  - [Zed Editor](#zed-editor)
  - [Generic MCP Client](#generic-mcp-client)
- [Available Tools](#available-tools-and-prompts)
- [Example Usage](#example-usage-with-ai-assistants)
- [Development & Testing](#development--testing)
- [Troubleshooting](#troubleshooting)
- [Requirements](#requirements)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Project Discovery**: List models, URLs, and management commands
- **Database Introspection**: View schema, migrations, and relationships
- **Configuration Access**: Query Django settings with dot notation
- **Log Reading**: Access recent application logs with filtering
- **Production-Ready Authentication**: Bearer token authentication for secure deployments
- **Read-Only**: All tools are safe, read-only operations
- **Fast**: Built on [FastMCP](https://gofastmcp.com/) for efficient async operations

## Screenshots

<details>
<summary>Click to view screenshots</summary>

### Django AI Boost in Action

![Django AI Boost Example](./assets/example_mcp01.png)

*Django AI Boost MCP server providing Django project introspection through AI assistants (Example using [OpenCode](https://opencode.ai/))*

</details>

## Installation

### For End Users

```bash
# Using uv (recommended)
uv pip install django-ai-boost

# Or with pip
pip install django-ai-boost
```

### For Development

If you want to contribute or run the latest development version:

```bash
# Clone the repository
git clone https://github.com/vinta/django-ai-boost.git
cd django-ai-boost

# Install uv if you haven't already
# On macOS/Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows:
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Install dependencies (creates virtual environment automatically)
uv sync --dev

# Verify installation
uv run django-ai-boost --help
```

## Usage

### Running the Server

The server requires access to your Django project's settings:

```bash
# Set the Django settings module
export DJANGO_SETTINGS_MODULE=myproject.settings
django-ai-boost

# Or specify settings directly
django-ai-boost --settings myproject.settings

# Run with SSE transport (default is stdio, which doesn't use network ports)
django-ai-boost --settings myproject.settings --transport sse

# Run with SSE transport on a custom port (default port is 8000)
django-ai-boost --settings myproject.settings --transport sse --port 3000

# Run with SSE transport on custom host and port
django-ai-boost --settings myproject.settings --transport sse --host 0.0.0.0 --port 8080
```

**Note:** The stdio transport (default) communicates via standard input/output and does not use network ports. The `--port` and `--host` options only apply when using `--transport sse`.

### Authentication

Django AI Boost supports bearer token authentication for secure production deployments when using SSE transport.

#### Quick Start

**Set authentication token (recommended for production):**
```bash
export DJANGO_MCP_AUTH_TOKEN="your-secret-token"
django-ai-boost --settings myproject.settings --transport sse
```

**Or use CLI argument:**
```bash
django-ai-boost --settings myproject.settings --transport sse --auth-token "your-secret-token"
```

#### How It Works

- **Automatic Production Mode**: When Django's `DEBUG=False` and using SSE transport, authentication is **automatically required**
- **Token Precedence**: Environment variable takes precedence over CLI argument for security
- **Transport Support**:
  - ✅ **SSE Transport**: Full authentication support (HTTP-based)
  - ❌ **Stdio Transport**: No authentication (local-only, trusted environments)
- **Error on Mismatch**: If you provide `--auth-token` with `--transport stdio`, the server will exit with an error to prevent false security assumptions

#### Production Deployment

When running in production (DEBUG=False) with SSE transport, you **must** provide an authentication token:

```bash
# This will fail without a token
django-ai-boost --settings myproject.production_settings --transport sse
# Error: Production mode detected but no authentication token provided

# This works
export DJANGO_MCP_AUTH_TOKEN="strong-secret-token"
django-ai-boost --settings myproject.production_settings --transport sse
# Authentication enabled with bearer token for SSE transport
```

#### Security Best Practices

1. **Generate strong tokens**:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Never commit tokens** to version control

3. **Use environment variables** in production (not CLI arguments)

4. **Rotate tokens periodically**

5. **Use HTTPS** with a reverse proxy for external access

#### Client Configuration with Authentication

When using authentication, configure your MCP clients to include the token:

**Cursor / Claude Desktop:**
```json
{
  "mcpServers": {
    "django-ai-boost": {
      "command": "django-ai-boost",
      "args": ["--settings", "myproject.settings", "--transport", "sse"],
      "env": {
        "DJANGO_MCP_AUTH_TOKEN": "your-secret-token",
        "DJANGO_SETTINGS_MODULE": "myproject.settings",
        "PYTHONPATH": "/path/to/your/django/project"
      }
    }
  }
}
```

**Testing with curl:**
```bash
# Without auth - fails
curl http://127.0.0.1:8000/sse

# With correct token - works
curl -H "Authorization: Bearer your-secret-token" http://127.0.0.1:8000/sse
```

#### Troubleshooting Authentication

**"Production mode detected but no authentication token provided"**
- Set `DJANGO_MCP_AUTH_TOKEN` environment variable or use `--auth-token`

**"Authentication token provided but transport is 'stdio'"**
- **This is now an error** that stops the server from starting
- Authentication only works with `--transport sse`
- Either use `--transport sse` with your token, or remove the `--auth-token` argument for stdio

**"Running in production mode with stdio transport"**
- This is OK for local/trusted environments, but stdio has no authentication capability
- For remote access, use `--transport sse` with authentication

## AI Tools Setup

### Cursor

[Cursor](https://cursor.com/) is a popular AI-powered code editor with built-in MCP support.

1. Open Cursor Settings (Cmd/Ctrl + Shift + J)
2. Navigate to the "Tools & MCP" section
3. Add the Django AI Boost server configuration:

```json
{
  "mcpServers": {
    "django-ai-boost": {
      "command": "django-ai-boost",
      "args": ["--settings", "myproject.settings"],
      "env": {
        "DJANGO_SETTINGS_MODULE": "myproject.settings",
        "PYTHONPATH": "/path/to/your/django/project"
      }
    }
  }
}
```

**Note**: Replace `/path/to/your/django/project` with the actual path to your Django project root directory.

For more information, see the [Cursor MCP documentation](https://cursor.com/docs/context/mcp).

### Claude Desktop

Add to your Claude Desktop configuration:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "django": {
      "command": "django-ai-boost",
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


### Github Copilot (VS Code Extension)

1. Install the Github Copilot Chat extension from VS Code marketplace
2. Create or edit `.vscode/mcp.json` in your Django project root:

```json
{
"inputs": [
  // The "inputs" section defines the inputs required for the MCP server configuration.
  {
    "type": "promptString"
  }
],
"servers": {
  // The "servers" section defines the MCP servers you want to use.
  "django-ai-boost": {
    "command": "uv",
    "args": ["run", "django-ai-boost", "--settings", "myproject.settings"],
    "env": {
      "DJANGO_SETTINGS_MODULE": "myproject.settings"
    }
  }
 }
}
```

3. Click "Start" in the JSON
   <img width="1182" height="642" alt="image" src="https://github.com/user-attachments/assets/9a0ea532-80bd-4bd7-bbd2-7d4afd726b32" />

5. Github Copilot Code will automatically connect to the MCP server when you start a conversation in "Agent" mode.

### Claude Code (VS Code Extension)

1. Install the Claude Code extension from VS Code marketplace
2. Create or edit `.mcp.json` in your Django project root:

```json
{
  "mcpServers": {
    "django-ai-boost": {
      "command": "uv",
      "args": ["run", "django-ai-boost", "--settings", "myproject.settings"],
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
      "command": "django-ai-boost",
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
    "command": "django-ai-boost",
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
      "command": "django-ai-boost",
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
# Standard I/O transport (default, no network port)
django-ai-boost --settings myproject.settings

# Server-Sent Events transport (default: 127.0.0.1:8000)
django-ai-boost --settings myproject.settings --transport sse

# SSE transport with custom port
django-ai-boost --settings myproject.settings --transport sse --port 3000

# SSE transport with custom host and port
django-ai-boost --settings myproject.settings --transport sse --host 0.0.0.0 --port 8080
```

## Available Tools and Prompts

### Tools

### 1. `application_info`
Get Django and Python versions, installed apps, middleware, database engine, and debug mode status.

### 2. `get_setting`
Retrieve any Django setting using dot notation (e.g., `DATABASES.default.ENGINE`).

### 3. `list_models`
List all Django models with fields, types, max_length, null/blank status, and relationships.

**Arguments:**
- `app_labels`: Optional list of app labels to filter (e.g., `["blog", "auth"]`). If not provided, returns all models.

**Note**: For large projects, some MCP clients (like PyCharm) may truncate output due to display limits. Use the `app_labels` parameter to filter by specific apps to avoid truncation. See [Troubleshooting](#troubleshooting) for more details.

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

### 10. `query_model`
Query a Django model with read-only operations using the Django ORM manager. This tool allows safe querying of any Django model with filtering, ordering, and pagination.

**Arguments:**
- `app_label`: The Django app label (e.g., "blog")
- `model_name`: The model name (e.g., "Post")
- `filters`: Optional dict of field lookups (e.g., `{"status": "published", "featured": true}`)
- `order_by`: Optional list of fields to order by (e.g., `["-created_at", "title"]`)
- `limit`: Maximum number of results to return (default: 100, max: 1000)

**Returns:**
- Total count of matching objects
- Number of results returned
- List of model instances as dictionaries with all field values
- For foreign keys, includes both the ID and string representation

**Example Queries:**
- Get all published posts: `filters={"status": "published"}`
- Get featured posts ordered by date: `filters={"featured": true}`, `order_by=["-created_at"]`
- Get recent posts with limit: `order_by=["-created_at"]`, `limit=10`

### 11. `read_recent_logs`
Read recent log entries with optional filtering by log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).

### Prompts

MCP prompts provide reusable message templates to help guide interactions with AI assistants.

### 1. `search_django_docs`
Generate a formatted prompt to help search for specific topics in Django documentation.

**Arguments:**
- `topic`: The Django topic or feature to search for (e.g., "models", "queryset", "migrations", "authentication")

**Returns:**
A formatted prompt that includes:
- The current Django version being used
- Direct links to the appropriate version of Django documentation
- Guidance on what information to look for
- Request for best practices and code examples

**Example topics:**
- "models" - Learn about Django models and ORM
- "queryset filtering" - Query optimization and filtering
- "migrations" - Database schema management
- "authentication" - User authentication and permissions
- "middleware" - Request/response processing
- "forms" - Form handling and validation

This prompt automatically adapts to your Django version (e.g., 5.2, 4.2) to ensure documentation compatibility.

## Example Usage with AI Assistants

Once configured, you can ask your AI assistant questions like:

**Using Tools:**
- "What models are in this Django project?"
- "Show me all URL patterns"
- "What's the database schema for the users table?"
- "Are there any unapplied migrations?"
- "What's the value of the DEBUG setting?"
- "What's the URL for blog post with ID 5?"
- "Reverse the 'post_detail' URL pattern with pk=10"
- "Show me all published blog posts"
- "Get the 10 most recent posts ordered by creation date"
- "Find all featured posts in the blog"
- "Show me recent error logs"

**Using Prompts:**
- "Use the search_django_docs prompt for 'models'" - Get help finding Django model documentation
- "Search Django docs for 'authentication'" - Learn about Django authentication
- "Show me Django documentation about 'migrations'" - Migration best practices and guides

## Development & Testing

The project includes a comprehensive test suite and a fixture Django project for development:

```bash
# Test the MCP server with the fixture project
uv run python test_server.py

# Test the query_model tool
uv run python test_query_model.py

# Run the MCP server with the test project
export PYTHONPATH="${PYTHONPATH}:./fixtures/testproject"
uv run django-ai-boost --settings testproject.settings

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
django-ai-boost
```

### PYTHONPATH Issues

If Django can't find your project modules, add your project directory to PYTHONPATH:

```bash
export PYTHONPATH="${PYTHONPATH}:/path/to/your/project"
django-ai-boost --settings myproject.settings
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

1. Check that the `django-ai-boost` command is accessible in your PATH
2. Verify your MCP client configuration file syntax is valid JSON
3. Check the logs in your AI tool (usually in settings or help menu)
4. Try running the server manually to see any error messages:
   ```bash
   django-ai-boost --settings myproject.settings
   ```

### Database Connection Issues

Ensure your Django database is properly configured and accessible. The MCP server needs the same database access as your Django application.

### Port Already in Use (SSE Transport)

If you see an error like "Address already in use" when using SSE transport, the default port 8000 is likely occupied by another service (such as your Django development server). Use a different port:

```bash
# Use a different port for the MCP server
django-ai-boost --settings myproject.settings --transport sse --port 8001
```

**Note:** The stdio transport (default) does not use network ports and will not have this issue.

### Output Truncation in MCP Clients

Some MCP clients have display limits that may truncate long tool outputs:

**PyCharm**: Limits tool output to 2000 lines (~100 Django models with typical field counts)
**Claude Code**: Truncates at ~700 characters in terminal display

**Symptoms:**
- Message stating "output truncated due to length"
- Incomplete model listings when calling `list_models`

**Solution:**
Use the `app_labels` parameter to filter models by specific Django apps:

```python
# Instead of listing all models (may truncate):
list_models()

# Filter by specific app(s):
list_models(app_labels=["blog"])
list_models(app_labels=["blog", "auth", "contenttypes"])
```

**Verification:**
The truncation is happening client-side, not in the server. To verify:
1. Count your Django models: `python manage.py shell -c "from django.apps import apps; print(len(apps.get_models()))"`
2. Estimate lines: models × 20 lines per model ≈ total output lines
3. If > 2000 lines (PyCharm) or very large (Claude Code), use app filtering


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
   git clone https://github.com/YOUR_USERNAME/django-ai-boost.git
   cd django-ai-boost
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
   uv run django-ai-boost --settings testproject.settings
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

## Commercial Support

[![alt text](https://avatars2.githubusercontent.com/u/5529080?s=80&v=4 "Vinta Logo")](https://www.vinta.com.br/)

This project is maintained by [Vinta Software](https://www.vinta.com.br/). Our team of design and development experts is available to help your company launch successful Django-powered products. If you need any commercial support, feel free to get in touch: contact@vinta.com.br
