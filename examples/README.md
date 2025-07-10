# MCP Simple DB Access - Client Examples

This directory contains example client scripts that demonstrate how to interact with the MCP Simple DB Access server.

## Prerequisites

1. **Ollama Setup**: Make sure Ollama is installed and running with a model:
   ```bash
   # Install Ollama (if not already installed)
   # Follow instructions at https://ollama.ai/
   
   # Pull a model
   ollama pull llama3.2
   
   # Verify Ollama is running
   ollama list
   ```

2. **Dependencies**: Install the project dependencies:
   ```bash
   cd ..  # Go to project root
   uv sync --extra dev
   ```

## Examples

### 1. Simple Client (`simple_client.py`)

A minimal example demonstrating basic MCP operations.

**Features:**
- Connect to MCP server
- Insert sample data
- Query database
- Basic Ollama chat

**Usage:**
```bash
python examples/simple_client.py
```

**Expected Output:**
```
Connecting to MCP Server...
Connected!

1. Inserting sample data...
   Sample data inserted successfully!

2. Querying users...
   - John Doe (john@example.com)
   - Jane Smith (jane@example.com)

3. Getting database schema...
   Found 3 tables: users, products, orders

4. Testing Ollama integration...
   Ollama says: MCP stands for Model Context Protocol...

✅ Simple example completed!
```

### 2. Interactive Client (`client_example.py`)

A comprehensive example with both automated demos and interactive mode.

**Features:**
- Automated demonstration of all tools
- Interactive mode for manual testing
- Error handling and user-friendly output

**Usage:**

**Automated Demo:**
```bash
python examples/client_example.py
```

**Interactive Mode:**
```bash
python examples/client_example.py --interactive
```

**Interactive Commands:**
- `help` - Show available commands
- `list` - List all MCP tools
- `schema` - Show database schema
- `users` - Show users table
- `models` - List Ollama models
- `chat <message>` - Chat with Ollama
- `sql <query>` - Execute SQL query (SELECT only)
- `quit` - Exit

### 3. LlamaIndex Advanced Example (`llamaindex_example.py`)

Advanced example showcasing AI-powered database analysis and SQL generation.

**Features:**
- Natural language to SQL conversion
- AI-powered database analysis
- Context-aware conversations
- Business insights generation

**Usage:**
```bash
python examples/llamaindex_example.py
```

**What it demonstrates:**
- Generating SQL from natural language descriptions
- Comprehensive database analysis using AI
- Context-aware conversations about data
- Business insights from database statistics

## Troubleshooting

### Common Issues

1. **"Connection refused" or server not starting:**
   - Make sure you're in the correct directory
   - Check that all dependencies are installed: `uv sync --extra dev`
   - Verify the server script exists: `ls -la run_server.py`

2. **Ollama-related errors:**
   - Ensure Ollama is running: `ollama list`
   - Check if the model exists: `ollama pull llama3.2`
   - Try a different model by modifying the `model` parameter

3. **Import errors:**
   - Make sure you're running from the project root
   - Check that the MCP SDK is installed: `uv pip list | grep mcp`

4. **Database errors:**
   - The database is created automatically in the `data/` directory
   - If you encounter issues, try deleting `data/app.db` to reset

### Debug Mode

To run examples with more verbose output, you can modify the scripts to include debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Customizing Examples

### Using Different Models

To use a different Ollama model, modify the `model` parameter in the tool calls:

```python
result = await session.call_tool("chat_with_ollama", {
    "prompt": "Your message here",
    "model": "llama2"  # Change this to your preferred model
})
```

### Adding Custom Queries

You can extend the examples with your own SQL queries and analysis questions:

```python
# Add to any example
custom_queries = [
    "SELECT COUNT(*) FROM products WHERE price > 100",
    "SELECT category, COUNT(*) FROM products GROUP BY category"
]

for query in custom_queries:
    result = await session.call_tool("query_database", {"sql": query})
    print(f"Query: {query}")
    print(f"Result: {result.content[0].text}")
```

### Error Handling

All examples include basic error handling, but you can enhance it:

```python
try:
    result = await session.call_tool("tool_name", parameters)
    # Handle success
except Exception as e:
    print(f"Detailed error: {type(e).__name__}: {e}")
    # Handle specific error types
```

## Next Steps

After running these examples, you can:

1. **Create your own client** based on these templates
2. **Integrate with your applications** using the MCP protocol
3. **Extend the server** with additional tools and capabilities
4. **Build web interfaces** or CLI tools using the MCP client patterns

For more information about the MCP protocol, visit: https://modelcontextprotocol.io/
