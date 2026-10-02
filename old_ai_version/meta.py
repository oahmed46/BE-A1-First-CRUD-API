"""
API layer — metadata routes (root and health check).
"""

from fastapi import APIRouter, Depends

from app.api.dependencies import get_task_service
from app.core.config import settings
from app.services.task_service import TaskService

router = APIRouter(tags=["Meta"])


@router.get("/")
def read_root(service: TaskService = Depends(get_task_service)):
    """Root endpoint — returns metadata about the API."""
    return {
        "name": settings.API_TITLE,
        "description": settings.API_DESCRIPTION,
        "version": settings.API_VERSION,
        "task_count": len(service.list_tasks()),
        "docs": "/docs",
        "endpoints": {
            "GET /health": "Health check",
            "GET /tasks": "List all tasks (optional ?done= filter)",
            "GET /tasks/{id}": "Get a single task by id",
            "POST /tasks": "Create a new task",
            "PUT /tasks/{id}": "Update a task's title and/or done status",
            "DELETE /tasks/{id}": "Delete a task",
        },
    }


@router.get("/health")
def health_check():
    """Simple health check endpoint."""
    return {"status": "ok"}
