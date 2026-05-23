"""Project API routes - Project and partner management endpoints"""

from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from app.application.dto import ProjectCreateDTO, PartnerAddDTO
from app.application.use_cases import ProjectUseCases
from app.infrastructure.repositories import UserRepository, ProjectRepository
from app.infrastructure.database import db
from app.presentation.dependencies import get_current_user


router = APIRouter(tags=["Projects"])


# Pydantic models for request/response validation
class ProjectCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None


class ProjectResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    owner_id: str
    created_at: str  # ISO format string


class PartnerAddRequest(BaseModel):
    user_id: str


class MessageResponse(BaseModel):
    message: str


def get_project_use_cases() -> ProjectUseCases:
    """Factory function to create ProjectUseCases with dependencies"""
    project_repo = ProjectRepository(database=db)
    user_repo = UserRepository(database=db)
    return ProjectUseCases(project_repo, user_repo)


@router.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create a new project (owner is automatically added as partner)"""
    use_cases = get_project_use_cases()
    
    dto = ProjectCreateDTO(
        name=project_data.name,
        description=project_data.description
    )
    
    try:
        result = use_cases.create_project(dto, current_user["id"])
        return ProjectResponse(
            id=result.id,
            name=result.name,
            description=result.description,
            owner_id=result.owner_id,
            created_at=result.created_at.isoformat()
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get("/projects", response_model=List[ProjectResponse])
async def get_projects(current_user: dict = Depends(get_current_user)):
    """Get all projects where user is a partner"""
    use_cases = get_project_use_cases()
    
    try:
        results = use_cases.get_user_projects(current_user["id"])
        return [
            ProjectResponse(
                id=p.id,
                name=p.name,
                description=p.description,
                owner_id=p.owner_id,
                created_at=p.created_at.isoformat()
            )
            for p in results
        ]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific project"""
    use_cases = get_project_use_cases()
    
    try:
        result = use_cases.get_project(project_id, current_user["id"])
        if not result:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return ProjectResponse(
            id=result.id,
            name=result.name,
            description=result.description,
            owner_id=result.owner_id,
            created_at=result.created_at.isoformat()
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.post("/projects/{project_id}/partners", status_code=status.HTTP_201_CREATED)
async def add_partner(
    project_id: str,
    partner_data: PartnerAddRequest,
    current_user: dict = Depends(get_current_user)
):
    """Add a partner to a project (only owner can add partners)"""
    use_cases = get_project_use_cases()
    
    dto = PartnerAddDTO(user_id=partner_data.user_id)
    
    try:
        use_cases.add_partner(project_id, dto, current_user["id"])
        return MessageResponse(message="Partner added successfully")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
