"""Repository interfaces - Abstract contracts for data access"""

from abc import ABC, abstractmethod
from typing import Optional, List
from app.domain.entities import User, Project, Task, TaskTimer


class IUserRepository(ABC):
    """Interface for user data access"""

    @abstractmethod
    def add(self, user: User) -> None:
        """Add a new user"""
        pass

    @abstractmethod
    def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        pass


class IProjectRepository(ABC):
    """Interface for project data access"""

    @abstractmethod
    def add(self, project: Project) -> None:
        """Add a new project"""
        pass

    @abstractmethod
    def get_by_id(self, project_id: str) -> Optional[Project]:
        """Get project by ID"""
        pass

    @abstractmethod
    def get_all(self) -> List[Project]:
        """Get all projects"""
        pass

    @abstractmethod
    def add_partner(self, project_id: str, user_id: str) -> None:
        """Add a partner to a project"""
        pass

    @abstractmethod
    def get_partners(self, project_id: str) -> List[str]:
        """Get all partner IDs for a project"""
        pass

    @abstractmethod
    def is_partner(self, project_id: str, user_id: str) -> bool:
        """Check if user is a partner of the project"""
        pass


class ITaskRepository(ABC):
    """Interface for task data access"""

    @abstractmethod
    def add(self, task: Task) -> None:
        """Add a new task"""
        pass

    @abstractmethod
    def get_by_id(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        pass

    @abstractmethod
    def get_by_project(self, project_id: str) -> List[Task]:
        """Get all tasks for a project"""
        pass

    @abstractmethod
    def update(self, task: Task) -> None:
        """Update an existing task"""
        pass


class ITaskTimerRepository(ABC):
    """Interface for task timer data access"""

    @abstractmethod
    def start(self, task_id: str, user_id: str) -> TaskTimer:
        """Start a timer for a task"""
        pass

    @abstractmethod
    def stop(self, task_id: str) -> Optional[float]:
        """Stop timer and return duration in seconds"""
        pass

    @abstractmethod
    def get(self, task_id: str) -> Optional[TaskTimer]:
        """Get active timer for a task"""
        pass
