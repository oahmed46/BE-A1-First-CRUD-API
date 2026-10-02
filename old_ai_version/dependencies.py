"""
Dependency providers for FastAPI's dependency-injection system.

get_task_repository is cached so the same TaskRepository instance (and
therefore the same in-memory task list) is reused across requests,
rather than being reset on every call.
"""

from functools import lru_cache

from app.repositories.task_repository import TaskRepository
from app.services.task_service import TaskService


@lru_cache
def get_task_repository() -> TaskRepository:
    return TaskRepository()


def get_task_service() -> TaskService:
    return TaskService(get_task_repository())
