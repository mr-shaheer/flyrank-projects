from abc import ABC, abstractmethod
from typing import List, Optional

from .models import Task


class TaskRepository(ABC):
    """
    Contract that any storage backend must fulfil.
    The service layer only ever talks to this interface,
    never to a concrete implementation directly.
    """

    @abstractmethod
    def create(self, task: Task) -> Task:
        ...

    @abstractmethod
    def get_all(self) -> List[Task]:
        ...

    @abstractmethod
    def get_by_id(self, task_id: int) -> Optional[Task]:
        ...

    @abstractmethod
    def update(self, task_id: int, task: Task) -> bool:
        ...

    @abstractmethod
    def delete(self, task_id: int) -> bool:
        ...
