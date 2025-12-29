from django_ai_boost.server_fastmcp import run_server


def main() -> None:
    """Entry point for the django-ai-boost CLI."""
    import argparse

    parser = argparse.ArgumentParser(description="Django AI Boost Server")
    parser.add_argument(
        "--settings",
        help="Django settings module (e.g., myproject.settings)",
        default=None,
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="Transport type (default: stdio)",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind to for SSE transport (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to for SSE transport (default: 8000)",
    )
    parser.add_argument(
        "--auth-token",
        default=None,
        help="Bearer token for authentication (can also use DJANGO_MCP_AUTH_TOKEN env var). "
             "Required in production (DEBUG=False) when using SSE transport.",
    )

    args = parser.parse_args()

    run_server(
        settings_module=args.settings,
        transport=args.transport,
        host=args.host,
        port=args.port,
        auth_token=args.auth_token,
    )
