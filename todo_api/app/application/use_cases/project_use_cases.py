"""Project use cases - Project and partner management"""

import uuid
from datetime import datetime
from typing import List, Optional

from app.domain.entities import Project
from app.domain.repositories import IProjectRepository, IUserRepository
from app.application.dto import (
    ProjectCreateDTO, ProjectResponseDTO, PartnerAddDTO
)


class ProjectUseCases:
    """Use cases for project operations following SRP and OCP"""

    def __init__(
        self,
        project_repository: IProjectRepository,
        user_repository: IUserRepository
    ):
        self.project_repository = project_repository
        self.user_repository = user_repository

    def create_project(
        self, dto: ProjectCreateDTO, owner_id: str
    ) -> ProjectResponseDTO:
        """Create a new project with owner as initial partner"""
        project = Project(
            id=str(uuid.uuid4()),
            name=dto.name,
            description=dto.description,
            owner_id=owner_id
        )

        # Save project
        self.project_repository.add(project)

        # Add owner as partner
        self.project_repository.add_partner(project.id, owner_id)

        return ProjectResponseDTO(
            id=project.id,
            name=project.name,
            description=project.description,
            owner_id=project.owner_id,
            created_at=project.created_at
        )

    def get_project(
        self, project_id: str, user_id: str
    ) -> Optional[ProjectResponseDTO]:
        """Get project by ID if user is a partner"""
        project = self.project_repository.get_by_id(project_id)
        if not project:
            return None

        # Check authorization
        if not self.project_repository.is_partner(project_id, user_id):
            raise PermissionError("Not authorized to access this project")

        return ProjectResponseDTO(
            id=project.id,
            name=project.name,
            description=project.description,
            owner_id=project.owner_id,
            created_at=project.created_at
        )

    def get_user_projects(self, user_id: str) -> List[ProjectResponseDTO]:
        """Get all projects where user is a partner"""
        all_projects = self.project_repository.get_all()
        user_projects = []

        for project in all_projects:
            if self.project_repository.is_partner(project.id, user_id):
                user_projects.append(ProjectResponseDTO(
                    id=project.id,
                    name=project.name,
                    description=project.description,
                    owner_id=project.owner_id,
                    created_at=project.created_at
                ))

        return user_projects

    def add_partner(
        self, project_id: str, partner_dto: PartnerAddDTO, current_user_id: str
    ) -> None:
        """Add a partner to project (only owner can add)"""
        project = self.project_repository.get_by_id(project_id)
        if not project:
            raise ValueError("Project not found")

        # Only owner can add partners
        if not project.is_owner(current_user_id):
            raise PermissionError("Only project owner can add partners")

        # Verify partner user exists
        partner_user = self.user_repository.get_by_id(partner_dto.user_id)
        if not partner_user:
            raise ValueError("User not found")

        # Add partner
        self.project_repository.add_partner(project_id, partner_dto.user_id)

    def is_project_partner(self, project_id: str, user_id: str) -> bool:
        """Check if user is a partner of the project"""
        return self.project_repository.is_partner(project_id, user_id)

    def get_project_partners(self, project_id: str) -> List[str]:
        """Get list of partner IDs for a project"""
        return self.project_repository.get_partners(project_id)
