from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

tasks: list(dict()) = [
    {"id": 1, "title": "Buy groceries", "done": False},
    {"id": 2, "title": "Walk the dog", "done": True},
    {"id": 3, "title": "Read a book", "done": False},
    ]

class Task(BaseModel):
    title: str


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


@app.post("/tasks")
async def create_task(task: Task):
    if task.title is None or "":
        raise HTTPException(status_code = 400, detail = "title is required and cannot be empty")
    largest_id = 0
    for t in tasks:
        if t["id"] > largest_id:
            largest_id = t["id"]
    largest_id += 1
    new_task = {"id": largest_id, "title": task.title, "done": False}
    tasks.append(new_task)
    raise HTTPException(status_code= 201, detail = new_task)
