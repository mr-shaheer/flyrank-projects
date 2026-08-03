from typing import List, Optional

import psycopg2

from .models import Task
from .repository import TaskRepository


class PostgresTaskRepository(TaskRepository):
    """
    Concrete storage backend backed by Postgres.
    This is the only file in the app that knows SQL exists.
    """

    def __init__(self, dsn: str):
        self.dsn = dsn

    def _conn(self):
        return psycopg2.connect(self.dsn)

    def create(self, task: Task) -> Task:
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO tasks (id, title, completed) VALUES (%s, %s, %s)",
                (task.id, task.title, task.completed),
            )
            conn.commit()
        finally:
            conn.close()
        return task

    def get_all(self) -> List[Task]:
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, title, completed FROM tasks ORDER BY id")
            rows = cur.fetchall()
        finally:
            conn.close()
        return [Task(id=r[0], title=r[1], completed=r[2]) for r in rows]

    def get_by_id(self, task_id: int) -> Optional[Task]:
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, title, completed FROM tasks WHERE id = %s", (task_id,)
            )
            row = cur.fetchone()
        finally:
            conn.close()
        return Task(id=row[0], title=row[1], completed=row[2]) if row else None

    def update(self, task_id: int, task: Task) -> bool:
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute(
                "UPDATE tasks SET title = %s, completed = %s WHERE id = %s",
                (task.title, task.completed, task_id),
            )
            updated = cur.rowcount > 0
            conn.commit()
        finally:
            conn.close()
        return updated

    def delete(self, task_id: int) -> bool:
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
            deleted = cur.rowcount > 0
            conn.commit()
        finally:
            conn.close()
        return deleted
