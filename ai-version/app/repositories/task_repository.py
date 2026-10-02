"""
Repository layer — data access.

Owns storage and retrieval of Task entities using SQLite. The database
table and seed data are only created if they don't already exist, so
the same database can be used across multiple application runs without
data loss or duplication.
"""

import sqlite3
import os
from contextlib import contextmanager
from typing import Optional

from app.models.task import Task


# Database file location (relative to project root)
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "user-data", "tasks.db")


def _init_db(conn: sqlite3.Connection) -> None:
    """Create the tasks table and seed data if they don't already exist."""
    cursor = conn.cursor()
    
    # Create table only if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT 0
        )
    """)
    
    # Check if table already has data
    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]
    
    # Seed data only if table is empty
    if count == 0:
        cursor.executemany(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            [
                ("Learn FastAPI", 1),
                ("Build a CRUD API", 0),
                ("Write documentation", 0),
            ]
        )
        conn.commit()


class TaskRepository:
    """SQLite-backed storage for Task entities."""

    def __init__(self, db_path: str = DB_PATH) -> None:
        self.db_path = db_path
        self._init_connection()

    def _init_connection(self) -> None:
        """Initialize database connection and ensure schema exists."""
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        _init_db(self.conn)

    @contextmanager
    def _get_cursor(self):
        """Context manager for database operations."""
        cursor = self.conn.cursor()
        try:
            yield cursor
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise

    def _row_to_task(self, row: sqlite3.Row) -> Task:
        """Convert a database row to a Task object."""
        return Task(id=row["id"], title=row["title"], done=bool(row["done"]))

    def list_all(self) -> list[Task]:
        """Return all tasks."""
        with self._get_cursor() as cursor:
            cursor.execute("SELECT * FROM tasks ORDER BY id")
            return [self._row_to_task(row) for row in cursor.fetchall()]

    def get(self, task_id: int) -> Optional[Task]:
        """Return a single task by id, or None if it doesn't exist."""
        with self._get_cursor() as cursor:
            cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()
            return self._row_to_task(row) if row else None

    def add(self, title: str, done: bool) -> Task:
        """Create and store a new task."""
        with self._get_cursor() as cursor:
            cursor.execute(
                "INSERT INTO tasks (title, done) VALUES (?, ?)",
                (title, int(done))
            )
            return self.get(cursor.lastrowid)

    def delete(self, task_id: int) -> bool:
        """Remove a task by id. Returns True if it was found and removed."""
        with self._get_cursor() as cursor:
            cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            return cursor.rowcount > 0

    def count(self) -> int:
        """Return the current number of tasks."""
        with self._get_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM tasks")
            return cursor.fetchone()[0]
