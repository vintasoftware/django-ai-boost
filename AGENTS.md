# AGENTS.md
Guidance for coding agents working in `django-ai-boost`.
## 1) Project Snapshot
- Python package: `django-ai-boost`
- Purpose: MCP server exposing read-only Django introspection tools
- Runtime: Python `>=3.12`
- Core deps: `django>=4.2`, `fastmcp>=2.14.5`
- Package manager: `uv`
- Entry point: `django-ai-boost` -> `django_ai_boost:main`
- Main server module: `src/django_ai_boost/server_fastmcp.py`
## 2) Environment Setup
- Install runtime deps:
  - `uv sync`
- Install dev deps:
  - `uv sync --dev`
- Verify CLI:
  - `uv run django-ai-boost --help`
## 3) Build / Lint / Format Commands
- Lint all Python files:
  - `uv run ruff check .`
- Auto-fix lint issues:
  - `uv run ruff check --fix .`
- Format code:
  - `uv run ruff format .`
Notes:
- There is no separate compile/build step for this repository.
- `ruff` is the formatter and linter source of truth.
## 4) Test Commands
Primary test scripts used in this repo:
- Run broad integration script:
  - `uv run python test_server.py`
- Run query-model tests:
  - `uv run python test_query_model.py`
- Run system-check tests:
  - `uv run python test_run_check.py`
- Run auth logic tests:
  - `uv run python test_auth_logic.py`
- Run prompt-related test script:
  - `uv run python test_prompt.py`
Pytest is also available:
- Run all pytest tests:
  - `uv run pytest`
- Verbose pytest:
  - `uv run pytest -v`
### Running a single test (important)
Use one of these patterns:
- Single pytest file:
  - `uv run pytest test_auth_logic.py`
- Single pytest test function:
  - `uv run pytest test_auth_logic.py::test_validation_logic`
- Filter by test name substring:
  - `uv run pytest -k validation_logic`
- Single script-style test file (non-pytest harness):
  - `uv run python test_query_model.py`
## 5) Running the Server Locally
With env var:
- `export DJANGO_SETTINGS_MODULE=myproject.settings`
- `uv run django-ai-boost`
With explicit settings arg:
- `uv run django-ai-boost --settings myproject.settings`
SSE transport:
- `uv run django-ai-boost --settings myproject.settings --transport sse`
- `uv run django-ai-boost --settings myproject.settings --transport sse --host 127.0.0.1 --port 8000`
Fixture project quick run:
- `export PYTHONPATH="${PYTHONPATH}:./fixtures/testproject"`
- `uv run django-ai-boost --settings testproject.settings`
## 6) Authentication and Safety Rules
- Token env var: `DJANGO_MCP_AUTH_TOKEN`
- Token precedence: env var > `--auth-token`
- Auth tokens are only valid with `--transport sse`
- `DEBUG=False` + SSE requires a token; startup should fail otherwise
- `DEBUG=False` + stdio is allowed but intentionally unauthenticated
- Never log or expose raw token values
## 7) Code Style and Conventions
### Formatting and imports
- Follow `ruff check` + `ruff format` outputs exactly.
- Keep imports grouped and ordered:
  - stdlib
  - third-party
  - local package imports
- Prefer explicit imports over wildcard imports.
- Keep one import per line when practical.
### Typing
- Use Python 3.12+ type syntax:
  - `str | None`, `list[str]`, `dict[str, Any]`
- Keep type hints on all public functions.
- Use `Any` only when unavoidable for dynamic payloads.
- Return JSON-serializable structures from MCP tools.
### Naming
- Functions/variables: `snake_case`
- Constants: `UPPER_CASE`
- Modules: `snake_case`
- Use clear action-oriented function names (`list_models`, `run_check`).
### Async and Django ORM patterns
- MCP tool handlers are `async def`.
- Wrap blocking ORM/db work with `sync_to_async`.
- Keep synchronous DB operations inside small inner helper functions.
- Avoid blocking work directly in async handlers.
### Error handling
- For tool operations, prefer graceful error payloads:
  - `{"error": "..."}`
- Raise exceptions only for startup/config validation failures where aborting is correct.
- Keep error messages actionable and specific.
- Catch narrow exceptions when possible (`LookupError`, `NoReverseMatch`), then fallback to generic handling.
### Tool behavior constraints
- Preserve read-only behavior for introspection tools.
- Do not add mutating database operations to current tools without explicit product direction.
- Keep limits/guardrails (for example query limits) to prevent heavy operations.
### Docs and comments
- Keep docstrings for public tools and CLI-facing functions.
- Add comments only for non-obvious logic.
- Prefer concise, direct wording in docs and errors.
## 8) File/Module-Specific Guidance
- `src/django_ai_boost/__init__.py`
  - CLI arg parsing and delegation to `run_server`.
- `src/django_ai_boost/server_fastmcp.py`
  - Django initialization
  - auth validation
  - tool and prompt registration
  - server startup by transport
- Keep tool registration centralized via `TOOLS` and `PROMPTS` lists.
## 9) Cursor/Copilot Rule Files
Checked in this repository:
- `.cursor/rules/`: not found
- `.cursorrules`: not found
- `.github/copilot-instructions.md`: not found
If these files are added later, treat them as higher-priority agent instructions and merge them into this guide.
## 10) Practical Workflow for Agents
1. Sync deps with `uv sync --dev`.
2. Make focused code changes.
3. Run `uv run ruff check .` and `uv run ruff format .`.
4. Run the most relevant test file first (single-test pattern above).
5. Run broader tests before finalizing.
6. Ensure behavior remains read-only unless explicitly requested otherwise.

## 11) Agent Guardrails

- Make minimal, targeted changes and avoid unrelated refactors.
- Do not change public behavior unless the task requires it.
- Preserve CLI flags, tool names, and prompt names for compatibility.
- Keep startup validation strict and fail early on misconfiguration.
- Prefer adding tests near the behavior being changed.
- When updating tests, keep fixtures deterministic and explicit.
- Avoid introducing global state when function-local state is enough.
- Keep return payload shapes stable for MCP clients.
- Do not swallow exceptions silently; return actionable context.
- Validate user-provided limits and keep hard caps in place.
- Prefer clarity over cleverness in async and ORM code.
- Update this file if repository workflows or conventions change.
