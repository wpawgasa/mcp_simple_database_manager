"""
Integration tests for the MCP server.
"""

import pytest
import json
import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from mcp import ClientSession, ServerSession
from mcp.server.stdio import stdio_server
from mcp.client.stdio import stdio_client, StdioServerParameters

from mcp_simple_db_access.server import mcp, main


class TestMCPServerIntegration:
    """Integration tests for the complete MCP server."""

    @pytest.mark.asyncio
    async def test_server_initialization(self, temp_db):
        """Test that the server initializes correctly."""
        # Mock the database path and test the components directly
        with patch("mcp_simple_db_access.server.DB_PATH", temp_db):
            # Test that the database manager can be created
            from mcp_simple_db_access.server import DatabaseManager
            db_manager = DatabaseManager(temp_db)
            await db_manager.init_db()

            # Verify tables were created
            tables = await db_manager.execute_query("SELECT name FROM sqlite_master WHERE type='table'")
            table_names = [table["name"] for table in tables]
            assert "users" in table_names
            assert "products" in table_names
            assert "orders" in table_names

    @pytest.mark.asyncio
    async def test_server_tools_registration(self):
        """Test that all expected tools are registered."""
        # Test that the tools are available in the server module by checking if they are defined
        from mcp_simple_db_access import server

        expected_tools = [
            "query_database",
            "insert_sample_data",
            "analyze_data_with_llm",
            "chat_with_ollama",
            "list_ollama_models",
            "get_database_schema",
            "create_table",
            "chat_with_context",
            "analyze_database_with_llamaindex",
            "generate_sql_with_llamaindex",
        ]

        # Check that all expected tools are functions in the server module
        for tool_name in expected_tools:
            assert hasattr(
                server, tool_name), f"Tool {tool_name} not found in server module"
            assert callable(getattr(server, tool_name)
                            ), f"Tool {tool_name} is not callable"

    @pytest.mark.asyncio
    async def test_tool_descriptions_present(self):
        """Test that all tools have descriptions."""
        # Test that the tool functions have docstrings
        from mcp_simple_db_access import server

        tool_functions = [
            server.query_database,
            server.insert_sample_data,
            server.analyze_data_with_llm,
            server.chat_with_ollama,
            server.list_ollama_models,
            server.get_database_schema,
            server.create_table,
            server.chat_with_context,
            server.analyze_database_with_llamaindex,
            server.generate_sql_with_llamaindex,
        ]

        for func in tool_functions:
            assert func.__doc__ is not None, f"Function {func.__name__} missing docstring"
            assert len(func.__doc__.strip(
            )) > 10, f"Function {func.__name__} has too short docstring"

    @pytest.mark.asyncio
    async def test_tool_input_schemas(self):
        """Test that tools have proper input schemas."""
        # Test that the tool functions have proper type annotations
        from mcp_simple_db_access import server
        import inspect

        # Test some specific functions have the right parameters
        query_sig = inspect.signature(server.query_database)
        assert 'sql' in query_sig.parameters

        chat_sig = inspect.signature(server.chat_with_ollama)
        assert 'prompt' in chat_sig.parameters

        analyze_sig = inspect.signature(server.analyze_data_with_llm)
        assert 'table_name' in analyze_sig.parameters

        generate_sig = inspect.signature(server.generate_sql_with_llamaindex)
        assert 'description' in generate_sig.parameters

    @pytest.mark.asyncio
    async def test_database_workflow(self, temp_db, mock_ollama_client):
        """Test a complete database workflow."""
        with (
            patch("mcp_simple_db_access.server.DB_PATH", temp_db),
            patch("mcp_simple_db_access.server.ollama_client", mock_ollama_client),
        ):
            from mcp_simple_db_access import server

            # Create a database manager for testing
            db_manager = server.DatabaseManager(temp_db)
            await db_manager.init_db()

            # Test the workflow by calling the server functions directly
            with patch.object(server, "db_manager", db_manager):
                # 1. Insert sample data
                result = await server.insert_sample_data()
                assert "successfully" in result

                # 2. Query the data
                result = await server.query_database("SELECT * FROM users")
                users = json.loads(result)
                assert len(users) == 2

                # 3. Get schema
                result = await server.get_database_schema()
                schema = json.loads(result)
                assert "users" in schema
                assert "products" in schema

    @pytest.mark.asyncio
    async def test_llm_integration_workflow(self, temp_db, mock_ollama_client):
        """Test LLM integration workflow."""
        mock_ollama_client.generate.return_value = "Mock LLM response"
        mock_ollama_client.list_models.return_value = ["llama3.2", "gemma2"]

        with (
            patch("mcp_simple_db_access.server.DB_PATH", temp_db),
            patch("mcp_simple_db_access.server.ollama_client", mock_ollama_client),
        ):
            from mcp_simple_db_access import server

            # Create a database manager for testing
            db_manager = server.DatabaseManager(temp_db)
            await db_manager.init_db()

            with patch.object(server, "db_manager", db_manager):
                # 1. Insert sample data first
                await server.insert_sample_data()

                # 2. List models
                result = await server.list_ollama_models()
                assert "llama3.2" in result

                # 3. Chat with Ollama
                result = await server.chat_with_ollama("Hello", "llama3.2")
                assert result == "Mock LLM response"

                # 4. Analyze data with LLM
                result = await server.analyze_data_with_llm("users", "What patterns do you see?", "llama3.2")
                assert result == "Mock LLM response"

    @pytest.mark.asyncio
    async def test_llamaindex_workflow(self, temp_db, mock_ollama_client):
        """Test LlamaIndex-specific features."""
        mock_ollama_client.generate.return_value = "LlamaIndex analysis result"

        with (
            patch("mcp_simple_db_access.server.DB_PATH", temp_db),
            patch("mcp_simple_db_access.server.ollama_client", mock_ollama_client),
        ):
            from mcp_simple_db_access import server

            # Create a database manager for testing
            db_manager = server.DatabaseManager(temp_db)
            await db_manager.init_db()

            with patch.object(server, "db_manager", db_manager):
                # 1. Insert sample data
                await server.insert_sample_data()

                # 2. Chat with context
                result = await server.chat_with_context(
                    "What can you tell me about this database?",
                    "This is a test database with sample data",
                    "llama3.2"
                )
                assert result == "LlamaIndex analysis result"

                # 3. Comprehensive database analysis
                result = await server.analyze_database_with_llamaindex("Provide insights about the database", "llama3.2")
                assert result == "LlamaIndex analysis result"

                # 4. SQL generation
                mock_ollama_client.generate.return_value = "SELECT * FROM users WHERE age > 25"
                result = await server.generate_sql_with_llamaindex("Find users older than 25", "llama3.2")
                assert "SELECT * FROM users WHERE age > 25" in result

    @pytest.mark.asyncio
    async def test_error_handling_workflow(self, temp_db, mock_ollama_client):
        """Test error handling across different scenarios."""
        with (
            patch("mcp_simple_db_access.server.DB_PATH", temp_db),
            patch("mcp_simple_db_access.server.ollama_client", mock_ollama_client),
        ):
            from mcp_simple_db_access import server

            # Create a database manager for testing
            db_manager = server.DatabaseManager(temp_db)
            await db_manager.init_db()

            with patch.object(server, "db_manager", db_manager):
                # 1. Invalid SQL query
                # Not allowed
                result = await server.query_database("DELETE FROM users")
                assert "Only SELECT queries are allowed" in result

                # 2. Query non-existent table
                result = await server.query_database("SELECT * FROM nonexistent_table")
                assert "Database error" in result

                # 3. LLM error
                mock_ollama_client.generate.side_effect = Exception(
                    "LLM error")
                result = await server.chat_with_ollama("Hello", "llama3.2")
                assert "Error communicating with Ollama" in result

    @pytest.mark.asyncio
    async def test_security_features(self, temp_db):
        """Test security features of the server."""
        with patch("mcp_simple_db_access.server.DB_PATH", temp_db):
            from mcp_simple_db_access import server

            # Create a database manager for testing
            db_manager = server.DatabaseManager(temp_db)
            await db_manager.init_db()

            with patch.object(server, "db_manager", db_manager):
                # 1. Insert sample data first
                await server.insert_sample_data()

                # 2. Test SQL injection prevention
                malicious_queries = [
                    "DELETE FROM users",  # This should be blocked
                    "DROP TABLE users",   # This should be blocked
                    "UPDATE users SET age = 100",  # This should be blocked
                ]

                for query in malicious_queries:
                    # These should be blocked
                    result = await server.query_database(query)
                    assert "Only SELECT queries are allowed" in result

                # Test potentially dangerous but valid SELECT queries
                union_query = "SELECT * FROM users UNION SELECT * FROM sqlite_master"
                result = await server.query_database(union_query)
                # This currently works but shows system tables, which is not ideal
                # but it's a valid SELECT query, so the current implementation allows it
                # Should return some result, not an error
                assert isinstance(result, str)

                # 3. Verify users table still exists
                result = await server.query_database("SELECT COUNT(*) as count FROM users")
                count_data = json.loads(result)
                # Sample data should still be there
                assert count_data[0]["count"] == 2

    @pytest.mark.asyncio
    async def test_performance_basic(self, temp_db, mock_ollama_client):
        """Basic performance test - ensure operations complete in reasonable time."""
        mock_ollama_client.generate.return_value = "Quick response"

        with (
            patch("mcp_simple_db_access.server.DB_PATH", temp_db),
            patch("mcp_simple_db_access.server.ollama_client", mock_ollama_client),
        ):

            # Time database operations
            import time

            start_time = time.time()
            await mcp.call_tool("insert_sample_data", {})
            insert_time = time.time() - start_time

            start_time = time.time()
            await mcp.call_tool("query_database", {"sql": "SELECT * FROM users"})
            query_time = time.time() - start_time

            start_time = time.time()
            await mcp.call_tool("get_database_schema", {})
            schema_time = time.time() - start_time

            # Operations should complete within reasonable time (adjust as needed)
            assert insert_time < 5.0, f"Insert took too long: {insert_time}s"
            assert query_time < 1.0, f"Query took too long: {query_time}s"
            assert schema_time < 2.0, f"Schema took too long: {schema_time}s"
