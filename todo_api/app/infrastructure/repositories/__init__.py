"""Repository implementations - Infrastructure layer"""

from app.domain.entities import User, Project, Task, TaskTimer
from app.domain.repositories import (
    IUserRepository, IProjectRepository, ITaskRepository, ITaskTimerRepository
)
from app.infrastructure.database import InMemoryDatabase


class UserRepository(IUserRepository):
    """In-memory implementation of IUserRepository"""

    def __init__(self, database: InMemoryDatabase):
        self.db = database

    def add(self, user: User) -> None:
        self.db.add_user(user)

    def get_by_id(self, user_id: str) -> User | None:
        return self.db.get_user(user_id)

    def get_by_username(self, username: str) -> User | None:
        return self.db.get_user_by_username(username)


class ProjectRepository(IProjectRepository):
    """In-memory implementation of IProjectRepository"""

    def __init__(self, database: InMemoryDatabase):
        self.db = database

    def add(self, project: Project) -> None:
        self.db.add_project(project)

    def get_by_id(self, project_id: str) -> Project | None:
        return self.db.get_project(project_id)

    def get_all(self) -> list[Project]:
        return self.db.get_all_projects()

    def add_partner(self, project_id: str, user_id: str) -> None:
        self.db.add_project_partner(project_id, user_id)

    def get_partners(self, project_id: str) -> list[str]:
        return self.db.get_project_partners(project_id)

    def is_partner(self, project_id: str, user_id: str) -> bool:
        return self.db.is_project_partner(project_id, user_id)


class TaskRepository(ITaskRepository):
    """In-memory implementation of ITaskRepository"""

    def __init__(self, database: InMemoryDatabase):
        self.db = database

    def add(self, task: Task) -> None:
        self.db.add_task(task)

    def get_by_id(self, task_id: str) -> Task | None:
        return self.db.get_task(task_id)

    def get_by_project(self, project_id: str) -> list[Task]:
        return self.db.get_tasks_by_project(project_id)

    def update(self, task: Task) -> None:
        self.db.update_task(task)


class TaskTimerRepository(ITaskTimerRepository):
    """In-memory implementation of ITaskTimerRepository"""

    def __init__(self, database: InMemoryDatabase):
        self.db = database

    def start(self, task_id: str, user_id: str) -> TaskTimer:
        return self.db.start_timer(task_id, user_id)

    def stop(self, task_id: str) -> float | None:
        return self.db.stop_timer(task_id)

    def get(self, task_id: str) -> TaskTimer | None:
        return self.db.get_timer(task_id)
