"""Task use cases - Task and timer management"""

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from app.domain.entities import Task
from app.domain.repositories import (
    ITaskRepository, IProjectRepository, ITaskTimerRepository
)
from app.application.dto import (
    TaskCreateDTO, TaskUpdateDTO, TaskResponseDTO, TimerStatusDTO
)


class TaskUseCases:
    """Use cases for task operations following SRP and ISP"""

    def __init__(
        self,
        task_repository: ITaskRepository,
        project_repository: IProjectRepository,
        timer_repository: ITaskTimerRepository
    ):
        self.task_repository = task_repository
        self.project_repository = project_repository
        self.timer_repository = timer_repository

    def create_task(
        self, dto: TaskCreateDTO, current_user_id: str
    ) -> TaskResponseDTO:
        """Create a new task in a project"""
        # Verify project exists and user is partner
        if not self.project_repository.get_by_id(dto.project_id):
            raise ValueError("Project not found")

        if not self.project_repository.is_partner(dto.project_id, current_user_id):
            raise PermissionError("Not authorized to create tasks in this project")

        # Verify assigned user is a partner if provided
        if dto.assigned_to:
            if not self.project_repository.is_partner(dto.project_id, dto.assigned_to):
                raise ValueError("Assigned user must be a project partner")

        # Create task entity
        task = Task(
            id=str(uuid.uuid4()),
            title=dto.title,
            description=dto.description,
            project_id=dto.project_id,
            assigned_to=dto.assigned_to
        )

        # Save task
        self.task_repository.add(task)

        return self._task_to_response_dto(task)

    def get_task(
        self, task_id: str, current_user_id: str
    ) -> Optional[TaskResponseDTO]:
        """Get task by ID with authorization check"""
        task = self.task_repository.get_by_id(task_id)
        if not task:
            return None

        # Check authorization
        if not self.project_repository.is_partner(task.project_id, current_user_id):
            raise PermissionError("Not authorized to view this task")

        return self._task_to_response_dto(task)

    def get_project_tasks(
        self, project_id: str, current_user_id: str
    ) -> List[TaskResponseDTO]:
        """Get all tasks in a project"""
        # Verify project exists and user is partner
        project = self.project_repository.get_by_id(project_id)
        if not project:
            raise ValueError("Project not found")

        if not self.project_repository.is_partner(project_id, current_user_id):
            raise PermissionError("Not authorized to view tasks in this project")

        # Get tasks
        tasks = self.task_repository.get_by_project(project_id)
        return [self._task_to_response_dto(task) for task in tasks]

    def update_task(
        self, task_id: str, dto: TaskUpdateDTO, current_user_id: str
    ) -> TaskResponseDTO:
        """Update an existing task"""
        task = self.task_repository.get_by_id(task_id)
        if not task:
            raise ValueError("Task not found")

        # Check authorization
        if not self.project_repository.is_partner(task.project_id, current_user_id):
            raise PermissionError("Not authorized to update this task")

        # Apply updates
        if dto.title is not None:
            task.title = dto.title
        if dto.description is not None:
            task.description = dto.description
        if dto.assigned_to is not None:
            if not self.project_repository.is_partner(task.project_id, dto.assigned_to):
                raise ValueError("Assigned user must be a project partner")
            task.assigned_to = dto.assigned_to

        # Save changes
        self.task_repository.update(task)

        return self._task_to_response_dto(task)

    def start_task(
        self, task_id: str, current_user_id: str
    ) -> Dict[str, Any]:
        """Start working on a task (start timer)"""
        task = self.task_repository.get_by_id(task_id)
        if not task:
            raise ValueError("Task not found")

        # Check authorization
        if not self.project_repository.is_partner(task.project_id, current_user_id):
            raise PermissionError("Not authorized to work on this task")

        # Check if task can be started
        if not task.can_be_started():
            raise ValueError("Cannot start a completed task")

        # Stop existing timer if any
        self.timer_repository.stop(task_id)

        # Start new timer
        timer = self.timer_repository.start(task_id, current_user_id)

        return {
            "message": "Task timer started",
            "task_id": task_id,
            "started_at": timer.started_at.isoformat()
        }

    def complete_task(
        self, task_id: str, current_user_id: str
    ) -> TaskResponseDTO:
        """Mark task as complete and stop timer"""
        task = self.task_repository.get_by_id(task_id)
        if not task:
            raise ValueError("Task not found")

        # Check authorization
        if not self.project_repository.is_partner(task.project_id, current_user_id):
            raise PermissionError("Not authorized to complete this task")

        # Check if already completed
        if task.completed:
            raise ValueError("Task already completed")

        # Stop timer and get duration
        duration = self.timer_repository.stop(task_id)

        # Mark task as complete
        task.mark_complete()
        if duration is not None:
            task.last_work_duration = duration

        # Save changes
        self.task_repository.update(task)

        # Return response with duration
        response = self._task_to_response_dto(task)
        if duration is not None:
            response.work_duration_seconds = duration

        return response

    def get_timer_status(
        self, task_id: str, current_user_id: str
    ) -> TimerStatusDTO:
        """Get current timer status for a task"""
        task = self.task_repository.get_by_id(task_id)
        if not task:
            raise ValueError("Task not found")

        # Check authorization
        if not self.project_repository.is_partner(task.project_id, current_user_id):
            raise PermissionError("Not authorized to view this task")

        # Get timer
        timer = self.timer_repository.get(task_id)
        if not timer:
            return TimerStatusDTO(active=False, task_id=task_id)

        return TimerStatusDTO(
            active=True,
            task_id=task_id,
            started_at=timer.started_at,
            elapsed_seconds=timer.get_elapsed_seconds(),
            user_id=timer.user_id
        )

    def _task_to_response_dto(self, task: Task) -> TaskResponseDTO:
        """Convert Task entity to TaskResponseDTO"""
        return TaskResponseDTO(
            id=task.id,
            title=task.title,
            description=task.description,
            project_id=task.project_id,
            assigned_to=task.assigned_to,
            completed=task.completed,
            created_at=task.created_at,
            completed_at=task.completed_at,
            last_work_duration=task.last_work_duration
        )
