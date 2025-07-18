"""
Test configuration and fixtures for MCP Simple DB Access Server tests.
"""

from mcp_simple_db_access.server import (
    DatabaseManager,
    OllamaLlamaIndexClient,
    mcp,
    get_ollama_llm,
)
import asyncio
import json
import tempfile
from pathlib import Path
from typing import AsyncGenerator, Dict, Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
import aiosqlite
from mcp import ClientSession, ServerSession
from mcp.server.stdio import stdio_server
from mcp.types import Tool

# Import our server components
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def temp_db() -> AsyncGenerator[str, None]:
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        temp_db_path = f.name

    # Initialize the test database
    db_manager = DatabaseManager(temp_db_path)
    await db_manager.init_db()

    yield temp_db_path

    # Cleanup
    Path(temp_db_path).unlink(missing_ok=True)


@pytest_asyncio.fixture
async def db_manager(temp_db: str) -> DatabaseManager:
    """Create a DatabaseManager instance with test database."""
    return DatabaseManager(temp_db)


@pytest.fixture
def mock_ollama_client():
    """Mock Ollama client for testing without requiring Ollama to be running."""
    client = MagicMock(spec=OllamaLlamaIndexClient)

    # Mock async methods
    client.generate = AsyncMock(return_value="Mock LLM response")
    client.list_models = AsyncMock(return_value=["llama3.2", "gemma2"])
    client.chat = AsyncMock(return_value="Mock chat response")

    return client


@pytest_asyncio.fixture
async def populated_db(db_manager: DatabaseManager) -> DatabaseManager:
    """Database manager with sample data inserted."""
    # Insert test users
    await db_manager.execute_write(
        "INSERT INTO users (name, email, age) VALUES (?, ?, ?)", (
            "Test User 1", "test1@example.com", 25)
    )
    await db_manager.execute_write(
        "INSERT INTO users (name, email, age) VALUES (?, ?, ?)", (
            "Test User 2", "test2@example.com", 30)
    )

    # Insert test products
    await db_manager.execute_write(
        "INSERT INTO products (name, price, category, stock_quantity) VALUES (?, ?, ?, ?)",
        ("Test Product 1", 99.99, "Electronics", 10),
    )
    await db_manager.execute_write(
        "INSERT INTO products (name, price, category, stock_quantity) VALUES (?, ?, ?, ?)",
        ("Test Product 2", 19.99, "Books", 50),
    )

    # Insert test orders
    await db_manager.execute_write(
        "INSERT INTO orders (user_id, product_id, quantity, total_price) VALUES (?, ?, ?, ?)", (
            1, 1, 2, 199.98)
    )

    return db_manager


@pytest.fixture
def mock_llama_index():
    """Mock LlamaIndex components."""
    with patch("mcp_simple_db_access.server.get_ollama_llm") as mock_get_llm:
        mock_llm = MagicMock()
        mock_llm.acomplete = AsyncMock(return_value="Mock LlamaIndex response")
        mock_get_llm.return_value = mock_llm
        yield mock_llm


@pytest.fixture
def sample_tools_data():
    """Sample data for testing tools."""
    return {
        "query": "SELECT * FROM users LIMIT 5",
        "table_name": "users",
        "question": "What patterns do you see in the user data?",
        "prompt": "Hello, how are you?",
        "model": "llama3.2",
        "description": "Find all users older than 25",
        "context": "Database analysis context",
        "message": "What can you tell me about this data?",
    }


class MockMCPServer:
    """Mock MCP server for testing tool functionality."""

    def __init__(self, db_manager: DatabaseManager, ollama_client):
        self.db_manager = db_manager
        self.ollama_client = ollama_client

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Mock tool calling functionality."""
        # This would normally go through the MCP protocol
        # For testing, we'll call the functions directly
        from mcp_simple_db_access import server

        # Patch the global instances for testing
        with (
            patch.object(server, "db_manager", self.db_manager),
            patch.object(server, "ollama_client", self.ollama_client),
        ):

            if tool_name == "query_database":
                return await server.query_database(arguments["sql"])
            elif tool_name == "insert_sample_data":
                return await server.insert_sample_data()
            elif tool_name == "get_database_schema":
                return await server.get_database_schema()
            elif tool_name == "chat_with_ollama":
                return await server.chat_with_ollama(arguments["prompt"], arguments.get("model", "llama3.2"))
            elif tool_name == "list_ollama_models":
                return await server.list_ollama_models()
            # Add more tools as needed
            else:
                raise ValueError(f"Unknown tool: {tool_name}")


@pytest_asyncio.fixture
async def mock_mcp_server(db_manager: DatabaseManager, mock_ollama_client) -> MockMCPServer:
    """Create a mock MCP server for testing."""
    return MockMCPServer(db_manager, mock_ollama_client)
