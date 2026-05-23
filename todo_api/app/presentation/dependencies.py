"""FastAPI dependencies for authentication and authorization"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.infrastructure.auth import get_token_service
from app.infrastructure.repositories import UserRepository
from app.infrastructure.database import db


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_user_repository() -> UserRepository:
    """Get user repository instance"""
    return UserRepository(database=db)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repo: UserRepository = Depends(get_user_repository),
    token_service=None  # Lazy init
) -> dict:
    """
    Get current authenticated user from JWT token.
    Returns user dict for backward compatibility.
    """
    if token_service is None:
        token_service = get_token_service()

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Decode token
    user_id = token_service.decode_token(token)
    if user_id is None:
        raise credentials_exception

    # Get user from repository
    user = user_repo.get_by_id(user_id)
    if user is None:
        raise credentials_exception

    # Return user dict for API compatibility
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email
    }
