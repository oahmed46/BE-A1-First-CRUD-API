# Tasks API

A simple SQLite-backed CRUD API for managing tasks, built with a layered architecture.

## Architecture

The project follows a clean layered architecture:

- **API Layer** (`app/api/`): Routes, schemas (DTOs), and dependency providers
- **Service Layer** (`app/services/`): Business logic and validation
- **Repository Layer** (`app/repositories/`): Data access and persistence
- **Domain Models** (`app/models/`): Core business entities
- **Core** (`app/core/`): Configuration and shared utilities

## Storage

The API uses SQLite for persistence. The database file is created at `user-data/tasks.db` and:

- The `tasks` table is only created if it doesn't already exist
- Seed data (3 example tasks) is only added if the table is empty
- This ensures data persistence across application restarts

## Getting Started

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Run the server:
   ```bash
   uv run uvicorn main:app --reload
   ```

3. Visit the API documentation at http://localhost:8000/docs

## API Endpoints

- `GET /` - API metadata
- `GET /health` - Health check
- `GET /tasks` - List all tasks (optional `?done=` filter)
- `GET /tasks/{id}` - Get a single task by id
- `POST /tasks` - Create a new task
- `PUT /tasks/{id}` - Update a task's title and/or done status
- `DELETE /tasks/{id}` - Delete a task

## AI vs Me

### Initial Prompt
Create a CRUD API using Python as the programming language. Use uv to initialize the venv and add the fastapi module as the API of choice. Store tasks in the Python script with three example ones (id, title, and done). The root should display metadata about the API, health should return status ok, get tasks will return the tasks data, and another get endpoint retrieves a single task by ID. POST tasks creates a new task, PUT task by ID updates the task title and/or done status, DELETE task by ID deletes the specific task. Incorporate proper HTTP responses such as 204 and 404. Add any extra features you think would fit the scope of this project. Document your work in a README.md.

### Second Prompt
Refactor project to use layered architecture system design instead of having everything in a main.py file. Also change POST /tasks to use 400 error instead of 422.

### Third Prompt
Update the project to move from in-memory to using SQLite. Ensure the table and seeded data respectively are only added if missing. Everything else should be the same.

---

## Comparison: My Version vs AI Version

### My Version (my_attempt/)

**Architecture:**
- Single-file approach — all code in `main.py`
- No separation of concerns
- Database initialization runs at module load time

**Storage:**
- SQLite database (`tasks.db` in project root)
- Table created with `CREATE TABLE IF NOT EXISTS`
- Seed data uses `INSERT OR IGNORE` with explicit IDs (1, 2, 3)
- **Issue:** Explicit ID insertion can cause conflicts if database is re-initialized

**Code Quality:**
- Database connections opened and closed in every request (inefficient)
- No connection pooling or reuse
- Error handling with try/except blocks in every endpoint
- Uses `HTTPException` directly in business logic (mixes concerns)
- Manual ID generation by querying for largest ID (O(n) operation)
- Validation done inline in endpoints rather than centralized

**Features:**
- Basic CRUD operations
- Proper HTTP status codes (201, 204, 404, 400)
- Seed data: "Buy groceries", "Walk the dog", "Read a book"

**Weaknesses:**
- Tight coupling between API layer and database layer
- No business logic layer — validation and logic mixed in routes
- Connection management is fragile (what if `con` is undefined on error?)
- No dependency injection
- No separation of schemas (single Task model used for both input and output)
- String conversion of IDs in SQL queries (`str(id)`) is unnecessary

---

### AI Version (ai-version/)

**Architecture:**
- Clean layered architecture with 5 distinct layers
- Separation of concerns: API → Service → Repository → Model
- Dependency injection via FastAPI's `Depends()` system
- Cached repository instance (single connection per app lifecycle)

**Storage:**
- SQLite database (`user-data/tasks.db`)
- Table created with `CREATE TABLE IF NOT EXISTS`
- Seed data only added if table is empty (checked via `SELECT COUNT(*)`)
- Proper transaction management with context manager and rollback
- Auto-incrementing IDs (no manual ID management)

**Code Quality:**
- Domain exceptions (`TaskNotFoundError`, `InvalidTaskDataError`, etc.) keep business logic framework-agnostic
- Exception handlers in `main.py` translate domain exceptions to HTTP responses
- Repository pattern abstracts database operations
- Service layer enforces business rules (blank title validation, update field requirements)
- Pydantic schemas separate input (`TaskCreate`, `TaskUpdate`) from output (`TaskRead`)
- Connection reused across requests via `@lru_cache`
- Context manager ensures proper commit/rollback

**Features:**
- All CRUD operations from my version
- **Added:** `?done=` filter on `GET /tasks` endpoint
- **Added:** Proper validation for blank titles (returns 400, not 422)
- **Added:** Validation that PUT requests include at least one field to update
- **Added:** Comprehensive API documentation via FastAPI auto-docs
- **Added:** Config module for centralized settings
- **Added:** Detailed README with architecture explanation

**Strengths:**
- Scalable architecture — easy to swap SQLite for PostgreSQL
- Testable — each layer can be unit tested independently
- Maintainable — changes to one layer don't affect others
- Professional error handling with consistent HTTP status codes
- No code duplication — shared logic in service layer
- Proper resource management (cached connections, context managers)

---

## Key Improvements in AI Version

| Aspect | My Version | AI Version | Why Better |
|--------|-----------|------------|------------|
| **Architecture** | Single file | 5-layer architecture | Separation of concerns, testability |
| **Database Connections** | New connection per request | Cached single connection | Performance, resource efficiency |
| **ID Generation** | Query for max ID (O(n)) | Auto-increment (O(1)) | Better performance |
| **Validation** | Inline in routes | Centralized in service layer | DRY, consistent |
| **Error Handling** | HTTPException everywhere | Domain exceptions + handlers | Framework-agnostic business logic |
| **Schemas** | Single model | Separate Create/Update/Read models | Proper API contract |
| **Seed Data** | INSERT OR IGNORE with explicit IDs | Conditional insert if empty | No conflicts, cleaner |
| **Extra Features** | None | `?done=` filter, better validation | More useful API |

## What I Learned

1. **Layered Architecture:** Separating concerns into API, Service, Repository, and Model layers makes code more maintainable and testable.

2. **Dependency Injection:** FastAPI's `Depends()` system with `@lru_cache` provides efficient resource management without global state.

3. **Domain Exceptions:** Using custom exceptions keeps business logic framework-agnostic, making it easier to test and swap implementations.

4. **Connection Management:** Reusing database connections via caching is significantly more efficient than creating new connections per request.

5. **ID Generation:** Auto-incrementing IDs are simpler and more efficient than querying for the maximum ID.

6. **Schema Separation:** Using different Pydantic models for input and output provides better API contracts and validation.

7. **Context Managers:** Using context managers for database operations ensures proper transaction handling (commit on success, rollback on error).

## Areas for Further Improvement

- Add database migrations system (e.g., Alembic)
- Add authentication/authorization
- Add pagination for large task lists
- Add logging
- Add unit and integration tests
- Add environment configuration (`.env` files)
- Add Docker support
- Add CI/CD pipeline 
