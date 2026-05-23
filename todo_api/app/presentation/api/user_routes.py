"""User API routes - Authentication endpoints"""

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

from app.application.dto import UserCreateDTO, UserLoginDTO
from app.application.use_cases import UserUseCases
from app.infrastructure.repositories import UserRepository
from app.infrastructure.auth import get_password_service, get_token_service
from app.infrastructure.database import db


router = APIRouter(tags=["Users"])


# Pydantic models for request/response validation
class UserCreateRequest(BaseModel):
    username: str
    password: str
    email: str


class UserLoginRequest(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: str
    username: str
    email: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


def get_user_use_cases() -> UserUseCases:
    """Factory function to create UserUseCases with dependencies"""
    user_repo = UserRepository(database=db)
    password_service = get_password_service()
    token_service = get_token_service()
    return UserUseCases(user_repo, password_service, token_service)


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreateRequest):
    """Register a new user"""
    use_cases = get_user_use_cases()
    
    dto = UserCreateDTO(
        username=user_data.username,
        password=user_data.password,
        email=user_data.email
    )
    
    try:
        result = use_cases.signup(dto)
        return UserResponse(
            id=result.id,
            username=result.username,
            email=result.email
        )
    except ValueError as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/token", response_model=TokenResponse)
async def login(form_data: UserLoginRequest):
    """Login and get access token"""
    use_cases = get_user_use_cases()
    
    dto = UserLoginDTO(
        username=form_data.username,
        password=form_data.password
    )
    
    try:
        result = use_cases.login(dto)
        return TokenResponse(
            access_token=result.access_token,
            token_type=result.token_type
        )
    except ValueError as e:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )
