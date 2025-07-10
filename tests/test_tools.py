"""
Tests for MCP server tools.
"""

import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock

from mcp_simple_db_access import server


class TestMCPTools:
    """Test cases for MCP server tools."""

    @pytest.mark.asyncio
    async def test_query_database_success(self, populated_db):
        """Test successful database query."""
        with patch.object(server, "db_manager", populated_db):
            result = await server.query_database("SELECT * FROM users")

            # Should return JSON string
            data = json.loads(result)
            assert len(data) == 2
            assert data[0]["name"] == "Test User 1"
            assert data[1]["name"] == "Test User 2"

    @pytest.mark.asyncio
    async def test_query_database_non_select_blocked(self, populated_db):
        """Test that non-SELECT queries are blocked."""
        with patch.object(server, "db_manager", populated_db):
            result = await server.query_database("DELETE FROM users")

            assert "Only SELECT queries are allowed" in result

    @pytest.mark.asyncio
    async def test_query_database_empty_result(self, populated_db):
        """Test query with no results."""
        with patch.object(server, "db_manager", populated_db):
            result = await server.query_database("SELECT * FROM users WHERE age > 100")

            assert "returned no results" in result

    @pytest.mark.asyncio
    async def test_query_database_error_handling(self, populated_db):
        """Test error handling in database queries."""
        with patch.object(server, "db_manager", populated_db):
            result = await server.query_database("SELECT * FROM nonexistent_table")

            assert "Database error" in result

    @pytest.mark.asyncio
    async def test_insert_sample_data(self, db_manager):
        """Test inserting sample data."""
        with patch.object(server, "db_manager", db_manager):
            result = await server.insert_sample_data()

            assert "Sample data inserted successfully" in result

            # Verify data was inserted
            users = await db_manager.execute_query("SELECT * FROM users")
            products = await db_manager.execute_query("SELECT * FROM products")

            assert len(users) == 2
            assert len(products) == 2
            assert users[0]["name"] == "John Doe"
            assert products[0]["name"] == "Laptop"

    @pytest.mark.asyncio
    async def test_get_database_schema(self, populated_db):
        """Test getting database schema."""
        with patch.object(server, "db_manager", populated_db):
            result = await server.get_database_schema()

            schema = json.loads(result)

            # Should have all three tables
            assert "users" in schema
            assert "products" in schema
            assert "orders" in schema

            # Check users table structure
            users_schema = schema["users"]
            assert users_schema["row_count"] == 2

            # Check column information
            columns = users_schema["columns"]
            column_names = [col["name"] for col in columns]
            assert "id" in column_names
            assert "name" in column_names
            assert "email" in column_names
            assert "age" in column_names

    @pytest.mark.asyncio
    async def test_create_table_success(self, db_manager):
        """Test successful table creation."""
        with patch.object(server, "db_manager", db_manager):
            result = await server.create_table(
                "test_table", "CREATE TABLE test_table (id INTEGER PRIMARY KEY, name TEXT)"
            )

            assert "created successfully" in result

            # Verify table was created
            tables = await db_manager.execute_query(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='test_table'"
            )
            assert len(tables) == 1

    @pytest.mark.asyncio
    async def test_create_table_invalid_sql(self, db_manager):
        """Test table creation with invalid SQL."""
        with patch.object(server, "db_manager", db_manager):
            result = await server.create_table("test_table", "DROP TABLE users")  # Not a CREATE TABLE statement

            assert "Only CREATE TABLE statements are allowed" in result

    @pytest.mark.asyncio
    async def test_chat_with_ollama(self, mock_ollama_client):
        """Test chat with Ollama."""
        mock_ollama_client.generate.return_value = "Hello! I'm doing well."

        with patch.object(server, "ollama_client", mock_ollama_client):
            result = await server.chat_with_ollama("How are you?", "llama3.2")

            assert result == "Hello! I'm doing well."
            mock_ollama_client.generate.assert_called_once_with("llama3.2", "How are you?")

    @pytest.mark.asyncio
    async def test_chat_with_ollama_error(self, mock_ollama_client):
        """Test chat with Ollama error handling."""
        mock_ollama_client.generate.side_effect = Exception("Connection failed")

        with patch.object(server, "ollama_client", mock_ollama_client):
            result = await server.chat_with_ollama("Hello", "llama3.2")

            assert "Error communicating with Ollama" in result

    @pytest.mark.asyncio
    async def test_list_ollama_models(self, mock_ollama_client):
        """Test listing Ollama models."""
        mock_ollama_client.list_models.return_value = ["llama3.2", "gemma2"]

        with patch.object(server, "ollama_client", mock_ollama_client):
            result = await server.list_ollama_models()

            assert "Available Ollama models:" in result
            assert "llama3.2" in result
            assert "gemma2" in result

    @pytest.mark.asyncio
    async def test_list_ollama_models_empty(self, mock_ollama_client):
        """Test listing Ollama models when none available."""
        mock_ollama_client.list_models.return_value = []

        with patch.object(server, "ollama_client", mock_ollama_client):
            result = await server.list_ollama_models()

            assert "No models found" in result

    @pytest.mark.asyncio
    async def test_analyze_data_with_llm(self, populated_db, mock_ollama_client):
        """Test data analysis with LLM."""
        mock_ollama_client.generate.return_value = "Analysis result"

        with (
            patch.object(server, "db_manager", populated_db),
            patch.object(server, "ollama_client", mock_ollama_client),
        ):

            result = await server.analyze_data_with_llm("users", "What patterns do you see?")

            assert result == "Analysis result"

            # Verify the LLM was called with appropriate prompt
            mock_ollama_client.generate.assert_called_once()
            call_args = mock_ollama_client.generate.call_args
            prompt = call_args[0][1]  # Second argument is the prompt

            assert "users" in prompt
            assert "What patterns do you see?" in prompt

    @pytest.mark.asyncio
    async def test_chat_with_context(self, mock_ollama_client):
        """Test chat with context."""
        mock_ollama_client.generate.return_value = "Contextual response"

        with patch.object(server, "ollama_client", mock_ollama_client):
            result = await server.chat_with_context(
                "What can you tell me?", "Database contains user information", "llama3.2"
            )

            assert result == "Contextual response"

            # Verify the prompt includes context
            call_args = mock_ollama_client.generate.call_args
            prompt = call_args[0][1]

            assert "Context: Database contains user information" in prompt
            assert "User: What can you tell me?" in prompt

    @pytest.mark.asyncio
    async def test_chat_with_context_no_context(self, mock_ollama_client):
        """Test chat with context when no context provided."""
        mock_ollama_client.generate.return_value = "Simple response"

        with patch.object(server, "ollama_client", mock_ollama_client):
            result = await server.chat_with_context("Hello", "", "llama3.2")

            assert result == "Simple response"

            # Verify the prompt is just the message
            call_args = mock_ollama_client.generate.call_args
            prompt = call_args[0][1]

            assert prompt == "Hello"

    @pytest.mark.asyncio
    async def test_analyze_database_with_llamaindex(self, populated_db, mock_ollama_client):
        """Test comprehensive database analysis."""
        mock_ollama_client.generate.return_value = "Comprehensive analysis"

        with (
            patch.object(server, "db_manager", populated_db),
            patch.object(server, "ollama_client", mock_ollama_client),
        ):

            result = await server.analyze_database_with_llamaindex("What insights can you provide?")

            assert result == "Comprehensive analysis"

            # Verify the prompt includes schema and sample data
            call_args = mock_ollama_client.generate.call_args
            prompt = call_args[0][1]

            assert "Database Schema:" in prompt
            assert "Sample Data:" in prompt
            assert "What insights can you provide?" in prompt

    @pytest.mark.asyncio
    async def test_generate_sql_with_llamaindex(self, populated_db, mock_ollama_client):
        """Test SQL generation with LlamaIndex."""
        mock_ollama_client.generate.return_value = "SELECT * FROM users WHERE age > 25"

        with (
            patch.object(server, "db_manager", populated_db),
            patch.object(server, "ollama_client", mock_ollama_client),
        ):

            result = await server.generate_sql_with_llamaindex("Find users older than 25")

            assert "Generated SQL Query:" in result
            assert "SELECT * FROM users WHERE age > 25" in result
            assert "use the query_database tool" in result

    @pytest.mark.asyncio
    async def test_generate_sql_with_llamaindex_code_blocks(self, populated_db, mock_ollama_client):
        """Test SQL generation with code block formatting."""
        mock_ollama_client.generate.return_value = "```sql\nSELECT * FROM users\n```"

        with (
            patch.object(server, "db_manager", populated_db),
            patch.object(server, "ollama_client", mock_ollama_client),
        ):

            result = await server.generate_sql_with_llamaindex("Show all users")

            # Should strip code block markers
            assert "Generated SQL Query:\nSELECT * FROM users" in result
