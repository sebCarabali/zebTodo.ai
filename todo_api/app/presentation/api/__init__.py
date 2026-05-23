"""API routes module"""

from .user_routes import router as user_router
from .project_routes import router as project_router
from .task_routes import router as task_router

__all__ = ["user_router", "project_router", "task_router"]
