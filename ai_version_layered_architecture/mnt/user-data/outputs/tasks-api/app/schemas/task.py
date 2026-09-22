"""
API schemas (DTOs).

These Pydantic models define the shape of data crossing the HTTP
boundary — what clients send us and what we send back. They're kept
separate from the domain model (`app.models.task.Task`) so the internal
representation of a task is free to evolve independently of the public
API contract.
"""

from typing import Optional

from pydantic import BaseModel, Field


class TaskRead(BaseModel):
    """Representation of a task returned to clients."""

    id: int
    title: str
    done: bool

    model_config = {"from_attributes": True}


class TaskCreate(BaseModel):
    """Payload for creating a new task.

    Note: title emptiness is validated in the service layer (not here)
    so that "title is blank" produces a 400 response consistent with
    the rest of the API's error handling, rather than a framework-level
    422.
    """

    title: str = Field(..., description="The task title")
    done: bool = Field(False, description="Whether the task is already done")


class TaskUpdate(BaseModel):
    """Payload for updating an existing task.

    All fields are optional so a client can update just the title, just
    the done flag, or both.
    """

    title: Optional[str] = Field(None, description="New title")
    done: Optional[bool] = Field(None, description="New done state")
