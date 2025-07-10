# Development Guide

## Quick Start

1. **Install dependencies:**
   ```bash
   make install
   # or
   uv sync
   ```

2. **Run tests:**
   ```bash
   make test
   # or
   uv run python -m pytest tests/ -v
   ```

3. **Run the server:**
   ```bash
   make run
   # or
   uv run python run_server.py
   ```

## Development Workflow

### Code Quality

We use several tools to maintain code quality:

- **Black**: Code formatting (120 character line length)
- **isort**: Import sorting (Black-compatible profile)
- **MyPy**: Static type checking
- **pytest**: Testing framework with async support

### Running Quality Checks

```bash
# Format code
make format

# Type checking
make type-check

# Run all linting
make lint

# Full development workflow
make dev
```

### Testing

```bash
# Run all tests
make test

# Run tests with coverage
make test-cov

# Run specific test file
uv run python -m pytest tests/test_database.py -v

# Run specific test
uv run python -m pytest tests/test_database.py::TestDatabaseManager::test_init_db -v
```

### VS Code Integration

The project includes comprehensive VS Code configuration:

- **Settings** (`.vscode/settings.json`): Python interpreter, formatting, linting
- **Tasks** (`.vscode/tasks.json`): Common development tasks
- **Launch** (`.vscode/launch.json`): Debug configurations
- **MCP Config** (`.vscode/mcp.json`): MCP server integration

#### Available VS Code Tasks

- `Ctrl+Shift+P` → "Tasks: Run Task" → Select from:
  - Run MCP Server
  - Run Tests
  - Run Tests with Coverage
  - Format Code
  - Sort Imports
  - Type Check
  - Install Dependencies
  - Run Examples

#### Debugging

Use `F5` or debug panel to run:
- Debug MCP Server
- Debug Client Examples
- Debug Tests

## Project Structure

```
src/mcp_simple_db_access/
├── __init__.py          # Package initialization
├── __main__.py          # CLI entry point
├── server.py            # Main server implementation
└── py.typed             # Type hint marker

tests/
├── conftest.py          # Test configuration and fixtures
├── test_database.py     # Database manager tests
├── test_ollama_client.py # Ollama client tests
├── test_tools.py        # MCP tools tests
├── test_integration.py  # Integration tests
└── test_examples.py     # Example validation tests

examples/
├── README.md            # Examples documentation
├── simple_client.py     # Basic usage example
├── client_example.py    # Comprehensive demo
└── llamaindex_example.py # Advanced AI features
```

## Adding New Features

### 1. Add a New MCP Tool

1. **Define the tool function in `server.py`:**
   ```python
   @mcp.tool()
   async def my_new_tool(param1: str, param2: int = 10) -> str:
       """Tool description for AI agents."""
       # Implementation
       return result
   ```

2. **Add tests in `tests/test_tools.py`:**
   ```python
   @pytest.mark.asyncio
   async def test_my_new_tool(self, populated_db):
       with patch.object(server, 'db_manager', populated_db):
           result = await server.my_new_tool("test", 5)
           assert "expected" in result
   ```

3. **Update integration tests in `tests/test_integration.py`**

4. **Add example usage in `examples/`**

### 2. Extend Database Schema

1. **Update `init_db()` method in `DatabaseManager`**
2. **Add migration logic if needed**
3. **Update sample data in `insert_sample_data()`**
4. **Add tests for new schema**

### 3. Add LlamaIndex Features

1. **Extend `OllamaLlamaIndexClient` class**
2. **Add new LLM interaction methods**
3. **Create tools that use the new features**
4. **Add comprehensive tests with mocking**

## Testing Strategy

### Unit Tests
- Test individual components in isolation
- Mock external dependencies (Ollama, file system)
- Fast execution, high coverage

### Integration Tests
- Test complete workflows
- Test MCP protocol integration
- Test tool interactions

### Example Tests
- Validate that examples work correctly
- Test import structure and basic functionality
- Ensure examples stay in sync with API changes

## CI/CD Pipeline

### GitHub Actions Workflow

The project includes a comprehensive CI/CD pipeline (`.github/workflows/ci.yml`):

1. **Testing Matrix**: Python 3.12 and 3.13
2. **Linting**: Black, isort, MyPy
3. **Security**: Bandit, Safety
4. **Coverage**: Codecov integration
5. **Example Validation**: Import and basic functionality checks
6. **Build**: Package building and artifact upload

### Local CI Simulation

```bash
# Run the full CI workflow locally
make ci
```

## Common Issues and Solutions

### 1. Import Errors

```bash
# Make sure PYTHONPATH includes src/
export PYTHONPATH="${PWD}/src:${PYTHONPATH}"

# Or use uv run which handles this automatically
uv run python -m pytest tests/
```

### 2. Ollama Connection Issues

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama if needed
ollama serve
```

### 3. Test Database Issues

Tests use temporary databases that are automatically cleaned up. If you see persistent issues:

```bash
# Clean up any leftover files
make clean
```

### 4. VS Code Integration Issues

1. **Select correct Python interpreter**: `Ctrl+Shift+P` → "Python: Select Interpreter" → Choose `.venv/bin/python`
2. **Reload window**: `Ctrl+Shift+P` → "Developer: Reload Window"
3. **Check Python path**: Ensure `PYTHONPATH` includes `src/`

## Performance Considerations

### Database Operations
- Use parameterized queries for security and performance
- Consider connection pooling for high-load scenarios
- Monitor query performance with SQLite EXPLAIN

### LLM Interactions
- Implement request timeouts (default: 60s)
- Consider caching for repeated queries
- Monitor token usage and costs

### Memory Management
- Large query results are streamed as JSON
- Temporary databases are properly cleaned up
- Async operations prevent blocking

## Security Guidelines

### Database Security
- Only SELECT queries allowed in `query_database` tool
- Parameterized queries prevent SQL injection
- File permissions restricted on database files

### LLM Security
- Input sanitization for prompts
- No sensitive data in LLM requests
- Timeout and error handling for external API calls

### Development Security
- Secrets in `.env` files (not committed)
- Security scanning in CI pipeline
- Regular dependency updates

## Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature-name`
3. **Make changes following the coding standards**
4. **Add tests for new functionality**
5. **Run the full test suite**: `make dev`
6. **Submit a pull request**

### Coding Standards

- Follow PEP 8 (enforced by Black)
- Use type hints for all functions
- Write docstrings for public functions
- Keep functions focused and testable
- Use async/await for I/O operations

### Pull Request Requirements

- [ ] All tests pass
- [ ] Code coverage maintained or improved
- [ ] Type checking passes
- [ ] Documentation updated
- [ ] Examples updated if API changes
- [ ] Changelog entry added (if applicable)
