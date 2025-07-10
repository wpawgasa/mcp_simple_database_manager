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
        # Mock the database path
        with patch("mcp_simple_db_access.server.DB_PATH", temp_db):
            # This should not raise any exceptions
            await main()

    @pytest.mark.asyncio
    async def test_server_tools_registration(self):
        """Test that all expected tools are registered."""
        # Get the tools from the MCP server
        tools = mcp.list_tools()

        expected_tools = {
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
        }

        registered_tools = {tool.name for tool in tools}

        # Check that all expected tools are registered
        for tool_name in expected_tools:
            assert tool_name in registered_tools, f"Tool {tool_name} not registered"

    @pytest.mark.asyncio
    async def test_tool_descriptions_present(self):
        """Test that all tools have descriptions."""
        tools = mcp.list_tools()

        for tool in tools:
            assert tool.description, f"Tool {tool.name} missing description"
            assert len(tool.description) > 10, f"Tool {tool.name} has too short description"

    @pytest.mark.asyncio
    async def test_tool_input_schemas(self):
        """Test that tools have proper input schemas."""
        tools = mcp.list_tools()
        tool_dict = {tool.name: tool for tool in tools}

        # Test specific tools that should have parameters
        assert "sql" in str(tool_dict["query_database"].inputSchema)
        assert "prompt" in str(tool_dict["chat_with_ollama"].inputSchema)
        assert "table_name" in str(tool_dict["analyze_data_with_llm"].inputSchema)
        assert "description" in str(tool_dict["generate_sql_with_llamaindex"].inputSchema)

    @pytest.mark.asyncio
    async def test_database_workflow(self, temp_db, mock_ollama_client):
        """Test a complete database workflow."""
        with (
            patch("mcp_simple_db_access.server.DB_PATH", temp_db),
            patch("mcp_simple_db_access.server.ollama_client", mock_ollama_client),
        ):

            # 1. Insert sample data
            result = await mcp.call_tool("insert_sample_data", {})
            assert "successfully" in result["content"][0]["text"]

            # 2. Query the data
            result = await mcp.call_tool("query_database", {"sql": "SELECT * FROM users"})
            users = json.loads(result["content"][0]["text"])
            assert len(users) == 2

            # 3. Get schema
            result = await mcp.call_tool("get_database_schema", {})
            schema = json.loads(result["content"][0]["text"])
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

            # 1. Insert sample data first
            await mcp.call_tool("insert_sample_data", {})

            # 2. List models
            result = await mcp.call_tool("list_ollama_models", {})
            assert "llama3.2" in result["content"][0]["text"]

            # 3. Chat with Ollama
            result = await mcp.call_tool("chat_with_ollama", {"prompt": "Hello", "model": "llama3.2"})
            assert result["content"][0]["text"] == "Mock LLM response"

            # 4. Analyze data with LLM
            result = await mcp.call_tool(
                "analyze_data_with_llm",
                {"table_name": "users", "question": "What patterns do you see?", "model": "llama3.2"},
            )
            assert result["content"][0]["text"] == "Mock LLM response"

    @pytest.mark.asyncio
    async def test_llamaindex_workflow(self, temp_db, mock_ollama_client):
        """Test LlamaIndex-specific features."""
        mock_ollama_client.generate.return_value = "LlamaIndex analysis result"

        with (
            patch("mcp_simple_db_access.server.DB_PATH", temp_db),
            patch("mcp_simple_db_access.server.ollama_client", mock_ollama_client),
        ):

            # 1. Insert sample data
            await mcp.call_tool("insert_sample_data", {})

            # 2. Chat with context
            result = await mcp.call_tool(
                "chat_with_context",
                {
                    "message": "What can you tell me about this database?",
                    "context": "This is a test database with sample data",
                    "model": "llama3.2",
                },
            )
            assert result["content"][0]["text"] == "LlamaIndex analysis result"

            # 3. Comprehensive database analysis
            result = await mcp.call_tool(
                "analyze_database_with_llamaindex",
                {"question": "Provide insights about the database", "model": "llama3.2"},
            )
            assert result["content"][0]["text"] == "LlamaIndex analysis result"

            # 4. SQL generation
            mock_ollama_client.generate.return_value = "SELECT * FROM users WHERE age > 25"
            result = await mcp.call_tool(
                "generate_sql_with_llamaindex", {"description": "Find users older than 25", "model": "llama3.2"}
            )
            assert "SELECT * FROM users WHERE age > 25" in result["content"][0]["text"]

    @pytest.mark.asyncio
    async def test_error_handling_workflow(self, temp_db, mock_ollama_client):
        """Test error handling across different scenarios."""
        with (
            patch("mcp_simple_db_access.server.DB_PATH", temp_db),
            patch("mcp_simple_db_access.server.ollama_client", mock_ollama_client),
        ):

            # 1. Invalid SQL query
            result = await mcp.call_tool("query_database", {"sql": "DELETE FROM users"})  # Not allowed
            assert "Only SELECT queries are allowed" in result["content"][0]["text"]

            # 2. Query non-existent table
            result = await mcp.call_tool("query_database", {"sql": "SELECT * FROM nonexistent_table"})
            assert "Database error" in result["content"][0]["text"]

            # 3. LLM error
            mock_ollama_client.generate.side_effect = Exception("LLM error")
            result = await mcp.call_tool("chat_with_ollama", {"prompt": "Hello", "model": "llama3.2"})
            assert "Error communicating with Ollama" in result["content"][0]["text"]

    @pytest.mark.asyncio
    async def test_security_features(self, temp_db):
        """Test security features of the server."""
        with patch("mcp_simple_db_access.server.DB_PATH", temp_db):

            # 1. Insert sample data first
            await mcp.call_tool("insert_sample_data", {})

            # 2. Test SQL injection prevention
            malicious_queries = [
                "SELECT * FROM users; DROP TABLE users; --",
                "'; DELETE FROM users; --",
                "SELECT * FROM users UNION SELECT * FROM sqlite_master",
            ]

            for query in malicious_queries:
                # These should either be blocked or fail safely
                result = await mcp.call_tool("query_database", {"sql": query})
                # Should not succeed (either blocked or error)
                assert (
                    "Database error" in result["content"][0]["text"]
                    or "Only SELECT queries are allowed" in result["content"][0]["text"]
                )

            # 3. Verify users table still exists
            result = await mcp.call_tool("query_database", {"sql": "SELECT COUNT(*) as count FROM users"})
            count_data = json.loads(result["content"][0]["text"])
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
