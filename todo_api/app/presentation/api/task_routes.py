"""Task API routes - Task and timer management endpoints"""

from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional

from app.application.dto import TaskCreateDTO, TaskUpdateDTO
from app.application.use_cases import TaskUseCases
from app.infrastructure.repositories import (
    TaskRepository, ProjectRepository, TaskTimerRepository
)
from app.infrastructure.database import db
from app.presentation.dependencies import get_current_user


router = APIRouter(tags=["Tasks"])


# Pydantic models for request/response validation
class TaskCreateRequest(BaseModel):
    title: str
    description: Optional[str] = None
    project_id: str
    assigned_to: Optional[str] = None


class TaskUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assigned_to: Optional[str] = None


class TaskResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    project_id: str
    assigned_to: Optional[str]
    completed: bool
    created_at: str  # ISO format string
    completed_at: Optional[str] = None
    last_work_duration: Optional[float] = None
    work_duration_seconds: Optional[float] = None  # Added when completing task


class TimerStatusResponse(BaseModel):
    active: bool
    task_id: str
    started_at: Optional[str] = None
    elapsed_seconds: Optional[float] = None
    user_id: Optional[str] = None


class StartTaskResponse(BaseModel):
    message: str
    task_id: str
    started_at: str


def get_task_use_cases() -> TaskUseCases:
    """Factory function to create TaskUseCases with dependencies"""
    task_repo = TaskRepository(database=db)
    project_repo = ProjectRepository(database=db)
    timer_repo = TaskTimerRepository(database=db)
    return TaskUseCases(task_repo, project_repo, timer_repo)


@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create a new task in a project"""
    use_cases = get_task_use_cases()
    
    dto = TaskCreateDTO(
        title=task_data.title,
        description=task_data.description,
        project_id=task_data.project_id,
        assigned_to=task_data.assigned_to
    )
    
    try:
        result = use_cases.create_task(dto, current_user["id"])
        return TaskResponse(
            id=result.id,
            title=result.title,
            description=result.description,
            project_id=result.project_id,
            assigned_to=result.assigned_to,
            completed=result.completed,
            created_at=result.created_at.isoformat(),
            completed_at=result.completed_at.isoformat() if result.completed_at else None,
            last_work_duration=result.last_work_duration
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get("/projects/{project_id}/tasks", response_model=List[TaskResponse])
async def get_tasks(
    project_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get all tasks in a project"""
    use_cases = get_task_use_cases()
    
    try:
        results = use_cases.get_project_tasks(project_id, current_user["id"])
        return [
            TaskResponse(
                id=t.id,
                title=t.title,
                description=t.description,
                project_id=t.project_id,
                assigned_to=t.assigned_to,
                completed=t.completed,
                created_at=t.created_at.isoformat(),
                completed_at=t.completed_at.isoformat() if t.completed_at else None,
                last_work_duration=t.last_work_duration
            )
            for t in results
        ]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.patch("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_data: TaskUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update a task"""
    use_cases = get_task_use_cases()
    
    dto = TaskUpdateDTO(
        title=task_data.title,
        description=task_data.description,
        assigned_to=task_data.assigned_to
    )
    
    try:
        result = use_cases.update_task(task_id, dto, current_user["id"])
        return TaskResponse(
            id=result.id,
            title=result.title,
            description=result.description,
            project_id=result.project_id,
            assigned_to=result.assigned_to,
            completed=result.completed,
            created_at=result.created_at.isoformat(),
            completed_at=result.completed_at.isoformat() if result.completed_at else None,
            last_work_duration=result.last_work_duration
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.post("/tasks/{task_id}/start", response_model=StartTaskResponse)
async def start_task(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Start working on a task (starts timer)"""
    use_cases = get_task_use_cases()
    
    try:
        result = use_cases.start_task(task_id, current_user["id"])
        return StartTaskResponse(
            message=result["message"],
            task_id=result["task_id"],
            started_at=result["started_at"]
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.post("/tasks/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Mark a task as complete (stops timer and records duration)"""
    use_cases = get_task_use_cases()
    
    try:
        result = use_cases.complete_task(task_id, current_user["id"])
        return TaskResponse(
            id=result.id,
            title=result.title,
            description=result.description,
            project_id=result.project_id,
            assigned_to=result.assigned_to,
            completed=result.completed,
            created_at=result.created_at.isoformat(),
            completed_at=result.completed_at.isoformat() if result.completed_at else None,
            last_work_duration=result.last_work_duration,
            work_duration_seconds=getattr(result, 'work_duration_seconds', None)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get("/tasks/{task_id}/timer", response_model=TimerStatusResponse)
async def get_task_timer(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get current timer status for a task"""
    use_cases = get_task_use_cases()
    
    try:
        result = use_cases.get_timer_status(task_id, current_user["id"])
        return TimerStatusResponse(
            active=result.active,
            task_id=result.task_id,
            started_at=result.started_at.isoformat() if result.started_at else None,
            elapsed_seconds=result.elapsed_seconds,
            user_id=result.user_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get("/projects/{project_id}/export")
async def export_project_tasks(
    project_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Export project tasks to Excel file"""
    use_cases = get_task_use_cases()
    
    try:
        excel_file = use_cases.export_project_to_excel(project_id, current_user["id"])
        
        return StreamingResponse(
            excel_file,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename=project_{project_id}_tasks.xlsx"
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
