from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

con = sqlite3.connect("tasks.db")

cur = con.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS tasks (
id INT AUTO_INCREMENT PRIMARY KEY, 
title VARCHAR(100) NOT NULL, 
done BOOL)""")

data = [
    (1, "Buy groceries", False),
    (2, "Walk the dog", True), 
    (3, "Read a book", False),
]
cur.executemany("""INSERT OR IGNORE INTO tasks VALUES(?, ?, ?)""", data)
con.commit()  

#cur.execute("""INSERT OR IGNORE INTO tasks (1, Buy groceries, False),
#(2, Walk the dog, True), 
#(3, Read a book, False)

# cur.execute("""INSERT OR IGNORE INTO tasks ("Buy groceries", False),
# (Walk the dog, True), 
# (Read a book, False)
# WHERE NOT EXISTS (SELECT * FROM tasks)
# """)

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


@app.get("/", description = "Returns metadata about the API.")
async def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks", "/health"]}


@app.get("/health", description = "Health check endpoint.")
async def read_health():
    return {"status": "ok"}


@app.get("/tasks", description = "Returns all tasks.")
async def read_tasks():
    return tasks


@app.get("/tasks/{id}", description = "Returns a single task by id.")
async def read_task(id: int):
    for task in tasks:
        if task["id"] == id:
            return task
    raise HTTPException(status_code = 404, detail = f"error: Task {id} not found")


@app.post("/tasks", description = "Creates a new task.")
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


@app.put("/tasks/{id}", description = "Updates a task's title and/or done. Send one or both fields; omitted fields stay unchanged.")
async def update_task(task: Task):
    for t in tasks:
        if t["id"] == task.id:
            if task.title is not None:
                t["title"] = task.title
            if task.done is not None:
                t["done"] = task.done
            return t
    raise HTTPException(status_code = 404, detail = f"error: Task {id} not found")


@app.delete("/tasks/{id}", description = "Deletes a task.")
async def delete_task(task: Task):
    for i, t in enumerate(tasks):
        if t["id"] == task.id:
            del tasks[i]
            raise HTTPException(status_code = 204)
    raise HTTPException(status_code = 404, detail = f"error: Task {task.id} not found")    
