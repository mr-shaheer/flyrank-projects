# Task Manager API (FastAPI)

A simple RESTful API built with FastAPI for managing tasks, using in-memory storage.

## Features

- Create, read, update, and delete tasks (CRUD)
- In-memory data storage (no database required)
- Automatic request/response validation with Pydantic
- Interactive API docs via Swagger UI

## Requirements

- Python 3.8+
- FastAPI
- Uvicorn

## Installation

```bash
pip install fastapi uvicorn
```

## Running the Server

```bash
uvicorn server:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

Interactive docs: `http://127.0.0.1:8000/docs`

## API Endpoints

| Method | Endpoint           | Description      |
|--------|--------------------|-------------------|
| GET    | /                  | Health check      |
| POST   | /tasks             | Create a task     |
| GET    | /tasks             | Get all tasks     |
| GET    | /tasks/{task_id}   | Get a task        |
| PUT    | /tasks/{task_id}   | Update a task     |
| DELETE | /tasks/{task_id}   | Delete a task     |

## Task Model

```json
{
  "id": 1,
  "title": "Buy groceries",
  "completed": false
}
```

## Example Usage

**Create a task:**

```bash
curl -X POST http://127.0.0.1:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"id": 1, "title": "Buy groceries", "completed": false}'
```

**Get all tasks:**

```bash
curl http://127.0.0.1:8000/tasks
```

## Status Codes

- 200 OK
- 201 Created
- 400 Bad Request
- 404 Not Found
- 500 Internal Server Error

## Notes

- Data is stored in memory and will reset whenever the server restarts.
- This project is intended as a learning/assignment exercise.
