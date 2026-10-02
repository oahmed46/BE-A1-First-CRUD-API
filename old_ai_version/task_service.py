"""
Service layer — business logic.

Sits between the API layer and the repository layer. Routes never talk
to TaskRepository directly; they go through TaskService, which enforces
business rules (e.g. titles can't be blank, updates need at least one
field) and raises domain exceptions (see app/exceptions.py) when those
rules are violated.
"""

from typing import Optional

from app.exceptions import InvalidTaskDataError, NoUpdateFieldsError, TaskNotFoundError
from app.models.task import Task
from app.repositories.task_repository import TaskRepository


class TaskService:
    """Business logic for creating, reading, updating, and deleting tasks."""

    def __init__(self, repository: TaskRepository) -> None:
        self._repository = repository

    def list_tasks(self, done: Optional[bool] = None) -> list[Task]:
        """Return all tasks, optionally filtered by completion status."""
        tasks = self._repository.list_all()
        if done is None:
            return tasks
        return [t for t in tasks if t.done == done]

    def get_task(self, task_id: int) -> Task:
        """Return a single task by id.

        Raises:
            TaskNotFoundError: if no task with that id exists.
        """
        task = self._repository.get(task_id)
        if task is None:
            raise TaskNotFoundError(task_id)
        return task

    def create_task(self, title: str, done: bool) -> Task:
        """Create a new task.

        Raises:
            InvalidTaskDataError: if the title is blank.
        """
        clean_title = title.strip()
        if not clean_title:
            raise InvalidTaskDataError("Task title must not be empty.")
        return self._repository.add(title=clean_title, done=done)

    def update_task(
        self, task_id: int, title: Optional[str], done: Optional[bool]
    ) -> Task:
        """Update a task's title and/or done status. Omitted (None)
        fields are left unchanged.

        Raises:
            TaskNotFoundError: if no task with that id exists.
            NoUpdateFieldsError: if both title and done are None.
            InvalidTaskDataError: if a provided title is blank.
        """
        task = self.get_task(task_id)  # raises TaskNotFoundError

        if title is None and done is None:
            raise NoUpdateFieldsError()

        if title is not None:
            clean_title = title.strip()
            if not clean_title:
                raise InvalidTaskDataError("Task title must not be empty.")
            task.title = clean_title

        if done is not None:
            task.done = done

        return task

    def delete_task(self, task_id: int) -> None:
        """Delete a task by id.

        Raises:
            TaskNotFoundError: if no task with that id exists.
        """
        if not self._repository.delete(task_id):
            raise TaskNotFoundError(task_id)
