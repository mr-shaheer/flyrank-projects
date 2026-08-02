import os
from typing import List

from fastapi import FastAPI, HTTPException

from .models import Task
from .postgres_repository import PostgresTaskRepository
from .service import TaskService

app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL")

# The only line that changes when storage is swapped.
repo = PostgresTaskRepository(DATABASE_URL)
service = TaskService(repo)


@app.get("/")
def home():
    return {"message": "API is running"}


@app.post("/tasks", response_model=Task)
def create_task(task: Task):
    if service.get_task(task.id):
        raise HTTPException(status_code=400, detail="Task with this ID already exists")
    return service.create_task(task)


@app.get("/tasks", response_model=List[Task])
def get_tasks():
    return service.list_tasks()


@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    task = service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, updated_task: Task):
    if not service.update_task(task_id, updated_task):
        raise HTTPException(status_code=404, detail="Task not found")
    return updated_task


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    if not service.delete_task(task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted"}
