from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from ..core.database import get_db
from ..core.dependencies import get_current_superadmin
from ..models import User
from ..schemas import UserCreate, UserUpdate, UserResponse
from ..crud.user import (
    get_user, get_users, create_user, update_user, delete_user,
    get_user_by_username
)

# Constants
USER_NOT_FOUND_MSG = "User not found"
USERNAME_ALREADY_EXISTS_MSG = "Username already registered"

router = APIRouter()

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_new_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superadmin)
):
    """Create a new user (superadmin only)"""
    # Check if username already exists
    existing_user = get_user_by_username(db=db, username=user.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=USERNAME_ALREADY_EXISTS_MSG
        )
    
    return create_user(db=db, user=user)

@router.get("/", response_model=List[UserResponse])
def read_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superadmin)
):
    """Get list of users (superadmin only)"""
    return get_users(db=db, skip=skip, limit=limit)

@router.get("/{user_id}", response_model=UserResponse)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superadmin)
):
    """Get user by ID (superadmin only)"""
    user = get_user(db=db, user_id=user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=USER_NOT_FOUND_MSG
        )
    return user

@router.put("/{user_id}", response_model=UserResponse)
def update_existing_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superadmin)
):
    """Update user (superadmin only)"""
    # Check if username is being changed and already exists
    if user_update.username:
        existing_user = get_user_by_username(db=db, username=user_update.username)
        if existing_user is not None and getattr(existing_user, 'id', None) != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=USERNAME_ALREADY_EXISTS_MSG
            )
    
    user = update_user(db=db, user_id=user_id, user_update=user_update)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=USER_NOT_FOUND_MSG
        )
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superadmin)
):
    """Delete user (superadmin only)"""
    try:
        success = delete_user(db=db, user_id=user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=USER_NOT_FOUND_MSG
            )
    except Exception as e:
        # Handle database constraint errors
        error_msg = str(e).lower()
        if "constraint" in error_msg or "foreign key" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot delete user: User may have associated data. Please remove associations first."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error occurred: {str(e)}"
            )
