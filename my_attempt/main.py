from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

try: 
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

except sqlite3.Error as error:
    print("Error occured -", error)

finally:
    if con:
        con.close()

app = FastAPI()

class TaskCreate(BaseModel):
     title: str
     done: bool = False

class Task(TaskCreate):
    id: int


@app.get("/", description = "Returns metadata about the API.")
async def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks", "/health"]}


@app.get("/health", description = "Health check endpoint.")
async def read_health():
    return {"status": "ok"}


@app.get("/tasks", description = "Returns all tasks.")
async def read_tasks():
    try:
        con = sqlite3.connect("tasks.db")
        cur = con.cursor()
        cur.execute("SELECT * FROM tasks")
        rows = cur.fetchall()

        tasks_list = [{"id": row[0], "title": row[1], "done": row[2]} for row in rows]
        return tasks_list

    except sqlite3.Error as error:
        raise HTTPException(status_code= 500, detail = error)
    finally:
        if con:
            con.close()


@app.get("/tasks/{id}", description = "Returns a single task by id.")
async def read_task(id: int):
    try:
        con = sqlite3.connect("tasks.db")
        cur = con.cursor()
        cur.execute("SELECT * FROM tasks WHERE id = ?", (str(id)))
        row = cur.fetchone()

        if row:
            return {"id": row[0], "title":row[1], "done":row[2]}
        raise HTTPException(status_code = 404, detail = f"error: Task {id} not found")

    except sqlite3.Error as error:
        raise HTTPException(status_code= 500, detail = error)
    finally:
            if con:
                con.close()


@app.post("/tasks", 
          description = "Creates a new task.",
          response_model=Task,
          status_code=201)
async def create_task(task: TaskCreate):
    if task.title is None or "":
            raise HTTPException(status_code = 400, detail = "title is required and cannot be empty")
    
    try:
        con = sqlite3.connect("tasks.db")
        cur = con.cursor()

        cur.execute("SELECT * FROM tasks ORDER BY id DESC")
        largest_id = cur.fetchone()[0]
        new_task = Task(largest_id+1, task.title, task.done)

        cur.execute("INSERT INTO tasks (id, title, done) VALUES (?,?,?)", (new_task.id, new_task.title, new_task.done))
        con.commit()
        return new_task
    except sqlite3.Error as error:
            raise HTTPException(status_code= 500, detail = error)
    finally:
            if con:
                con.close()


@app.put("/tasks/{id}", 
         description = "Updates a task's title and/or done. Send one or both fields; omitted fields stay unchanged.",
         response_model=Task,
         status_code=201)
async def update_task(task: Task):
    try:
        con = sqlite3.connect("tasks.db")
        cur = con.cursor()

        cur.execute("SELECT * FROM tasks WHERE id = ?", (str(task.id)))
        row = cur.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail=f"error: Task {task.id} not found")

        task.title = task.title if task.title is not None else row[1]
        task.done = task.done if task.done is not None else row[2]

        cur.execute("UPDATE tasks SET title = ?, done = ? WHERE id = ?", (task.title, task.done, task.id))
        con.commit()
        return task
    except sqlite3.Error as error:
            raise HTTPException(status_code= 500, detail = error)
    finally:
            if con:
                con.close()


@app.delete("/tasks/{id}", 
            description = "Deletes a task.",
            status_code=204)
async def delete_task(id: int):
    try:
        con = sqlite3.connect("tasks.db")
        cur = con.cursor()

        cur.execute("SELECT * FROM tasks WHERE id = ?", (str(id)))
        row = cur.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail=f"error: Task {id} not found")

        cur.execute("DELETE FROM tasks WHERE id = ?", (str(id)))
        con.commit()
        return None
    except sqlite3.Error as error:
            raise HTTPException(status_code= 500, detail = error)
    finally:
            if con:
                con.close()
