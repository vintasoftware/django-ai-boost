#!/usr/bin/env python
"""
Test the search_django_docs prompt.

Note: FastMCP prompts are designed to be called by MCP clients, not directly in Python.
This test demonstrates the prompt is properly registered and shows what it would return.
"""
import asyncio
import os
import sys

# Add fixtures project to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "fixtures", "testproject"))

# Set Django settings
os.environ["DJANGO_SETTINGS_MODULE"] = "testproject.settings"

# Import Django and setup
import django

django.setup()

# Import the server and inspect the prompt
from django_ai_boost.server_fastmcp import mcp


async def test_search_django_docs_prompt():
    """Test that the search_django_docs prompt is registered and callable."""
    print("Testing search_django_docs prompt registration...\n")
    print("=" * 80)

    # List all registered prompts
    prompts = await mcp._list_prompts()
    print(f"Found {len(prompts)} registered prompt(s):\n")

    for prompt in prompts:
        print(f"✓ Prompt: {prompt.name}")
        print(f"  Description: {prompt.description}")
        print(f"  Arguments: {[arg.name for arg in prompt.arguments]}")
        print()

    # Check if our prompt is registered
    prompt_names = [p.name for p in prompts]
    if "search_django_docs" in prompt_names:
        print("✓ search_django_docs prompt is registered successfully!")
        print()
        print("To use this prompt, connect an MCP client and call:")
        print('  mcp.get_prompt("search_django_docs", arguments={"topic": "models"})')
        print()
        print("=" * 80)
        print("\nExample usage in MCP Inspector or Claude Desktop:\n")
        print("1. Configure the MCP server in your client")
        print("2. Use the prompt with a topic, e.g., 'models', 'queryset', etc.")
        print("3. The prompt will generate a formatted request to search Django docs")
        print("=" * 80)
    else:
        print("✗ search_django_docs prompt not found!")

    # Demonstrate what the prompt function would return for a sample topic
    print("\nSample output for topic='models':")
    print("-" * 80)
    # Access the underlying function through the prompt
    from django_ai_boost.server_fastmcp import search_django_docs

    # Get the underlying function
    result = await search_django_docs.fn("models")
    print(result)
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_search_django_docs_prompt())
