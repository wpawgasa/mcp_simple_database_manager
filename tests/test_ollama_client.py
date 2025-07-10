"""
Tests for OllamaLlamaIndexClient class.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx

from mcp_simple_db_access.server import OllamaLlamaIndexClient, get_ollama_llm


class TestOllamaLlamaIndexClient:
    """Test cases for OllamaLlamaIndexClient functionality."""

    def test_init(self):
        """Test client initialization."""
        client = OllamaLlamaIndexClient("http://test:11434")
        assert client.base_url == "http://test:11434"

    @pytest.mark.asyncio
    async def test_generate_success(self, mock_llama_index):
        """Test successful text generation."""
        # Setup mock
        mock_llama_index.acomplete.return_value = "Generated response"

        client = OllamaLlamaIndexClient()

        with patch("mcp_simple_db_access.server.get_ollama_llm", return_value=mock_llama_index):
            result = await client.generate("llama3.2", "Test prompt")

            assert result == "Generated response"
            mock_llama_index.acomplete.assert_called_once_with("Test prompt")

    @pytest.mark.asyncio
    async def test_generate_error_handling(self):
        """Test error handling in generate method."""
        client = OllamaLlamaIndexClient()

        with patch("mcp_simple_db_access.server.get_ollama_llm") as mock_get_llm:
            # Mock LLM to raise an exception
            mock_llm = MagicMock()
            mock_llm.acomplete = AsyncMock(side_effect=Exception("Connection error"))
            mock_get_llm.return_value = mock_llm

            result = await client.generate("llama3.2", "Test prompt")

            assert "Error communicating with Ollama via LlamaIndex" in result
            assert "Connection error" in result

    @pytest.mark.asyncio
    async def test_list_models_success(self):
        """Test successful model listing."""
        client = OllamaLlamaIndexClient()

        # Mock successful HTTP response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"models": [{"name": "llama3.2"}, {"name": "gemma2"}, {"name": "codellama"}]}

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            models = await client.list_models()

            assert models == ["llama3.2", "gemma2", "codellama"]
            mock_client.get.assert_called_once_with("http://localhost:11434/api/tags")

    @pytest.mark.asyncio
    async def test_list_models_empty_response(self):
        """Test listing models with empty response."""
        client = OllamaLlamaIndexClient()

        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"models": []}

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            models = await client.list_models()

            assert models == []

    @pytest.mark.asyncio
    async def test_list_models_error_handling(self):
        """Test error handling in list_models method."""
        client = OllamaLlamaIndexClient()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.get.side_effect = httpx.ConnectError("Connection failed")
            mock_client_class.return_value = mock_client

            models = await client.list_models()

            assert models == []

    @pytest.mark.asyncio
    async def test_chat_success(self, mock_llama_index):
        """Test successful chat functionality."""
        mock_llama_index.acomplete.return_value = "Chat response"

        client = OllamaLlamaIndexClient()
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "How are you?"},
        ]

        with patch("mcp_simple_db_access.server.get_ollama_llm", return_value=mock_llama_index):
            result = await client.chat("llama3.2", messages)

            assert result == "Chat response"

            # Check that messages were converted to prompt format
            expected_prompt = "user: Hello\nassistant: Hi there!\nuser: How are you?"
            mock_llama_index.acomplete.assert_called_once_with(expected_prompt)

    @pytest.mark.asyncio
    async def test_chat_error_handling(self):
        """Test error handling in chat method."""
        client = OllamaLlamaIndexClient()

        with patch("mcp_simple_db_access.server.get_ollama_llm") as mock_get_llm:
            mock_llm = MagicMock()
            mock_llm.acomplete = AsyncMock(side_effect=Exception("Chat error"))
            mock_get_llm.return_value = mock_llm

            messages = [{"role": "user", "content": "Hello"}]
            result = await client.chat("llama3.2", messages)

            assert "Error in chat with Ollama via LlamaIndex" in result
            assert "Chat error" in result


class TestOllamaLLMFunction:
    """Test cases for get_ollama_llm function."""

    @patch("mcp_simple_db_access.server.Ollama")
    def test_get_ollama_llm_default_params(self, mock_ollama_class):
        """Test get_ollama_llm with default parameters."""
        mock_instance = MagicMock()
        mock_ollama_class.return_value = mock_instance

        result = get_ollama_llm()

        mock_ollama_class.assert_called_once_with(
            model="gemma3n", base_url="http://localhost:11434", request_timeout=60.0  # DEFAULT_MODEL from server
        )
        assert result == mock_instance

    @patch("mcp_simple_db_access.server.Ollama")
    def test_get_ollama_llm_custom_params(self, mock_ollama_class):
        """Test get_ollama_llm with custom parameters."""
        mock_instance = MagicMock()
        mock_ollama_class.return_value = mock_instance

        result = get_ollama_llm("custom-model", "http://custom:8080")

        mock_ollama_class.assert_called_once_with(
            model="custom-model", base_url="http://custom:8080", request_timeout=60.0
        )
        assert result == mock_instance
