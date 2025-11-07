from django_telescope.server_fastmcp import run_server


def main() -> None:
    """Entry point for the django-telescope CLI."""
    import argparse

    parser = argparse.ArgumentParser(description="Django Telescope Server")
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

    args = parser.parse_args()

    run_server(settings_module=args.settings, transport=args.transport)
