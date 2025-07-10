#!/usr/bin/env python3
"""
Advanced MCP client example demonstrating LlamaIndex integration.

This example shows how to use the advanced AI-powered features
of the MCP server for data analysis and SQL generation.
"""

import asyncio
import json
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import CallToolResult, TextContent

from utilities import extract_text_content


async def llamaindex_example():
    """Advanced example demonstrating LlamaIndex features."""

    server_params = StdioServerParameters(
        command="python",
        args=[str(Path(__file__).parent.parent / "run_server.py")],
    )

    print("🧠 Advanced MCP Client - LlamaIndex Features")
    print("=" * 50)

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("✅ Connected to MCP Server with LlamaIndex support")

            # Ensure we have sample data
            print("\n📝 Setting up sample data...")
            result = await session.call_tool("insert_sample_data", {})
            if result.content and isinstance(result.content[0], TextContent):
                print(f"   {extract_text_content(result)}")

            # Add more sample data for better analysis
            print("\n📊 Adding additional sample data...")
            try:
                # Add more products
                await session.call_tool(
                    "query_database",
                    {
                        "sql": """INSERT INTO products (name, price, category, stock_quantity) 
                             VALUES ('Smartphone', 599.99, 'Electronics', 25)"""
                    },
                )
                await session.call_tool(
                    "query_database",
                    {
                        "sql": """INSERT INTO products (name, price, category, stock_quantity) 
                             VALUES ('Book', 19.99, 'Education', 100)"""
                    },
                )
                print("   ✅ Additional products added")
            except Exception as e:
                print(f"   ℹ️  Sample data might already exist: {e}")

            # Example 1: Natural Language SQL Generation
            print("\n🔧 Example 1: Natural Language to SQL Generation")
            questions = [
                "Show me all products with their prices",
                "Find users who are older than 25",
                "Get the total number of products in each category",
            ]

            for question in questions:
                print(f"\n   Question: '{question}'")
                try:
                    result = await session.call_tool(
                        "generate_sql_with_llamaindex", {
                            "description": question, "model": "llama3.2"}
                    )
                    print(f"   Generated SQL: {extract_text_content(result)}")
                except Exception as e:
                    print(f"   Error: {e}")

            # Example 2: Comprehensive Database Analysis
            print("\n\n📈 Example 2: Comprehensive Database Analysis")
            analysis_questions = [
                "What patterns do you see in the user data?",
                "Analyze the product inventory and pricing",
                "What insights can you provide about the database structure?",
            ]

            for question in analysis_questions:
                print(f"\n   Analyzing: '{question}'")
                try:
                    result = await session.call_tool(
                        "analyze_database_with_llamaindex", {
                            "question": question, "model": "llama3.2"}
                    )
                    print(f"   Analysis:\n   {extract_text_content(result)}")
                    print("   " + "-" * 40)
                except Exception as e:
                    print(f"   Error: {e}")

            # Example 3: Context-Aware Conversations
            print("\n\n💬 Example 3: Context-Aware Conversations")

            # Get current database state for context
            schema_result = await session.call_tool("get_database_schema", {})
            schema = json.loads(extract_text_content(schema_result))

            context = f"""
            Database Context:
            - Tables: {', '.join(schema.keys())}
            - Total tables: {len(schema)}
            - Users table has {schema.get('users', {}).get('row_count', 0)} records
            - Products table has {schema.get('products', {}).get('row_count', 0)} records
            """

            conversations = [
                "How many tables are in this database?",
                "What would be a good query to find popular products?",
                "Can you suggest some analytics we could run on this data?",
            ]

            for message in conversations:
                print(f"\n   User: {message}")
                try:
                    result = await session.call_tool(
                        "chat_with_context", {
                            "message": message, "context": context, "model": "llama3.2"}
                    )
                    print(f"   AI: {extract_text_content(result)}")
                except Exception as e:
                    print(f"   Error: {e}")

            # Example 4: Data-Driven Insights
            print("\n\n🔍 Example 4: Generating Data-Driven Insights")

            # First, get some actual data
            users_result = await session.call_tool(
                "query_database", {
                    "sql": "SELECT COUNT(*) as total_users, AVG(age) as avg_age FROM users"}
            )
            products_result = await session.call_tool(
                "query_database", {
                    "sql": "SELECT COUNT(*) as total_products, AVG(price) as avg_price FROM products"}
            )

            users_stats = json.loads(extract_text_content(users_result))[0]
            products_stats = json.loads(
                extract_text_content(products_result))[0]

            data_context = f"""
            Current Database Statistics:
            - Total Users: {users_stats['total_users']}
            - Average User Age: {users_stats['avg_age']:.1f}
            - Total Products: {products_stats['total_products']}
            - Average Product Price: ${products_stats['avg_price']:.2f}
            """

            print(f"   Current Data: {data_context}")

            try:
                result = await session.call_tool(
                    "chat_with_context",
                    {
                        "message": "Based on these statistics, what business insights can you provide?",
                        "context": data_context,
                        "model": "llama3.2",
                    },
                )
                print(
                    f"\n   💡 Business Insights:\n   {extract_text_content(result)}")
            except Exception as e:
                print(f"   Error: {e}")

            print("\n🎉 Advanced LlamaIndex example completed!")
            print("\nThis example demonstrated:")
            print("  ✓ Natural language to SQL conversion")
            print("  ✓ AI-powered database analysis")
            print("  ✓ Context-aware conversations")
            print("  ✓ Data-driven business insights")


if __name__ == "__main__":
    asyncio.run(llamaindex_example())
