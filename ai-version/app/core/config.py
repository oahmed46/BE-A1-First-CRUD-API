"""
Application configuration.

A single place for app-wide metadata/settings, kept separate so it can
be extended later (e.g. reading from environment variables) without
touching the rest of the codebase.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    API_TITLE: str = "Tasks API"
    API_DESCRIPTION: str = (
        "A simple SQLite-backed CRUD API for managing tasks, "
        "built with a layered architecture."
    )
    API_VERSION: str = "1.2.0"


settings = Settings()
