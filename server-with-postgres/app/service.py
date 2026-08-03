from typing import List, Optional

from .models import Task
from .repository import TaskRepository


class TaskService:
    """
    Business logic layer. Depends only on the TaskRepository interface,
    never on a concrete implementation - so it never changes when
    storage is swapped.
    """

    def __init__(self, repo: TaskRepository):
        self.repo = repo

    def create_task(self, task: Task) -> Task:
        return self.repo.create(task)

    def list_tasks(self) -> List[Task]:
        return self.repo.get_all()

    def get_task(self, task_id: int) -> Optional[Task]:
        return self.repo.get_by_id(task_id)

    def update_task(self, task_id: int, task: Task) -> bool:
        return self.repo.update(task_id, task)

    def delete_task(self, task_id: int) -> bool:
        return self.repo.delete(task_id)
