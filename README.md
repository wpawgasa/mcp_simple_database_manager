# MCP Simple DB Access Server

A Model Context Protocol (MCP) server that provides database access capabilities with local LLM integration via Ollama and LlamaIndex.

## Features

- **Database Operations**: SQLite database management with async support
- **LLM Integration**: Local AI capabilities using Ollama via LlamaIndex
- **Data Analysis**: Intelligent data analysis and querying
- **SQL Generation**: Natural language to SQL conversion
- **Schema Management**: Database schema inspection and table creation

## Dependencies

- Python 3.12+
- [MCP SDK](https://github.com/modelcontextprotocol/python-sdk) - Model Context Protocol
- [LlamaIndex](https://www.llamaindex.ai/) - LLM framework
- [Ollama](https://ollama.ai/) - Local LLM runtime
- aiosqlite - Async SQLite support
- httpx - HTTP client

## Installation

1. **Prerequisites**: Install [Ollama](https://ollama.ai/) and pull a model:
   ```bash
   # Install Ollama (follow instructions at https://ollama.ai/)
   ollama pull llama3.2
   ```

2. **Install dependencies**:
   ```bash
   uv install
   ```

## Usage

### Running the Server

```bash
# Direct execution
python run_server.py

# Or via uv
uv run python run_server.py
```

### Available Tools

1. **query_database** - Execute SELECT queries on the database
2. **insert_sample_data** - Insert sample data for testing
3. **analyze_data_with_llm** - Analyze table data using LLM
4. **chat_with_ollama** - General chat with local LLM
5. **list_ollama_models** - List available Ollama models
6. **get_database_schema** - Get complete database schema
7. **create_table** - Create new database tables
8. **chat_with_context** - Chat with additional context (LlamaIndex)
9. **analyze_database_with_llamaindex** - Comprehensive database analysis
10. **generate_sql_with_llamaindex** - Natural language to SQL generation

### VS Code Integration

The server can be configured for use with VS Code and MCP-compatible clients:

1. Create `.vscode/mcp.json`:
   ```json
   {
     "servers": {
       "mcp-simple-db-access": {
         "type": "stdio",
         "command": "uv",
         "args": ["run", "python", "run_server.py"]
       }
     }
   }
   ```

2. Use with Claude Desktop or other MCP clients by adding to your configuration.

#### VS Code Development Setup

For optimal VS Code development experience:

1. **Extensions**: Install the Python extension and enable the following settings:
   ```json
   {
     "python.defaultInterpreterPath": "./.venv/bin/python",
     "python.formatting.provider": "black",
     "python.formatting.blackArgs": ["--line-length", "120"],
     "python.sortImports.args": ["--profile", "black"],
     "python.linting.enabled": true,
     "python.linting.mypyEnabled": true
   }
   ```

2. **Tasks**: Create `.vscode/tasks.json` for quick development tasks:
   ```json
   {
     "version": "2.0.0",
     "tasks": [
       {
         "label": "Format Code",
         "type": "shell",
         "command": "uv run black src/ && uv run isort src/",
         "group": "build",
         "presentation": {
           "echo": true,
           "reveal": "silent"
         }
       },
       {
         "label": "Run Tests",
         "type": "shell",
         "command": "uv run pytest",
         "group": "test",
         "presentation": {
           "echo": true,
           "reveal": "always"
         }
       },
       {
         "label": "Type Check",
         "type": "shell",
         "command": "uv run mypy src/",
         "group": "build",
         "presentation": {
           "echo": true,
           "reveal": "always"
         }
       }
     ]
   }
   ```

3. **Launch Configuration**: Create `.vscode/launch.json` for debugging:
   ```json
   {
     "version": "0.2.0",
     "configurations": [
       {
         "name": "Debug MCP Server",
         "type": "python",
         "request": "launch",
         "program": "run_server.py",
         "console": "integratedTerminal",
         "cwd": "${workspaceFolder}",
         "env": {
           "PYTHONPATH": "${workspaceFolder}/src"
         }
       }
     ]
   }
   ```

## Architecture

### LlamaIndex Integration

The server uses LlamaIndex for enhanced LLM capabilities:

- **Ollama LLM**: Direct integration with local Ollama models
- **Async Support**: Non-blocking AI operations
- **Context Management**: Intelligent context handling for better responses
- **Schema-Aware**: Database-aware AI responses

### Database Structure

The server creates sample tables:
- `users` - User information
- `products` - Product catalog
- `orders` - Order records with relationships

### Security

- Only SELECT queries allowed for general querying
- Parameterized queries to prevent SQL injection
- Input validation for all operations

## Development

### Project Structure

```
src/mcp_simple_db_access/
├── __init__.py          # Package initialization
├── __main__.py          # Module entry point
├── server.py            # Main server implementation
└── py.typed             # Type hints marker

run_server.py            # CLI entry point
data/                    # SQLite database storage
.github/copilot-instructions.md  # Copilot guidance
```

### Development Tools

This project includes several development tools configured in `pyproject.toml`:

#### Code Formatting and Quality

```bash
# Format code with Black (120 character line length)
uv run black src/

# Sort imports with isort
uv run isort src/

# Type check with MyPy
uv run mypy src/

# Run all formatting and checks
uv run black src/ && uv run isort src/ && uv run mypy src/
```

#### Testing

```bash
# Run all tests
uv run pytest

# Run tests with verbose output
uv run pytest -v

# Run tests with coverage
uv run pytest --cov=src/mcp_simple_db_access

# Run async tests specifically
uv run pytest -k "async"
```

#### Development Dependencies

Install development dependencies:

```bash
# Install all dependencies including dev extras
uv sync --extra dev

# Or install just the project in development mode
uv install -e .
```

#### Pre-commit Setup

For consistent code quality, run before committing:

```bash
#!/bin/bash
# format_and_check.sh
set -e

echo "Formatting code with Black..."
uv run black src/

echo "Sorting imports with isort..."
uv run isort src/

echo "Type checking with MyPy..."
uv run mypy src/

echo "Running tests..."
uv run pytest

echo "All checks passed!"
```

### Contributing

1. Follow the existing code patterns
2. Use async/await for all I/O operations
3. Add proper error handling and logging
4. Test with multiple Ollama models
5. Update documentation for new features
6. Run formatting and type checking before committing:
   ```bash
   uv run black src/ && uv run isort src/ && uv run mypy src/ && uv run pytest
   ```

## Examples

This project includes comprehensive client examples in the `examples/` directory:

### Quick Start Examples

```bash
# Simple client demonstration
python examples/simple_client.py

# Interactive client with all features
python examples/client_example.py

# Interactive mode for manual testing
python examples/client_example.py --interactive

# Advanced LlamaIndex features
python examples/llamaindex_example.py
```

### Example Outputs

### Basic Database Query
```python
# Via MCP client
result = await session.call_tool("query_database", {
    "sql": "SELECT * FROM users LIMIT 5"
})
```

### AI-Powered Analysis
```python
# Analyze data with LlamaIndex
result = await session.call_tool("analyze_database_with_llamaindex", {
    "question": "What are the sales trends in our product data?"
})
```

### SQL Generation
```python
# Generate SQL from natural language
result = await session.call_tool("generate_sql_with_llamaindex", {
    "description": "Show me the top 5 customers by total order value"
})
```

See the [`examples/README.md`](examples/README.md) for detailed documentation and troubleshooting guides.

## License

MIT License - see LICENSE file for details.

## Related Projects

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [LlamaIndex](https://www.llamaindex.ai/)
- [Ollama](https://ollama.ai/)