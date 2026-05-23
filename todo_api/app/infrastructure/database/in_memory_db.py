"""In-memory database implementation - Thread-safe storage"""

from threading import Lock
from datetime import datetime
from typing import Dict, List

from app.domain.entities import User, Project, Task, TaskTimer


class InMemoryDatabase:
    """
    Thread-safe in-memory database implementation.
    Uses a single lock for all operations to ensure consistency.
    Optimized for read-heavy workloads with O(1) lookups.
    """

    def __init__(self):
        self._lock = Lock()
        
        # Main data stores
        self.users: Dict[str, User] = {}
        self.projects: Dict[str, Project] = {}
        self.tasks: Dict[str, Task] = {}
        self.timers: Dict[str, TaskTimer] = {}
        
        # Relationship stores
        self.project_partners: Dict[str, List[str]] = {}  # project_id -> [user_ids]
        self.username_index: Dict[str, str] = {}  # username -> user_id (for fast lookup)

    def clear(self) -> None:
        """Clear all data (useful for testing)"""
        with self._lock:
            self.users.clear()
            self.projects.clear()
            self.tasks.clear()
            self.timers.clear()
            self.project_partners.clear()
            self.username_index.clear()

    # User operations
    def add_user(self, user: User) -> None:
        """Add user with username index"""
        with self._lock:
            self.users[user.id] = user
            self.username_index[user.username] = user.id

    def get_user(self, user_id: str) -> User | None:
        """Get user by ID - O(1)"""
        with self._lock:
            return self.users.get(user_id)

    def get_user_by_username(self, username: str) -> User | None:
        """Get user by username - O(1) with index"""
        with self._lock:
            user_id = self.username_index.get(username)
            if user_id:
                return self.users.get(user_id)
            return None

    # Project operations
    def add_project(self, project: Project) -> None:
        """Add project and initialize partners list"""
        with self._lock:
            self.projects[project.id] = project
            self.project_partners[project.id] = []

    def get_project(self, project_id: str) -> Project | None:
        """Get project by ID - O(1)"""
        with self._lock:
            return self.projects.get(project_id)

    def get_all_projects(self) -> List[Project]:
        """Get all projects - O(n)"""
        with self._lock:
            return list(self.projects.values())

    def add_project_partner(self, project_id: str, user_id: str) -> None:
        """Add partner to project - O(1) average"""
        with self._lock:
            if project_id not in self.project_partners:
                raise ValueError("Project not found")
            partners = self.project_partners[project_id]
            if user_id not in partners:
                partners.append(user_id)

    def get_project_partners(self, project_id: str) -> List[str]:
        """Get project partners - O(1)"""
        with self._lock:
            return list(self.project_partners.get(project_id, []))

    def is_project_partner(self, project_id: str, user_id: str) -> bool:
        """Check if user is project partner - O(n) where n is number of partners"""
        with self._lock:
            partners = self.project_partners.get(project_id, [])
            return user_id in partners

    # Task operations
    def add_task(self, task: Task) -> None:
        """Add task - O(1)"""
        with self._lock:
            self.tasks[task.id] = task

    def get_task(self, task_id: str) -> Task | None:
        """Get task by ID - O(1)"""
        with self._lock:
            return self.tasks.get(task_id)

    def get_tasks_by_project(self, project_id: str) -> List[Task]:
        """Get tasks by project - O(n)"""
        with self._lock:
            return [t for t in self.tasks.values() if t.project_id == project_id]

    def update_task(self, task: Task) -> None:
        """Update task - O(1)"""
        with self._lock:
            if task.id in self.tasks:
                self.tasks[task.id] = task

    # Timer operations
    def start_timer(self, task_id: str, user_id: str) -> TaskTimer:
        """Start timer for task - O(1)"""
        with self._lock:
            timer = TaskTimer(task_id=task_id, user_id=user_id)
            self.timers[task_id] = timer
            return timer

    def stop_timer(self, task_id: str) -> float | None:
        """Stop timer and return duration - O(1)"""
        with self._lock:
            if task_id in self.timers:
                timer = self.timers.pop(task_id)
                return timer.get_elapsed_seconds()
            return None

    def get_timer(self, task_id: str) -> TaskTimer | None:
        """Get active timer - O(1)"""
        with self._lock:
            return self.timers.get(task_id)


# Singleton instance
db = InMemoryDatabase()
