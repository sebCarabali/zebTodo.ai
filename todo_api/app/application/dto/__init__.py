"""Data Transfer Objects - Request/Response schemas"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


# User DTOs
@dataclass
class UserCreateDTO:
    username: str
    password: str
    email: str


@dataclass
class UserLoginDTO:
    username: str
    password: str


@dataclass
class UserResponseDTO:
    id: str
    username: str
    email: str
    created_at: datetime


# Project DTOs
@dataclass
class ProjectCreateDTO:
    name: str
    description: Optional[str] = None


@dataclass
class ProjectResponseDTO:
    id: str
    name: str
    description: Optional[str]
    owner_id: str
    created_at: datetime


# Task DTOs
@dataclass
class TaskCreateDTO:
    title: str
    description: Optional[str]
    project_id: str
    assigned_to: Optional[str] = None


@dataclass
class TaskUpdateDTO:
    title: Optional[str] = None
    description: Optional[str] = None
    assigned_to: Optional[str] = None


@dataclass
class TaskResponseDTO:
    id: str
    title: str
    description: Optional[str]
    project_id: str
    assigned_to: Optional[str]
    completed: bool
    created_at: datetime
    completed_at: Optional[datetime] = None
    last_work_duration: Optional[float] = None


# Timer DTOs
@dataclass
class TimerStatusDTO:
    active: bool
    task_id: str
    started_at: Optional[datetime] = None
    elapsed_seconds: Optional[float] = None
    user_id: Optional[str] = None


# Auth DTOs
@dataclass
class TokenDTO:
    access_token: str
    token_type: str = "bearer"


# Partner DTOs
@dataclass
class PartnerAddDTO:
    user_id: str
