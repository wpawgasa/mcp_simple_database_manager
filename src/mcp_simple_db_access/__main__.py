#!/usr/bin/env python3
"""
CLI entry point for the MCP Simple DB Access server.
"""

from mcp_simple_db_access.server import main
import asyncio
import sys
from pathlib import Path

# Add src to path so we can import our module
sys.path.insert(0, str(Path(__file__).parent.parent))


if __name__ == "__main__":
    asyncio.run(main())
