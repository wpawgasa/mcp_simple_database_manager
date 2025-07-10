# MCP Simple DB Access - Development Makefile
# 
# Common development tasks for the MCP Simple DB Access Server project.
# Make sure you have uv installed: https://docs.astral.sh/uv/

.PHONY: install test test-cov format lint type-check clean run examples help

# Default target
help:
	@echo "Available targets:"
	@echo "  install     - Install dependencies"
	@echo "  test        - Run all tests"
	@echo "  test-cov    - Run tests with coverage report"
	@echo "  format      - Format code with black and isort"
	@echo "  lint        - Run all linting (format + type-check)"
	@echo "  type-check  - Run mypy type checking"
	@echo "  clean       - Clean up cache files"
	@echo "  run         - Run the MCP server"
	@echo "  examples    - Run example clients"
	@echo "  help        - Show this help message"

# Install dependencies
install:
	uv sync

# Run tests
test:
	uv run python -m pytest tests/ -v

# Run tests with coverage
test-cov:
	uv run python -m pytest tests/ --cov=src/mcp_simple_db_access --cov-report=html --cov-report=term-missing -v

# Format code
format:
	uv run black src/ tests/ examples/ --line-length=120
	uv run isort src/ tests/ examples/ --profile=black

# Type checking
type-check:
	uv run mypy src/

# Full linting pipeline
lint: format type-check

# Clean cache files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	rm -rf htmlcov/ 2>/dev/null || true
	rm -rf .coverage 2>/dev/null || true

# Run the MCP server
run:
	uv run python run_server.py

# Run example clients
examples:
	@echo "Running simple client example..."
	uv run python examples/simple_client.py
	@echo ""
	@echo "Running comprehensive client example..."
	uv run python examples/client_example.py
	@echo ""
	@echo "Running LlamaIndex example..."
	uv run python examples/llamaindex_example.py

# Development workflow
dev: clean format type-check test
	@echo "Development workflow completed successfully!"

# CI workflow
ci: install dev test-cov
	@echo "CI workflow completed!"

# Setup pre-commit hooks (if using git)
setup-hooks:
	@echo "Setting up git hooks..."
	@echo '#!/bin/bash' > .git/hooks/pre-commit
	@echo 'make lint' >> .git/hooks/pre-commit
	@chmod +x .git/hooks/pre-commit
	@echo "Pre-commit hook installed!"
