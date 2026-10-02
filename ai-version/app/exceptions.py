"""
Domain-level exceptions.

The service layer raises these plain Python exceptions instead of
HTTPException, so it stays framework-agnostic. The API layer (see
app/main.py) registers handlers that translate each one into the
appropriate HTTP response.
"""


class TaskNotFoundError(Exception):
    """Raised when a task with the given id doesn't exist."""

    def __init__(self, task_id: int) -> None:
        self.task_id = task_id
        super().__init__(f"Task with id {task_id} not found")


class InvalidTaskDataError(Exception):
    """Raised when task data fails a business-rule validation
    (e.g. an empty/blank title)."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class NoUpdateFieldsError(Exception):
    """Raised when a PUT request supplies neither 'title' nor 'done'."""

    def __init__(self) -> None:
        self.message = "No fields provided to update. Supply 'title' and/or 'done'."
        super().__init__(self.message)
