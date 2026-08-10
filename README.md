# Task API

A simple Express CRUD API for managing tasks.

## Getting started

Install dependencies (ideally create a venv in project folder with uv):

```bash
uv sync
```

Start the server:

```bash
uv run fastapi dev
```

The API runs at `http://localhost:8000`.

OpenAPI docs (Swagger UI) are at [http://localhost:8000/docs](http://localhost:8000/docs). Open API spec lives in [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json)

## Endpoints

### `GET /`

Returns metadata about the API.

**Response**

```json
{
  "name": "Task API",
  "version": "1.0",
  "endpoints": ["/tasks"]
}
```

**Example**

```bash
curl http://localhost:8000/
```

### `GET /health`

Health check endpoint.

**Response**

```json
{
  "status": "ok"
}
```

**Example**

```bash
curl http://localhost:8000/health
```

### `GET /tasks`

Returns all tasks. 

**Response**

```json
[
  { "id": 1, "title": "Buy groceries", "done": false },
  { "id": 2, "title": "Walk the dog", "done": true },
  { "id": 3, "title": "Read a book", "done": false }
]
```

**Example**

```bash
curl http://localhost:8000/tasks
```

### `GET /tasks/:id`

Returns a single task by id.

**Response (200)**

```json
{ "id": 1, "title": "Buy groceries", "done": false }
```

**Response (404)**

```json
{ "error": "Task 99 not found" }
```

**Example**

```bash
curl http://localhost:8000/tasks/1
curl http://localhost:8000/tasks/99
```

### `POST /tasks`

Creates a new task.

**Request body**

```json
{ "title": "Buy milk" }
```

**Response (201)**

```json
{ "id": 4, "title": "Buy milk", "done": false }
```

**Response (400)**

```json
{ "error": "title is required and cannot be empty" }
```

**Example**

```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy milk"}'
```

### `PUT /tasks/:id`

Updates a task's `title` and/or `done`. Send one or both fields; omitted fields stay unchanged.

**Request body**

```json
{ "title": "Buy oat milk", "done": true }
```

**Response (200)**

```json
{ "id": 1, "title": "Buy oat milk", "done": true }
```

**Response (400)**

```json
{ "error": "request body must include title and/or done" }
```

**Response (404)**

```json
{ "error": "Task 99 not found" }
```

**Example**

```bash
curl -X PUT http://localhost:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"done": true}'
```

### `DELETE /tasks/:id`

Deletes a task.

**Response (204)**

Empty body — success, nothing to return.

**Response (404)**

```json
{ "error": "Task 99 not found" }
```

**Example**

```bash
curl -X DELETE http://localhost:8000/tasks/1
```

### AI vs ME

**Prompt**
Create a CRUD api using Python as the programming language. Use uv to initialize the venv and add the fastapi module as the api of choice. I want to store tasks in the python script, have three example ones with id, title, and done. The root should display metadata about the API, health should get a status of ok, get tasks will return the tasks data and with another get you can also specify which id we want to get for a single task. post tasks will create a new task, put task by id will update the task title and/or done, delete task by id will delete the specific task. Incorporate proper HTTP responses such as 204 and 404. Add any extra features you think would fit the scope of this project. Document your work in a README.md

Code lives in /ai-version - improvements for pyproject.toml and .gitignore added to my work

I believe my approach was well thought out, since the AI response is quite similar but has extra functionality added (such as separating the create and update models). Now I am aware there is a lot of documentation improvements that can be made, such as describing the fields in the models. 

Also learned about next() which can retrieve the next item from an iterator, meaning we can search for every value within the criteria and only return the first one.

Using a counter that tracks the largest id is better than my approach of iterating through the entire tasks list and finding the largest value, which would be O(n) compared to the counters O(1) approach. The decorator can have a status code, instead of raising an HTTP Exception to get the code I want.

The AI also added extra features, such as filtering if a task is done or not.

The only mistake/correction to be made I found is when we POST /tasks using a string with nothing in it ("") we recieve a 422 error - I did not specify it had to be 400 so it used this isntead.