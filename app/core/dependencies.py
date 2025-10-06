from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from .database import get_db
from ..models import User, UserRole

# JWT token authentication
security = HTTPBearer()

def verify_token(token: str):
    """Verify JWT token and extract user data - placeholder"""
    # This will be implemented in auth.py to avoid circular imports
    pass

def get_current_user_dependency(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    # Import here to avoid circular imports
    from .auth import verify_token as auth_verify_token
    
    token = credentials.credentials
    token_data = auth_verify_token(token)
    
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def require_role(allowed_roles: list):
    """Decorator to check if user has required role"""
    def role_checker(current_user: User = Depends(get_current_user_dependency)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted"
            )
        return current_user
    return role_checker

# Role-based dependency shortcuts
def get_current_teacher_or_admin(current_user: User = Depends(require_role([UserRole.TEACHER, UserRole.ADMIN, UserRole.SUPERADMIN]))):
    return current_user

def get_current_admin_or_superadmin(current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SUPERADMIN]))):
    return current_user

def get_current_superadmin(current_user: User = Depends(require_role([UserRole.SUPERADMIN]))):
    return current_user
