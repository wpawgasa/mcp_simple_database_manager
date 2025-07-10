#!/usr/bin/env python3
"""
Simple MCP client example for basic database operations.

This is a minimal example showing how to connect to the MCP server
and perform basic database operations.
"""

import asyncio
import json
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from utilities import extract_text_content


async def simple_example():
    """Simple example demonstrating basic MCP operations."""

    # Configure server connection
    server_params = StdioServerParameters(
        command="python",
        args=[str(Path(__file__).parent.parent / "run_server.py")],
    )

    print("Connecting to MCP Server...")

    # Connect to the server
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize connection
            await session.initialize()
            print("Connected!")

            # Insert sample data
            print("\n1. Inserting sample data...")
            result = await session.call_tool("insert_sample_data", {})
            print(f"   {extract_text_content(result)}")

            # Query the database
            print("\n2. Querying users...")
            result = await session.call_tool("query_database", {"sql": "SELECT name, email FROM users LIMIT 2"})
            users_text = extract_text_content(result)
            if users_text != "No text content available":
                users = json.loads(users_text)
                for user in users:
                    print(f"   - {user['name']} ({user['email']})")

            # Get database schema
            print("\n3. Getting database schema...")
            result = await session.call_tool("get_database_schema", {})
            schema_text = extract_text_content(result)
            if schema_text != "No text content available":
                schema = json.loads(schema_text)
                print(f"   Found {len(schema)} tables: {', '.join(schema.keys())}")

            # Try chatting with Ollama (if available)
            print("\n4. Testing Ollama integration...")
            try:
                result = await session.call_tool(
                    "chat_with_ollama", {"prompt": "Hello! Can you tell me what MCP stands for?", "model": "llama3.2"}
                )
                print(f"   Ollama says: {extract_text_content(result)}")
            except Exception as e:
                print(f"   Ollama not available: {e}")

            print("\n✅ Simple example completed!")


if __name__ == "__main__":
    asyncio.run(simple_example())
