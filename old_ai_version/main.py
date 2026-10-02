"""
Application entrypoint.

Builds the FastAPI app, includes the API routers, and registers
exception handlers that translate domain-level exceptions (and
FastAPI's own request-validation errors) into the HTTP responses used
throughout this API. Business logic and storage live in the
services/repositories layers, not here.
"""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.routes import meta, tasks
from app.core.config import settings
from app.exceptions import InvalidTaskDataError, NoUpdateFieldsError, TaskNotFoundError


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.API_TITLE,
        description=settings.API_DESCRIPTION,
        version=settings.API_VERSION,
    )

    app.include_router(meta.router)
    app.include_router(tasks.router)

    register_exception_handlers(app)

    return app


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        # FastAPI/Pydantic raise this for malformed request bodies (e.g.
        # a missing required field). By default that maps to 422; this
        # API uses 400 Bad Request for all client-side input errors
        # instead, so the status code is consistent with the domain
        # validation errors below (e.g. a blank task title).
        return JSONResponse(status_code=400, content={"detail": exc.errors()})

    @app.exception_handler(TaskNotFoundError)
    async def task_not_found_handler(
        request: Request, exc: TaskNotFoundError
    ) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(InvalidTaskDataError)
    async def invalid_task_data_handler(
        request: Request, exc: InvalidTaskDataError
    ) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": exc.message})

    @app.exception_handler(NoUpdateFieldsError)
    async def no_update_fields_handler(
        request: Request, exc: NoUpdateFieldsError
    ) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": exc.message})


app = create_app()
