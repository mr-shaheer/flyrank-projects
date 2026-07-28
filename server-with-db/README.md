# Task Manager API

A simple **Task Manager API** built with **FastAPI**, backed by a **SQLite** database for persistent storage.

This project takes a basic CRUD API — the kind you'd normally build with an in-memory Python list — and connects it to a real SQLite database instead. The routes, request shapes, and response shapes stay exactly the same; only the storage underneath changes. It's a small demonstration that **persistence is just an implementation detail**.

---

## Features

- Create, read, update, and delete (CRUD) tasks
- Data persisted in a SQLite database (`tasks.db`), using Python's built-in `sqlite3` module
- Table is created automatically on startup, and seeded with 3 sample tasks the first time it runs
- Simple `Task` model validated with Pydantic
- Interactive API docs via FastAPI's auto-generated Swagger UI

---

## Tech Stack

- **Python 3.9+**
- **FastAPI** — web framework
- **Uvicorn** — ASGI server
- **SQLite3** — lightweight, file-based relational database (via Python's standard `sqlite3` module)
- **Pydantic** — request/response data validation

---

## Project Structure

```
task-manager-api/
├── main.py            # FastAPI app, DB setup, and all route definitions
├── tasks.db            # SQLite database file (auto-created on first run)
├── requirements.txt
└── README.md
```

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/task-manager-api.git
cd task-manager-api
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install fastapi uvicorn
```

(`sqlite3` ships with Python's standard library, so no separate install is needed.)

### 4. Run the application

```bash
uvicorn main:app --reload
```

The API will be available at:

```
http://127.0.0.1:8000
```

Interactive Swagger docs:

```
http://127.0.0.1:8000/docs
```

---

## Database Setup

On startup, `init_db()` runs automatically and:

1. Connects to the local SQLite file (`tasks.db`), creating it if it doesn't exist.
2. Creates the `tasks` table if it doesn't already exist.
3. If the table is empty, seeds it with 3 sample tasks (`Learn FastAPI`, `Build CRUD API`, `Connect SQLite DB`).

Table schema:

```sql
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    completed BOOLEAN NOT NULL
)
```

Each request opens its own connection with `get_connection()`, runs the relevant SQL through a cursor, commits on writes, and closes the connection — replacing what used to be simple list operations in memory.

> Note: `id` is supplied by the client when creating a task (not auto-incremented by the database), and must be unique — attempting to reuse an existing `id` returns a `400` error.

---

## API Endpoints

| Method | Endpoint          | Description                  |
|--------|-------------------|-------------------------------|
| GET    | `/`               | Health check — confirms the API is running |
| GET    | `/tasks`          | Retrieve all tasks            |
| GET    | `/tasks/{task_id}`| Retrieve a single task by ID  |
| POST   | `/tasks`          | Create a new task             |
| PUT    | `/tasks/{task_id}`| Update an existing task       |
| DELETE | `/tasks/{task_id}`| Delete a task                 |

### Task Model

```json
{
  "id": 1,
  "title": "Learn FastAPI",
  "completed": false
}
```

- `id` (int, required) — must be unique
- `title` (string, required)
- `completed` (bool, optional, defaults to `false`)

### Example Request — Health Check

```bash
curl http://127.0.0.1:8000/
```

### Example Request — Create a Task

```bash
curl -X POST "http://127.0.0.1:8000/tasks" \
  -H "Content-Type: application/json" \
  -d '{"id": 4, "title": "Write tests", "completed": false}'
```

### Example Request — Get All Tasks

```bash
curl http://127.0.0.1:8000/tasks
```

### Example Request — Get a Single Task

```bash
curl http://127.0.0.1:8000/tasks/1
```

### Example Request — Update a Task

```bash
curl -X PUT "http://127.0.0.1:8000/tasks/1" \
  -H "Content-Type: application/json" \
  -d '{"id": 1, "title": "Learn FastAPI", "completed": true}'
```

### Example Request — Delete a Task

```bash
curl -X DELETE "http://127.0.0.1:8000/tasks/1"
```

---

## Error Handling

- `POST /tasks` with an `id` that already exists → `400 Bad Request: Task with this ID already exists`
- `GET /tasks/{task_id}`, `PUT /tasks/{task_id}`, `DELETE /tasks/{task_id}` with an `id` that doesn't exist → `404 Not Found: Task not found`

---

## Why SQLite Instead of an In-Memory List?

The original version of this project stored tasks in a Python list that lived only in memory — meaning all data was lost every time the server restarted. Swapping in SQLite means:

- **Data persists** across server restarts
- The app behaves closer to a **real production backend**
- It's a natural stepping stone toward using more advanced databases (PostgreSQL, MySQL) or an ORM like SQLAlchemy later on
- Demonstrates a key backend engineering principle: **the API layer and the storage layer are independent** — you can change one without changing the other

---