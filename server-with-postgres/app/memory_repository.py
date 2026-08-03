from typing import List, Optional

from .models import Task
from .repository import TaskRepository


class InMemoryTaskRepository(TaskRepository):
    """
    Original storage backend, kept here as a reference to show that
    swapping storage only means swapping this file for
    postgres_repository.py - service.py and main.py do not change.
    """

    def __init__(self):
        self._tasks: dict[int, Task] = {}

    def create(self, task: Task) -> Task:
        self._tasks[task.id] = task
        return task

    def get_all(self) -> List[Task]:
        return list(self._tasks.values())

    def get_by_id(self, task_id: int) -> Optional[Task]:
        return self._tasks.get(task_id)

    def update(self, task_id: int, task: Task) -> bool:
        if task_id not in self._tasks:
            return False
        self._tasks[task_id] = task
        return True

    def delete(self, task_id: int) -> bool:
        if task_id not in self._tasks:
            return False
        del self._tasks[task_id]
        return True
