#!/usr/bin/env python3
"""
MCP Server for simple database access with Ollama integration.

This server provides tools for:
1. Database operations (SQLite)
2. Local LLM interaction via Ollama
3. File system operations
4. Data analysis and querying
"""

import asyncio
import json
import os
import aiosqlite
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import httpx
import logging

from mcp.server.fastmcp import FastMCP
from mcp.types import Tool, TextContent, Resource

# LlamaIndex imports
from llama_index.core import Settings
from llama_index.llms.ollama import Ollama
from llama_index.core.llms.llm import LLM

# Initialize FastMCP server
mcp = FastMCP("mcp-simple-db-access")

# Constants
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
DEFAULT_MODEL = "llama3.2"
DB_PATH = "data/app.db"

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure data directory exists
Path("data").mkdir(exist_ok=True)

# Initialize LlamaIndex Ollama LLM


def get_ollama_llm(model: str = DEFAULT_MODEL, base_url: str = OLLAMA_BASE_URL) -> Ollama:
    """Get Ollama LLM instance via LlamaIndex."""
    return Ollama(model=model, base_url=base_url, request_timeout=60.0)


# Set global LLM for LlamaIndex
Settings.llm = get_ollama_llm()


class OllamaLlamaIndexClient:
    """Client for interacting with Ollama via LlamaIndex."""

    def __init__(self, base_url: str = OLLAMA_BASE_URL):
        self.base_url = base_url

    async def generate(self, model: str, prompt: str, **kwargs) -> str:
        """Generate text using Ollama model via LlamaIndex."""
        try:
            llm = get_ollama_llm(model, self.base_url)
            response = await llm.acomplete(prompt)
            return str(response)
        except Exception as e:
            logger.error(f"LlamaIndex Ollama error: {e}")
            return f"Error communicating with Ollama via LlamaIndex: {e}"

    async def list_models(self) -> List[str]:
        """List available models in Ollama."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
                result = response.json()
                return [model["name"] for model in result.get("models", [])]
            except Exception as e:
                logger.error(f"Error listing models: {e}")
                return []

    async def chat(self, model: str, messages: List[Dict[str, str]], **kwargs) -> str:
        """Chat with Ollama model via LlamaIndex."""
        try:
            llm = get_ollama_llm(model, self.base_url)
            # Convert messages to a single prompt for completion
            prompt = "\n".join(
                [f"{msg['role']}: {msg['content']}" for msg in messages])
            response = await llm.acomplete(prompt)
            return str(response)
        except Exception as e:
            logger.error(f"LlamaIndex Ollama chat error: {e}")
            return f"Error in chat with Ollama via LlamaIndex: {e}"


class DatabaseManager:
    """Manager for SQLite database operations."""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path

    async def init_db(self):
        """Initialize database with sample tables."""
        async with aiosqlite.connect(self.db_path) as db:
            # Create users table
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    age INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Create products table
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    price REAL NOT NULL,
                    category TEXT,
                    stock_quantity INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Create orders table
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    product_id INTEGER,
                    quantity INTEGER NOT NULL,
                    total_price REAL NOT NULL,
                    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (product_id) REFERENCES products(id)
                )
            """
            )

            await db.commit()

    async def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def execute_write(self, query: str, params: tuple = ()) -> int:
        """Execute an INSERT/UPDATE/DELETE query and return affected rows."""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(query, params) as cursor:
                await db.commit()
                return cursor.rowcount


# Initialize clients
ollama_client = OllamaLlamaIndexClient()
db_manager = DatabaseManager()


@mcp.tool()
async def query_database(sql: str) -> str:
    """Execute a SQL query on the database.

    Args:
        sql: The SQL query to execute (SELECT statements only for safety)
    """
    try:
        # Basic safety check - only allow SELECT queries
        if not sql.strip().upper().startswith("SELECT"):
            return "Error: Only SELECT queries are allowed for safety reasons."

        results = await db_manager.execute_query(sql)

        if not results:
            return "Query executed successfully but returned no results."

        # Format results as JSON for better readability
        return json.dumps(results, indent=2, default=str)

    except Exception as e:
        return f"Database error: {str(e)}"


@mcp.tool()
async def insert_sample_data() -> str:
    """Insert sample data into the database tables."""
    try:
        # Insert sample users
        await db_manager.execute_write(
            "INSERT OR IGNORE INTO users (name, email, age) VALUES (?, ?, ?)", (
                "John Doe", "john@example.com", 30)
        )
        await db_manager.execute_write(
            "INSERT OR IGNORE INTO users (name, email, age) VALUES (?, ?, ?)", (
                "Jane Smith", "jane@example.com", 25)
        )

        # Insert sample products
        await db_manager.execute_write(
            "INSERT OR IGNORE INTO products (name, price, category, stock_quantity) VALUES (?, ?, ?, ?)",
            ("Laptop", 999.99, "Electronics", 10),
        )
        await db_manager.execute_write(
            "INSERT OR IGNORE INTO products (name, price, category, stock_quantity) VALUES (?, ?, ?, ?)",
            ("Coffee Mug", 12.99, "Kitchen", 50),
        )

        return "Sample data inserted successfully!"

    except Exception as e:
        return f"Error inserting sample data: {str(e)}"


@mcp.tool()
async def analyze_data_with_llm(table_name: str, question: str, model: str = DEFAULT_MODEL) -> str:
    """Analyze database data using local LLM via Ollama.

    Args:
        table_name: Name of the database table to analyze
        question: Question to ask about the data
        model: Ollama model to use (default: llama3.2)
    """
    try:
        # First, get the table schema
        schema_query = f"PRAGMA table_info({table_name})"
        schema_results = await db_manager.execute_query(schema_query)

        # Get sample data from the table
        data_query = f"SELECT * FROM {table_name} LIMIT 10"
        data_results = await db_manager.execute_query(data_query)

        # Construct prompt for LLM
        prompt = f"""
        You are a data analyst. I have a database table called '{table_name}' with the following schema:
        {json.dumps(schema_results, indent=2)}
        
        Here's a sample of the data:
        {json.dumps(data_results, indent=2, default=str)}
        
        Question: {question}
        
        Please provide insights and analysis based on this data. If you need to suggest SQL queries, make sure they are SELECT queries only.
        """

        response = await ollama_client.generate(model, prompt)
        return response

    except Exception as e:
        return f"Error analyzing data with LLM: {str(e)}"


@mcp.tool()
async def chat_with_ollama(prompt: str, model: str = DEFAULT_MODEL) -> str:
    """Chat with local LLM via Ollama.

    Args:
        prompt: The prompt/question to send to the LLM
        model: Ollama model to use (default: llama3.2)
    """
    try:
        response = await ollama_client.generate(model, prompt)
        return response
    except Exception as e:
        return f"Error communicating with Ollama: {str(e)}"


@mcp.tool()
async def list_ollama_models() -> str:
    """List all available models in Ollama."""
    try:
        models = await ollama_client.list_models()
        if models:
            return "Available Ollama models:\n" + "\n".join(f"- {model}" for model in models)
        else:
            return "No models found. Make sure Ollama is running and has models installed."
    except Exception as e:
        return f"Error listing models: {str(e)}"


@mcp.tool()
async def get_database_schema() -> str:
    """Get the complete database schema with table information."""
    try:
        # Get list of tables
        tables_query = "SELECT name FROM sqlite_master WHERE type='table'"
        tables = await db_manager.execute_query(tables_query)

        schema_info = {}

        for table in tables:
            table_name = table["name"]
            # Get table schema
            schema_query = f"PRAGMA table_info({table_name})"
            schema = await db_manager.execute_query(schema_query)

            # Get row count
            count_query = f"SELECT COUNT(*) as count FROM {table_name}"
            count_result = await db_manager.execute_query(count_query)
            row_count = count_result[0]["count"] if count_result else 0

            schema_info[table_name] = {
                "columns": schema, "row_count": row_count}

        return json.dumps(schema_info, indent=2)

    except Exception as e:
        return f"Error getting database schema: {str(e)}"


@mcp.tool()
async def create_table(table_name: str, schema_sql: str) -> str:
    """Create a new table in the database.

    Args:
        table_name: Name for the new table
        schema_sql: SQL CREATE TABLE statement
    """
    try:
        # Basic validation
        if not schema_sql.strip().upper().startswith("CREATE TABLE"):
            return "Error: Only CREATE TABLE statements are allowed."

        await db_manager.execute_write(schema_sql)
        return f"Table '{table_name}' created successfully!"

    except Exception as e:
        return f"Error creating table: {str(e)}"


@mcp.tool()
async def chat_with_context(message: str, context: str = "", model: str = DEFAULT_MODEL) -> str:
    """Chat with LlamaIndex Ollama LLM with additional context.

    Args:
        message: The message/question to send to the LLM
        context: Additional context to provide to the LLM
        model: Ollama model to use (default: llama3.2)
    """
    try:
        if context:
            full_prompt = f"Context: {context}\n\nUser: {message}\n\nAssistant:"
        else:
            full_prompt = message

        response = await ollama_client.generate(model, full_prompt)
        return response
    except Exception as e:
        return f"Error in chat with context: {str(e)}"


@mcp.tool()
async def analyze_database_with_llamaindex(question: str, model: str = DEFAULT_MODEL) -> str:
    """Use LlamaIndex to analyze the entire database and answer questions.

    Args:
        question: Question about the database
        model: Ollama model to use (default: llama3.2)
    """
    try:
        # Get complete database schema and sample data
        schema_info = await get_database_schema()

        # Get sample data from all tables
        tables_query = "SELECT name FROM sqlite_master WHERE type='table'"
        tables = await db_manager.execute_query(tables_query)

        all_data = {}
        for table in tables:
            table_name = table["name"]
            sample_data = await db_manager.execute_query(f"SELECT * FROM {table_name} LIMIT 5")
            all_data[table_name] = sample_data

        # Create comprehensive context
        context = f"""
        Database Schema:
        {schema_info}
        
        Sample Data:
        {json.dumps(all_data, indent=2, default=str)}
        """

        # Use LlamaIndex for analysis
        prompt = f"""
        You are a database analyst with access to a SQLite database. 
        
        {context}
        
        Question: {question}
        
        Please provide a comprehensive analysis. If you suggest SQL queries, ensure they are SELECT statements only.
        Include insights, patterns, and recommendations based on the data.
        """

        response = await ollama_client.generate(model, prompt)
        return response
    except Exception as e:
        return f"Error analyzing database with LlamaIndex: {str(e)}"


@mcp.tool()
async def generate_sql_with_llamaindex(description: str, model: str = DEFAULT_MODEL) -> str:
    """Generate SQL queries using LlamaIndex based on natural language description.

    Args:
        description: Natural language description of what you want to query
        model: Ollama model to use (default: llama3.2)
    """
    try:
        # Get database schema
        schema_info = await get_database_schema()

        prompt = f"""
        You are a SQL expert. Given the following database schema, generate a SQL query based on the user's description.
        
        Database Schema:
        {schema_info}
        
        User Request: {description}
        
        Generate only a SELECT SQL query that fulfills the request. Do not include explanations, just the SQL query.
        Ensure the query is safe and only uses SELECT statements.
        """

        sql_query = await ollama_client.generate(model, prompt)

        # Clean up the response to extract just the SQL
        sql_query = sql_query.strip()
        if sql_query.startswith("```sql"):
            sql_query = sql_query[6:-3].strip()
        elif sql_query.startswith("```"):
            sql_query = sql_query[3:-3].strip()

        return f"Generated SQL Query:\n{sql_query}\n\nTo execute this query, use the query_database tool."
    except Exception as e:
        return f"Error generating SQL with LlamaIndex: {str(e)}"


async def main():
    """Main function to run the MCP server."""
    # Initialize database
    await db_manager.init_db()

    # Run the server
    await mcp.run_stdio_async()


if __name__ == "__main__":
    asyncio.run(main())
