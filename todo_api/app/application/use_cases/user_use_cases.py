"""User use cases - Authentication and user management"""

import uuid
from datetime import datetime, timedelta
from typing import Optional, Tuple
from jose import jwt

from app.domain.entities import User
from app.domain.repositories import IUserRepository
from app.application.dto import (
    UserCreateDTO, UserLoginDTO, UserResponseDTO, TokenDTO
)


class UserUseCases:
    """Use cases for user operations following SRP"""

    def __init__(
        self,
        user_repository: IUserRepository,
        password_service: 'PasswordService',
        token_service: 'TokenService'
    ):
        self.user_repository = user_repository
        self.password_service = password_service
        self.token_service = token_service

    def signup(self, dto: UserCreateDTO) -> UserResponseDTO:
        """Register a new user"""
        # Check if username exists
        existing_user = self.user_repository.get_by_username(dto.username)
        if existing_user:
            raise ValueError("Username already registered")

        # Create user entity
        password_hash = self.password_service.hash_password(dto.password)
        user = User(
            id=str(uuid.uuid4()),
            username=dto.username,
            email=dto.email,
            password_hash=password_hash
        )

        # Save user
        self.user_repository.add(user)

        # Return response DTO (without password)
        return UserResponseDTO(
            id=user.id,
            username=user.username,
            email=user.email,
            created_at=user.created_at
        )

    def login(self, dto: UserLoginDTO) -> TokenDTO:
        """Authenticate user and return access token"""
        # Get user by username
        user = self.user_repository.get_by_username(dto.username)
        if not user:
            raise ValueError("Invalid credentials")

        # Verify password
        if not self.password_service.verify_password(dto.password, user.password_hash):
            raise ValueError("Invalid credentials")

        # Generate access token
        access_token = self.token_service.create_access_token(user.id)

        return TokenDTO(access_token=access_token)

    def get_user_by_id(self, user_id: str) -> Optional[UserResponseDTO]:
        """Get user by ID"""
        user = self.user_repository.get_by_id(user_id)
        if not user:
            return None

        return UserResponseDTO(
            id=user.id,
            username=user.username,
            email=user.email,
            created_at=user.created_at
        )


class PasswordService:
    """Service for password hashing and verification - Single Responsibility"""

    def __init__(self, pwd_context):
        self.pwd_context = pwd_context

    def hash_password(self, password: str) -> str:
        """Hash a plain text password"""
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return self.pwd_context.verify(plain_password, hashed_password)


class TokenService:
    """Service for JWT token operations - Single Responsibility"""

    def __init__(self, secret_key: str, algorithm: str, expire_minutes: int = 30):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.expire_minutes = expire_minutes

    def create_access_token(self, user_id: str) -> str:
        """Create JWT access token"""
        expire_delta = timedelta(minutes=self.expire_minutes)
        expire = datetime.utcnow() + expire_delta

        payload = {
            "sub": user_id,
            "exp": expire
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def decode_token(self, token: str) -> Optional[str]:
        """Decode JWT token and return user ID"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload.get("sub")
        except Exception:
            return None
