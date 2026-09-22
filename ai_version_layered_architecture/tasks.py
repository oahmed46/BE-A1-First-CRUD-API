"""
API layer — task routes.

Routes are intentionally thin: they parse/validate the HTTP request
(via Pydantic schemas), delegate to TaskService for all business logic,
and shape the result back into a response schema. They never touch
TaskRepository directly and never contain business rules themselves.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Response, status

from app.api.dependencies import get_task_service
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("", response_model=list[TaskRead])
def get_tasks(
    done: Optional[bool] = None,
    service: TaskService = Depends(get_task_service),
):
    """Return all tasks, optionally filtered with ?done=true/false."""
    return service.list_tasks(done)


@router.get("/{task_id}", response_model=TaskRead)
def get_task(task_id: int, service: TaskService = Depends(get_task_service)):
    """Return a single task by id, or 404 if it doesn't exist."""
    return service.get_task(task_id)


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: TaskCreate, service: TaskService = Depends(get_task_service)
):
    """Create a new task and return it, with a 201 Created status.

    Returns 400 Bad Request if the title is missing or blank.
    """
    return service.create_task(title=payload.title, done=payload.done)


@router.put("/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    service: TaskService = Depends(get_task_service),
):
    """Update a task's title and/or done status.

    Only fields present in the request body are changed. Returns 404
    if the task doesn't exist, or 400 if the body has no fields to
    update (or supplies a blank title).
    """
    update_data = payload.model_dump(exclude_unset=True)
    return service.update_task(
        task_id,
        title=update_data.get("title"),
        done=update_data.get("done"),
    )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, service: TaskService = Depends(get_task_service)):
    """Delete a task by id. Returns 204 on success, 404 if not found."""
    service.delete_task(task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
