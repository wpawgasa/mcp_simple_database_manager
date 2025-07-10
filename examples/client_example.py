#!/usr/bin/env python3
"""
Example MCP client for the MCP Simple DB Access Server.

This script demonstrates how to connect to and interact with the MCP server
using various tools for database operations and LLM integration.
"""

from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters
import asyncio
import json
import sys
from pathlib import Path

from utilities import extract_text_content

# Add the src directory to the path so we can import the MCP SDK
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


async def run_example_client():
    """Main function to demonstrate MCP client interactions."""

    # Server parameters - adjust path as needed
    server_params = StdioServerParameters(
        command="python", args=[str(Path(__file__).parent.parent / "run_server.py")], env=None
    )

    print("🚀 Starting MCP Simple DB Access Client Example")
    print("=" * 50)

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()

            print("✅ Connected to MCP Server")
            print()

            # List available tools
            print("📋 Available Tools:")
            tools = await session.list_tools()
            for i, tool in enumerate(tools.tools, 1):
                print(f"  {i}. {tool.name} - {tool.description}")
            print()

            # Example 1: Insert sample data
            print("📝 Example 1: Inserting sample data...")
            result = await session.call_tool("insert_sample_data", {})
            print(f"   {extract_text_content(result)}")
            # Example 2: Query database schema
            print("🗂️  Example 2: Getting database schema...")
            result = await session.call_tool("get_database_schema", {})
            result_text = extract_text_content(result)
            schema = json.loads(result_text)
            print("   Database Schema:")
            for table, info in schema.items():
                print(f"     📊 Table: {table} ({info['row_count']} rows)")
                for col in info["columns"]:
                    print(f"        - {col['name']}: {col['type']}")

            # Example 3: Basic database query
            print("🔍 Example 3: Querying users table...")
            result = await session.call_tool("query_database", {"sql": "SELECT * FROM users LIMIT 3"})
            users = json.loads(extract_text_content(result))
            print("   Users:")
            for user in users:
                print(
                    f"     👤 {user['name']} ({user['email']}) - Age: {user['age']}")

            # Example 4: List Ollama models
            print("🤖 Example 4: Listing available Ollama models...")
            result = await session.call_tool("list_ollama_models", {})
            print(f"   {extract_text_content(result)}")

            # Example 5: Chat with Ollama
            print("💬 Example 5: Chatting with Ollama...")
            result = await session.call_tool(
                "chat_with_ollama", {
                    "prompt": "Explain what a database is in one sentence.", "model": "llama3.2"}
            )
            print(f"   🤖 Ollama: {extract_text_content(result)}")

            # Example 6: Generate SQL with LlamaIndex
            print("🔧 Example 6: Generating SQL with LlamaIndex...")
            result = await session.call_tool(
                "generate_sql_with_llamaindex",
                {"description": "Find all users older than 25 years",
                    "model": "llama3.2"},
            )
            print(f"   {extract_text_content(result)}")

            # Example 7: Analyze data with LlamaIndex
            print("📊 Example 7: Analyzing data with LlamaIndex...")
            result = await session.call_tool(
                "analyze_database_with_llamaindex",
                {"question": "What insights can you provide about the users in the database?",
                    "model": "llama3.2"},
            )
            print(f"   📈 Analysis: {extract_text_content(result)}")

            # Example 8: Chat with context
            print("🧠 Example 8: Chat with context...")
            try:
                result = await session.call_tool(
                    "chat_with_context",
                    {
                        "message": "How many tables are in the database?",
                        "context": "You are analyzing a SQLite database with user, product, and order tables.",
                        "model": "llama3.2",
                    },
                )
                print(f"   🤖 Response: {extract_text_content(result)}")
            except Exception as e:
                print(f"   Error: {e}")
            print()

            print("🎉 Example client session completed successfully!")


async def interactive_client():
    """Interactive client for manual testing."""

    server_params = StdioServerParameters(
        command="python", args=[str(Path(__file__).parent.parent / "run_server.py")], env=None
    )

    print("🔧 Interactive MCP Client")
    print("Type 'help' for available commands, 'quit' to exit")
    print("=" * 40)

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()

            print("✅ Connected to Interactive MCP Server")
            print()

            # List available tools for reference
            tools = await session.list_tools()
            print("Available commands:")
            print("  help - Show this help message")
            print("  tools - List available MCP tools")
            print("  sample - Insert sample data")
            print("  schema - Show database schema")
            print("  users - Show all users")
            print("  models - List Ollama models")
            print("  chat <message> - Chat with Ollama")
            print("  sql <query> - Execute SELECT query")
            print("  quit - Exit the client")
            print()

            while True:
                try:
                    command = input("🔧 > ").strip()

                    if command in ["quit", "exit"]:
                        break
                    elif command == "help":
                        print("Available commands:")
                        print("  help - Show this help message")
                        print("  tools - List available MCP tools")
                        print("  sample - Insert sample data")
                        print("  schema - Show database schema")
                        print("  users - Show all users")
                        print("  models - List Ollama models")
                        print("  chat <message> - Chat with Ollama")
                        print("  sql <query> - Execute SELECT query")
                        print("  quit - Exit the client")
                    elif command == "tools":
                        print("📋 Available MCP Tools:")
                        for i, tool in enumerate(tools.tools, 1):
                            print(f"  {i}. {tool.name} - {tool.description}")
                    elif command == "sample":
                        result = await session.call_tool("insert_sample_data", {})
                        print(f"✅ {extract_text_content(result)}")
                    elif command == "schema":
                        result = await session.call_tool("get_database_schema", {})
                        print(json.dumps(json.loads(
                            extract_text_content(result)), indent=2))
                    elif command == "users":
                        result = await session.call_tool("query_database", {"sql": "SELECT * FROM users"})
                        print(json.dumps(json.loads(
                            extract_text_content(result)), indent=2))
                    elif command == "models":
                        result = await session.call_tool("list_ollama_models", {})
                        print(extract_text_content(result))
                    elif command.startswith("chat "):
                        message = command[5:]
                        result = await session.call_tool("chat_with_ollama", {"prompt": message, "model": "llama3.2"})
                        print(f"🤖 {extract_text_content(result)}")
                    elif command.startswith("sql "):
                        query = command[4:]
                        if query.strip().upper().startswith("SELECT"):
                            result = await session.call_tool("query_database", {"sql": query})
                            print(json.dumps(json.loads(
                                extract_text_content(result)), indent=2))
                        else:
                            print("❌ Only SELECT queries are allowed for safety")
                    else:
                        print(
                            "❓ Unknown command. Type 'help' for available commands.")

                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"❌ Error: {e}")

            print("\n👋 Goodbye!")


async def main():
    """Main entry point with mode selection."""
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        await interactive_client()
    else:
        await run_example_client()


if __name__ == "__main__":
    asyncio.run(main())
