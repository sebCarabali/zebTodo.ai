"""Task use cases - Task and timer management"""

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from io import BytesIO

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter

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

    def export_project_to_excel(
        self, project_id: str, current_user_id: str
    ) -> BytesIO:
        """Export project tasks to Excel file"""
        # Verify project exists and user is partner
        project = self.project_repository.get_by_id(project_id)
        if not project:
            raise ValueError("Project not found")

        if not self.project_repository.is_partner(project_id, current_user_id):
            raise PermissionError("Not authorized to view tasks in this project")

        # Get all tasks for the project
        tasks = self.task_repository.get_by_project(project_id)
        
        # Create workbook and worksheet
        wb = Workbook()
        ws = wb.active
        ws.title = f"Tasks - {project.name}"

        # Define styles
        header_font = Font(bold=True, color="FFFFFF", size=12)
        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        header_alignment = Alignment(horizontal="center", vertical="center")
        
        thin_border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
        center_alignment = Alignment(horizontal="center", vertical="center")
        left_alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)

        # Define headers
        headers = [
            "Task ID", "Title", "Description", "Assigned To", 
            "Status", "Created At", "Completed At", "Last Work Duration (sec)"
        ]

        # Add headers with styling
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
            cell.border = thin_border

        # Add task data
        for row_num, task in enumerate(tasks, 2):
            ws.cell(row=row_num, column=1, value=task.id).border = thin_border
            ws.cell(row=row_num, column=2, value=task.title).alignment = left_alignment
            ws.cell(row=row_num, column=2).border = thin_border
            
            desc_cell = ws.cell(row=row_num, column=3, value=task.description or "")
            desc_cell.alignment = left_alignment
            desc_cell.border = thin_border
            
            ws.cell(row=row_num, column=4, value=task.assigned_to or "Unassigned").border = thin_border
            
            status_cell = ws.cell(row=row_num, column=5, value="Completed" if task.completed else "Pending")
            status_cell.alignment = center_alignment
            status_cell.border = thin_border
            if task.completed:
                status_cell.font = Font(color="008000", bold=True)  # Green for completed
            else:
                status_cell.font = Font(color="FFA500", bold=True)  # Orange for pending
            
            ws.cell(row=row_num, column=6, value=task.created_at.strftime("%Y-%m-%d %H:%M:%S")).border = thin_border
            ws.cell(row=row_num, column=7, value=task.completed_at.strftime("%Y-%m-%d %H:%M:%S") if task.completed_at else "").border = thin_border
            ws.cell(row=row_num, column=8, value=task.last_work_duration or 0).alignment = center_alignment
            ws.cell(row=row_num, column=8).border = thin_border

        # Auto-adjust column widths
        column_widths = [15, 30, 40, 20, 12, 20, 20, 25]
        for i, width in enumerate(column_widths, 1):
            ws.column_dimensions[get_column_letter(i)].width = width

        # Save to BytesIO
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        
        return output
