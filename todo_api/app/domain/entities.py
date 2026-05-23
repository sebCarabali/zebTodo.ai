"""Domain entities - Pure business objects with no dependencies"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """User entity representing a system user"""
    id: str
    username: str
    email: str
    password_hash: str
    created_at: datetime = field(default_factory=datetime.utcnow)

    def verify_password(self, password_hash_func) -> bool:
        """Verify password against hash (delegates to service)"""
        pass  # Implementation in service layer


@dataclass
class Project:
    """Project entity representing a collaborative project"""
    id: str
    name: str
    description: Optional[str]
    owner_id: str
    created_at: datetime = field(default_factory=datetime.utcnow)

    def is_owner(self, user_id: str) -> bool:
        """Check if user is the project owner"""
        return self.owner_id == user_id


@dataclass
class Task:
    """Task entity representing a unit of work"""
    id: str
    title: str
    description: Optional[str]
    project_id: str
    assigned_to: Optional[str]
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    last_work_duration: Optional[float] = None

    def mark_complete(self) -> None:
        """Mark task as complete"""
        self.completed = True
        self.completed_at = datetime.utcnow()

    def can_be_started(self) -> bool:
        """Check if task can be started"""
        return not self.completed


@dataclass
class TaskTimer:
    """Timer entity for tracking work duration on tasks"""
    task_id: str
    user_id: str
    started_at: datetime = field(default_factory=datetime.utcnow)

    def get_elapsed_seconds(self) -> float:
        """Get elapsed time in seconds"""
        return (datetime.utcnow() - self.started_at).total_seconds()
