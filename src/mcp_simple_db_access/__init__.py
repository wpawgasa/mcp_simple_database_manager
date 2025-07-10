"""
MCP Server for simple database access with Ollama integration.

This package provides an MCP server that enables:
- Database operations with SQLite
- Local LLM integration via Ollama
- Data analysis and querying capabilities
"""

from .server import main

__version__ = "0.1.0"
__all__ = ["main"]
