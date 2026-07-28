from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import sqlite3

app = FastAPI()

DB_NAME = "tasks.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            completed BOOLEAN NOT NULL
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]

    if count == 0:
        cursor.executemany("""
            INSERT INTO tasks (id, title, completed)
            VALUES (?, ?, ?)
        """, [
            (1, "Learn FastAPI", False),
            (2, "Build CRUD API", False),
            (3, "Connect SQLite DB", False)
        ])
    
    conn.commit()
    conn.close()

init_db()

class Task(BaseModel):
    id: int
    title: str
    completed: bool = False

@app.get("/")
def home():
    return {"message": "API is running"}

@app.post("/tasks", response_model=Task)
def create_task(task: Task):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO tasks (id, title, completed) VALUES (?, ?, ?)",
            (task.id, task.title, task.completed)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Task with this ID already exists")

    conn.close()
    return task

@app.get("/tasks", response_model=List[Task])
def get_tasks():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, title, completed FROM tasks")
    rows = cursor.fetchall()

    conn.close()

    return [Task(id=row[0], title=row[1], completed=bool(row[2])) for row in rows]

@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, title, completed FROM tasks WHERE id = ?",
        (task_id,)
    )
    row = cursor.fetchone()
    conn.close()

    if row:
        return Task(id=row[0], title=row[1], completed=bool(row[2]))

    raise HTTPException(status_code=404, detail="Task not found")

@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, updated_task: Task):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE tasks SET title = ?, completed = ? WHERE id = ?",
        (updated_task.title, updated_task.completed, task_id)
    )

    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found")

    conn.commit()
    conn.close()

    return updated_task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found")

    conn.commit()
    conn.close()

    return {"message": "Task deleted"}