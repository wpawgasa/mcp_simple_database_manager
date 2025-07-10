#!/usr/bin/env python3
"""
Entry point script for the MCP Simple DB Access server.
"""

import asyncio
from src.mcp_simple_db_access.server import main

if __name__ == "__main__":
    asyncio.run(main())
