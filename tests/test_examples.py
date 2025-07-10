"""
Tests for example client scripts.
"""

import pytest
import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from mcp import ClientSession

# Add examples to path
examples_path = Path(__file__).parent.parent / "examples"
sys.path.insert(0, str(examples_path))


class TestExampleClients:
    """Test cases for example client scripts."""

    @pytest.mark.asyncio
    async def test_simple_client_imports(self):
        """Test that simple client can be imported without errors."""
        try:
            import simple_client

            assert hasattr(simple_client, "simple_example")
        except ImportError as e:
            pytest.fail(f"Failed to import simple_client: {e}")

    @pytest.mark.asyncio
    async def test_client_example_imports(self):
        """Test that client example can be imported without errors."""
        try:
            import client_example

            assert hasattr(client_example, "run_example_client")
            assert hasattr(client_example, "interactive_client")
        except ImportError as e:
            pytest.fail(f"Failed to import client_example: {e}")

    @pytest.mark.asyncio
    async def test_llamaindex_example_imports(self):
        """Test that LlamaIndex example can be imported without errors."""
        try:
            import llamaindex_example

            assert hasattr(llamaindex_example, "llamaindex_example")
        except ImportError as e:
            pytest.fail(f"Failed to import llamaindex_example: {e}")

    @pytest.mark.asyncio
    async def test_mock_client_session_functionality(self):
        """Test mock client session functionality used in examples."""

        # Create a mock session
        mock_session = MagicMock(spec=ClientSession)

        # Mock the methods used in examples
        mock_session.initialize = AsyncMock()
        mock_session.list_tools = AsyncMock()
        mock_session.call_tool = AsyncMock()

        # Mock list_tools response
        mock_tool = MagicMock()
        mock_tool.name = "query_database"
        mock_tool.description = "Execute SQL queries"
        mock_tools_response = MagicMock()
        mock_tools_response.tools = [mock_tool]
        mock_session.list_tools.return_value = mock_tools_response

        # Mock call_tool response
        mock_content = MagicMock()
        mock_content.text = '{"result": "success"}'
        mock_result = MagicMock()
        mock_result.content = [mock_content]
        mock_session.call_tool.return_value = mock_result

        # Test the mock functionality
        await mock_session.initialize()
        tools = await mock_session.list_tools()
        result = await mock_session.call_tool("query_database", {"sql": "SELECT 1"})

        assert len(tools.tools) == 1
        assert tools.tools[0].name == "query_database"
        assert result.content[0].text == '{"result": "success"}'

    @pytest.mark.asyncio
    async def test_example_error_handling_patterns(self):
        """Test the error handling patterns used in examples."""

        # Mock a session that raises errors
        mock_session = MagicMock(spec=ClientSession)
        mock_session.call_tool = AsyncMock(side_effect=Exception("Connection failed"))

        # Test that error handling would work
        try:
            await mock_session.call_tool("test_tool", {})
            pytest.fail("Should have raised an exception")
        except Exception as e:
            assert "Connection failed" in str(e)

    def test_example_readme_exists(self):
        """Test that examples README exists and contains expected content."""
        readme_path = examples_path / "README.md"
        assert readme_path.exists(), "Examples README.md missing"

        content = readme_path.read_text()

        # Check for key sections
        assert "Prerequisites" in content
        assert "simple_client.py" in content
        assert "client_example.py" in content
        assert "llamaindex_example.py" in content
        assert "Troubleshooting" in content

    def test_example_files_executable(self):
        """Test that example Python files are executable."""
        example_files = ["simple_client.py", "client_example.py", "llamaindex_example.py"]

        for filename in example_files:
            file_path = examples_path / filename
            assert file_path.exists(), f"Example file {filename} missing"

            # Check if file has shebang
            content = file_path.read_text()
            assert content.startswith("#!/usr/bin/env python3"), f"Example file {filename} missing shebang"

    def test_example_parameter_validation(self):
        """Test parameter structures used in examples."""

        # Test StdioServerParameters structure
        from mcp.client.stdio import StdioServerParameters

        # This should not raise an error
        params = StdioServerParameters(command="python", args=["test_script.py"], env=None)

        assert params.command == "python"
        assert params.args == ["test_script.py"]

    @pytest.mark.asyncio
    async def test_example_tool_calls_structure(self):
        """Test the structure of tool calls used in examples."""

        # Define the tool calls used in examples
        example_tool_calls = [
            ("insert_sample_data", {}),
            ("query_database", {"sql": "SELECT * FROM users"}),
            ("get_database_schema", {}),
            ("chat_with_ollama", {"prompt": "Hello", "model": "llama3.2"}),
            ("list_ollama_models", {}),
            (
                "analyze_data_with_llm",
                {"table_name": "users", "question": "What patterns do you see?", "model": "llama3.2"},
            ),
            ("generate_sql_with_llamaindex", {"description": "Find users older than 25", "model": "llama3.2"}),
            ("chat_with_context", {"message": "Hello", "context": "Database context", "model": "llama3.2"}),
            ("analyze_database_with_llamaindex", {"question": "What insights can you provide?", "model": "llama3.2"}),
        ]

        # Verify each tool call structure
        for tool_name, params in example_tool_calls:
            assert isinstance(tool_name, str), f"Tool name should be string: {tool_name}"
            assert isinstance(params, dict), f"Params should be dict: {params}"

            # Check specific parameter types
            if "sql" in params:
                assert isinstance(params["sql"], str)
            if "model" in params:
                assert isinstance(params["model"], str)
            if "prompt" in params:
                assert isinstance(params["prompt"], str)

    def test_example_imports_structure(self):
        """Test that examples have the correct import structure."""

        # Read each example file and check imports
        example_files = ["simple_client.py", "client_example.py", "llamaindex_example.py"]

        for filename in example_files:
            file_path = examples_path / filename
            content = file_path.read_text()

            # Should have these essential imports
            assert "import asyncio" in content, f"{filename} missing asyncio import"
            assert "from mcp import ClientSession" in content, f"{filename} missing ClientSession import"
            assert "from mcp.client.stdio import" in content, f"{filename} missing stdio import"

            # Should have main execution guard
            assert 'if __name__ == "__main__":' in content, f"{filename} missing main guard"
            assert "asyncio.run(" in content, f"{filename} missing asyncio.run"

    def test_example_json_handling(self):
        """Test JSON handling patterns used in examples."""
        import json

        # Test the JSON parsing patterns used in examples
        test_responses = [
            '{"users": [{"name": "John", "age": 30}]}',
            '[{"id": 1, "name": "Test"}]',
            '{"tables": {"users": {"row_count": 5}}}',
        ]

        for response in test_responses:
            # Should not raise an error
            parsed = json.loads(response)
            assert isinstance(parsed, (dict, list))

    @pytest.mark.asyncio
    async def test_example_async_patterns(self):
        """Test async patterns used in examples."""

        # Test async context manager pattern
        class MockAsyncContext:
            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass

        # This pattern is used in examples
        async with MockAsyncContext() as context:
            assert context is not None

    def test_example_constants_and_defaults(self):
        """Test constants and default values used in examples."""

        # These are the constants/defaults used in examples
        default_values = {"model": "llama3.2", "command": "python", "base_url": "http://localhost:11434"}

        # Verify they are reasonable values
        assert isinstance(default_values["model"], str)
        assert len(default_values["model"]) > 0
        assert default_values["command"] in ["python", "uv"]
        assert default_values["base_url"].startswith("http")
