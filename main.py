from fastapi import FastAPI, HTTPException

app = FastAPI()

tasks: list(dict()) = [
    {"id": 1, "title": "Buy groceries", "done": False},
    {"id": 2, "title": "Walk the dog", "done": True},
    {"id": 3, "title": "Read a book", "done": False},
    ]


@app.get("/")
async def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks", "/health"]}


@app.get("/health")
async def read_health():
    return {"status": "ok"}


@app.get("/tasks")
async def read_tasks():
    return tasks


@app.get("/tasks/{id}")
async def read_task(id: int):
    for task in tasks:
        if task["id"] == id:
            return task
    raise HTTPException(status_code = 404, detail = f"error: Task {id} not found")