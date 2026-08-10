from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

tasks: list(dict()) = [
    {"id": 1, "title": "Buy groceries", "done": False},
    {"id": 2, "title": "Walk the dog", "done": True},
    {"id": 3, "title": "Read a book", "done": False},
    ]

class Task(BaseModel):
    id: int
    title: str
    done: bool


@app.get("/", description = "Retrieve API information")
async def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks", "/health"]}


@app.get("/health", description = "Verify API health")
async def read_health():
    return {"status": "ok"}


@app.get("/tasks", description = "Retrieve a list of tasks")
async def read_tasks():
    return tasks


@app.get("/tasks/{id}", description = "Retrieve a task from list of tasks")
async def read_task(id: int):
    for task in tasks:
        if task["id"] == id:
            return task
    raise HTTPException(status_code = 404, detail = f"error: Task {id} not found")


@app.post("/tasks", description = "Create a task from list of tasks")
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


@app.put("/tasks/{id}", description = "Update a task from list of tasks")
async def update_task(task: Task):
    for t in tasks:
        if t["id"] == task.id:
            if task.title is not None:
                t["title"] = task.title
            if task.done is not None:
                t["done"] = task.done
            return t
    raise HTTPException(status_code = 404, detail = f"error: Task {id} not found")


@app.delete("/tasks/{id}", description = "Delete a task from list of tasks")
async def delete_task(task: Task):
    for i, t in enumerate(tasks):
        if t["id"] == task.id:
            del tasks[i]
            raise HTTPException(status_code = 204)
    raise HTTPException(status_code = 404, detail = f"error: Task {task.id} not found")    
