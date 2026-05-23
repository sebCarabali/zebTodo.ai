"""Authentication infrastructure"""

from passlib.context import CryptContext
from app.application.use_cases.user_use_cases import PasswordService, TokenService

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_service() -> PasswordService:
    """Get password service instance"""
    return PasswordService(pwd_context=pwd_context)

def get_token_service(
    secret_key: str = "your-secret-key-change-in-production",
    algorithm: str = "HS256",
    expire_minutes: int = 30
) -> TokenService:
    """Get token service instance"""
    return TokenService(
        secret_key=secret_key,
        algorithm=algorithm,
        expire_minutes=expire_minutes
    )

__all__ = ["pwd_context", "get_password_service", "get_token_service"]
