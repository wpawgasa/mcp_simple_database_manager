"""
Tests for DatabaseManager class.
"""

import pytest
import json
from mcp_simple_db_access.server import DatabaseManager


class TestDatabaseManager:
    """Test cases for DatabaseManager functionality."""

    @pytest.mark.asyncio
    async def test_init_db(self, temp_db):
        """Test database initialization creates all required tables."""
        db_manager = DatabaseManager(temp_db)
        await db_manager.init_db()

        # Check that all tables were created
        tables = await db_manager.execute_query("SELECT name FROM sqlite_master WHERE type='table'")
        table_names = [table["name"] for table in tables]

        assert "users" in table_names
        assert "products" in table_names
        assert "orders" in table_names

    @pytest.mark.asyncio
    async def test_execute_query_select(self, populated_db):
        """Test executing SELECT queries."""
        # Test basic SELECT
        result = await populated_db.execute_query("SELECT * FROM users")
        assert len(result) == 2
        assert result[0]["name"] == "Test User 1"
        assert result[1]["name"] == "Test User 2"

        # Test SELECT with WHERE clause
        result = await populated_db.execute_query("SELECT * FROM users WHERE age > ?", (25,))
        assert len(result) == 1
        assert result[0]["name"] == "Test User 2"

    @pytest.mark.asyncio
    async def test_execute_query_empty_result(self, populated_db):
        """Test query that returns no results."""
        result = await populated_db.execute_query("SELECT * FROM users WHERE age > 100")
        assert result == []

    @pytest.mark.asyncio
    async def test_execute_write_insert(self, db_manager):
        """Test INSERT operations."""
        # Insert a user
        rows_affected = await db_manager.execute_write(
            "INSERT INTO users (name, email, age) VALUES (?, ?, ?)", ("New User", "new@example.com", 35)
        )
        assert rows_affected == 1

        # Verify the user was inserted
        result = await db_manager.execute_query("SELECT * FROM users WHERE email = ?", ("new@example.com",))
        assert len(result) == 1
        assert result[0]["name"] == "New User"

    @pytest.mark.asyncio
    async def test_execute_write_update(self, populated_db):
        """Test UPDATE operations."""
        # Update a user's age
        rows_affected = await populated_db.execute_write("UPDATE users SET age = ? WHERE name = ?", (26, "Test User 1"))
        assert rows_affected == 1

        # Verify the update
        result = await populated_db.execute_query("SELECT age FROM users WHERE name = ?", ("Test User 1",))
        assert result[0]["age"] == 26

    @pytest.mark.asyncio
    async def test_execute_write_delete(self, populated_db):
        """Test DELETE operations."""
        # Delete a user
        rows_affected = await populated_db.execute_write("DELETE FROM users WHERE name = ?", ("Test User 1",))
        assert rows_affected == 1

        # Verify the user was deleted
        result = await populated_db.execute_query("SELECT * FROM users WHERE name = ?", ("Test User 1",))
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_foreign_key_constraint(self, populated_db):
        """Test that foreign key relationships work correctly."""
        # Get order data with JOIN
        result = await populated_db.execute_query(
            """
            SELECT o.id, u.name as user_name, p.name as product_name, o.quantity
            FROM orders o
            JOIN users u ON o.user_id = u.id
            JOIN products p ON o.product_id = p.id
        """
        )

        assert len(result) == 1
        assert result[0]["user_name"] == "Test User 1"
        assert result[0]["product_name"] == "Test Product 1"
        assert result[0]["quantity"] == 2

    @pytest.mark.asyncio
    async def test_transaction_rollback(self, db_manager):
        """Test that transactions work correctly on errors."""
        # This should work
        await db_manager.execute_write(
            "INSERT INTO users (name, email, age) VALUES (?, ?, ?)", ("User 1", "user1@example.com", 25)
        )

        # This should fail due to unique constraint on email
        with pytest.raises(Exception):
            await db_manager.execute_write(
                "INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
                ("User 2", "user1@example.com", 30),  # Same email
            )

        # Verify only the first user was inserted
        result = await db_manager.execute_query("SELECT * FROM users")
        assert len(result) == 1
        assert result[0]["name"] == "User 1"

    @pytest.mark.asyncio
    async def test_parameterized_queries_prevent_injection(self, db_manager):
        """Test that parameterized queries prevent SQL injection."""
        # Insert a user first
        await db_manager.execute_write(
            "INSERT INTO users (name, email, age) VALUES (?, ?, ?)", ("Test User", "test@example.com", 25)
        )

        # Try a potential SQL injection (should be treated as literal string)
        malicious_input = "'; DROP TABLE users; --"
        result = await db_manager.execute_query("SELECT * FROM users WHERE name = ?", (malicious_input,))

        # Should return no results (not execute the DROP)
        assert len(result) == 0

        # Verify users table still exists
        tables = await db_manager.execute_query("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        assert len(tables) == 1

    @pytest.mark.asyncio
    async def test_row_factory_returns_dict(self, populated_db):
        """Test that queries return dictionary-like rows."""
        result = await populated_db.execute_query("SELECT * FROM users LIMIT 1")

        assert len(result) == 1
        row = result[0]

        # Should be able to access columns by name
        assert "id" in row
        assert "name" in row
        assert "email" in row
        assert "age" in row

        # Should be a dictionary
        assert isinstance(row, dict)
