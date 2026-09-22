"""
Repository layer — data access.

Owns storage and retrieval of Task entities. Right now that storage is
just a Python list held in memory, but because everything above this
layer (service, API) only talks to TaskRepository's methods, the
in-memory list could be swapped for a real database (SQLite, Postgres,
etc.) without changing any other layer.
"""

from itertools import count
from typing import Optional

from app.models.task import Task


class TaskRepository:
    """In-memory storage for Task entities."""

    def __init__(self) -> None:
        # Seed data — three example tasks.
        self._tasks: list[Task] = [
            Task(id=1, title="Learn FastAPI", done=True),
            Task(id=2, title="Build a CRUD API", done=False),
            Task(id=3, title="Write documentation", done=False),
        ]
        # Generates new, always-increasing ids, continuing after the
        # seed data above even if earlier tasks are later deleted.
        self._id_counter = count(start=len(self._tasks) + 1)

    def list_all(self) -> list[Task]:
        """Return all tasks."""
        return list(self._tasks)

    def get(self, task_id: int) -> Optional[Task]:
        """Return a single task by id, or None if it doesn't exist."""
        return next((t for t in self._tasks if t.id == task_id), None)

    def add(self, title: str, done: bool) -> Task:
        """Create and store a new task, assigning it the next id."""
        task = Task(id=next(self._id_counter), title=title, done=done)
        self._tasks.append(task)
        return task

    def delete(self, task_id: int) -> bool:
        """Remove a task by id. Returns True if it was found and removed."""
        task = self.get(task_id)
        if task is None:
            return False
        self._tasks.remove(task)
        return True

    def count(self) -> int:
        """Return the current number of tasks."""
        return len(self._tasks)
