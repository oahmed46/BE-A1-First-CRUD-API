"""
Domain model.

This module intentionally has no dependency on FastAPI or Pydantic — it
represents the core business entity, independent of how it's transported
over HTTP (that's the job of the schemas layer) or how it's persisted
(that's the job of the repository layer).
"""

from dataclasses import dataclass


@dataclass
class Task:
    """A single task in the system."""

    id: int
    title: str
    done: bool = False
