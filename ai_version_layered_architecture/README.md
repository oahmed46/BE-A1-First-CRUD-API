# Tasks API

A small, in-memory CRUD API for managing tasks, built with **Python**,
**FastAPI**, and **uv**, using a **layered architecture**.

Data lives in memory (no database), so the task list resets to the three
example tasks every time the server restarts. This is meant as a
lightweight learning/demo project, not a production data store.

## Features

- Full CRUD for tasks: **C**reate, **R**ead, **U**pdate, **D**elete
- Layered architecture separating API, business logic, and data access
  (see below)
- Root (`/`) endpoint returning API metadata
- Health check endpoint (`/health`)
- Get all tasks, or filter by completion status (`/tasks?done=true`)
- Get a single task by id
- Partial updates on `PUT` — send `title`, `done`, or both
- Correct, consistent HTTP status codes throughout:
  - `200 OK` for successful reads/updates
  - `201 Created` for new tasks
  - `204 No Content` for successful deletes
  - `400 Bad Request` for any invalid client input — a missing/blank
    title, a `PUT` body with nothing to update, or a malformed request
    body
  - `404 Not Found` if a task id doesn't exist
- Auto-generated interactive API docs via FastAPI (Swagger UI & ReDoc)

## Architecture

The project follows a **layered architecture**, where each layer only
talks to the layer directly below it. This keeps business rules out of
the HTTP routes and out of storage, and means the in-memory "database"
could be swapped for a real one without touching the API or business
logic.

```
Request
   │
   ▼
┌───────────────────────────────────────────────┐
│ API layer            app/api/                 │  HTTP routes, request/response
│                                                 │  shaping. Thin — no business
│                                                 │  rules live here.
└───────────────────────────────────────────────┘
   │  calls
   ▼
┌───────────────────────────────────────────────┐
│ Service layer         app/services/            │  Business logic & validation
│                                                 │  rules (e.g. "title can't be
│                                                 │  blank"). Raises domain
│                                                 │  exceptions, knows nothing
│                                                 │  about HTTP.
└───────────────────────────────────────────────┘
   │  calls
   ▼
┌───────────────────────────────────────────────┐
│ Repository layer      app/repositories/        │  Data access. Owns the
│                                                 │  in-memory list today;
│                                                 │  could become a SQL/NoSQL
│                                                 │  repository tomorrow.
└───────────────────────────────────────────────┘
   │  operates on
   ▼
┌───────────────────────────────────────────────┐
│ Domain model           app/models/             │  Plain Python entity
│                                                 │  (Task) — no FastAPI or
│                                                 │  Pydantic dependency.
└───────────────────────────────────────────────┘
```

Supporting pieces:

- **`app/schemas/`** — Pydantic DTOs (`TaskCreate`, `TaskUpdate`,
  `TaskRead`) that define the public API contract. Kept separate from
  the domain model so the internal `Task` entity can evolve without
  breaking the API, and vice versa.
- **`app/exceptions.py`** — domain-level exceptions
  (`TaskNotFoundError`, `InvalidTaskDataError`, `NoUpdateFieldsError`)
  raised by the service layer. They carry no HTTP knowledge.
- **`app/main.py`** — builds the FastAPI app, includes the routers, and
  registers exception handlers that translate each domain exception (and
  FastAPI's own request-validation errors) into an HTTP response. This
  is the only place that maps business/validation errors to status
  codes.
- **`app/api/dependencies.py`** — FastAPI dependency providers. The
  `TaskRepository` is cached as a singleton so the same in-memory task
  list is shared across requests, and each request gets a fresh
  `TaskService` wrapping it.

### Why 400 instead of 422 for bad input?

By default, FastAPI returns `422 Unprocessable Entity` when a request
body fails Pydantic validation (e.g. a required field is missing). This
API overrides that behavior — via a `RequestValidationError` handler in
`app/main.py` — so malformed request bodies return `400 Bad Request`
instead, matching the same status code used for other input problems
like a blank task title or an empty `PUT` update. Note this applies API
wide, not only to `POST /tasks`, so error handling stays consistent
across every route.

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) for dependency and environment management

## Project setup

Dependencies are managed with `uv` (`fastapi` and `uvicorn[standard]`,
declared in `pyproject.toml` and pinned in `uv.lock`). To set the
project up:

```bash
uv sync
```

This creates a `.venv` with the exact dependency versions from the
lockfile.

## Running the API

```bash
uv run uvicorn app.main:app --reload
```

- `uv run` executes the command inside the project's virtual environment
  without needing to manually activate it.
- `app.main:app` points to the `app` FastAPI instance created in
  `app/main.py`.
- `--reload` restarts the server automatically when you edit the code
  (handy for development; drop it in production).

The API will be available at **http://127.0.0.1:8000**.

Interactive documentation is generated automatically:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- Raw OpenAPI schema: http://127.0.0.1:8000/openapi.json

## Data model

Each task looks like this:

```json
{
  "id": 1,
  "title": "Learn FastAPI",
  "done": true
}
```

The API starts pre-loaded with three example tasks:

| id | title               | done  |
|----|---------------------|-------|
| 1  | Learn FastAPI       | true  |
| 2  | Build a CRUD API    | false |
| 3  | Write documentation | false |

New task ids are generated automatically and always increase, even if
earlier tasks are deleted.

## Endpoints

### `GET /`
Returns metadata about the API: name, description, version, current task
count, and a map of available endpoints.

### `GET /health`
Health check. Returns `{"status": "ok"}`.

### `GET /tasks`
Returns the full list of tasks.

Optional query parameter:
- `done` (`true`/`false`) — filter tasks by completion status.

```bash
curl http://127.0.0.1:8000/tasks
curl "http://127.0.0.1:8000/tasks?done=false"
```

### `GET /tasks/{task_id}`
Returns a single task by id.

- `200 OK` with the task if found.
- `404 Not Found` if no task has that id.

```bash
curl http://127.0.0.1:8000/tasks/2
```

### `POST /tasks`
Creates a new task.

Request body:
```json
{
  "title": "Buy groceries",
  "done": false
}
```
`title` is required and must not be blank; `done` defaults to `false`
if omitted. The server assigns the `id`.

- `201 Created` with the newly created task.
- `400 Bad Request` if `title` is missing, blank, or the request body
  is otherwise malformed.

```bash
curl -X POST http://127.0.0.1:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries"}'
```

### `PUT /tasks/{task_id}`
Updates a task's `title` and/or `done` status. Only the fields you
include in the request body are changed — omitted fields are left as-is.

```bash
# Update just the title
curl -X PUT http://127.0.0.1:8000/tasks/2 \
  -H "Content-Type: application/json" \
  -d '{"title": "Build a robust CRUD API"}'

# Mark as done
curl -X PUT http://127.0.0.1:8000/tasks/2 \
  -H "Content-Type: application/json" \
  -d '{"done": true}'

# Update both at once
curl -X PUT http://127.0.0.1:8000/tasks/2 \
  -H "Content-Type: application/json" \
  -d '{"title": "Ship the CRUD API", "done": true}'
```

- `200 OK` with the updated task.
- `400 Bad Request` if the body doesn't contain `title` or `done`, or
  supplies a blank title.
- `404 Not Found` if no task has that id.

### `DELETE /tasks/{task_id}`
Deletes a task by id.

- `204 No Content` on success (empty body).
- `404 Not Found` if no task has that id.

```bash
curl -X DELETE http://127.0.0.1:8000/tasks/3
```

## Project structure

```
tasks-api/
├── app/
│   ├── main.py                    # App factory + exception handler registration
│   ├── core/
│   │   └── config.py              # App metadata/settings
│   ├── models/
│   │   └── task.py                # Domain entity (Task dataclass)
│   ├── schemas/
│   │   └── task.py                # Pydantic DTOs (TaskCreate/TaskUpdate/TaskRead)
│   ├── repositories/
│   │   └── task_repository.py     # Data access (in-memory storage)
│   ├── services/
│   │   └── task_service.py        # Business logic & validation rules
│   ├── exceptions.py              # Domain-level exceptions
│   └── api/
│       ├── dependencies.py        # DI providers (repository/service)
│       └── routes/
│           ├── meta.py            # / and /health routes
│           └── tasks.py           # /tasks CRUD routes
├── pyproject.toml                 # Project metadata and dependencies (managed by uv)
├── uv.lock                        # Locked dependency versions
├── .python-version                # Pinned Python version for uv
└── README.md
```

## Notes & limitations

- **In-memory storage**: all data is lost on restart. Because storage
  is isolated in `TaskRepository`, swapping in a real database (e.g.
  SQLite via SQLModel, or Postgres) means rewriting that one class —
  the service and API layers wouldn't need to change.
- **No auth**: there's no authentication/authorization layer — anyone
  who can reach the server can read and write all tasks.
- **Single process**: state lives in memory in the process that owns
  it. Running multiple worker processes (e.g. `--workers 4`) would give
  each worker its own separate task list. Stick to a single worker for
  this demo, or move to a shared database for multi-worker/production
  use.
