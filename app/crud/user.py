from sqlalchemy.orm import Session
from sqlalchemy import and_, extract, func
from typing import List, Optional
from datetime import date, datetime
import json

from ..models import User, UserRole
from ..schemas import UserCreate, UserUpdate
from ..core.auth import get_password_hash

def get_user(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username"""
    return db.query(User).filter(User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Get list of users with pagination"""
    return db.query(User).offset(skip).limit(limit).all()

def sync_user_courses(db: Session, user: User, course_ids: List[int]):
    """Sync user's course relationships with the many-to-many table"""
    from ..models import Course
    
    # Clear existing course relationships
    user.courses.clear()
    
    # Add new course relationships
    user_role_value = user.role.value if hasattr(user.role, 'value') else str(user.role)
    if course_ids and user_role_value == UserRole.TEACHER.value:
        courses = db.query(Course).filter(Course.id.in_(course_ids)).all()
        for course in courses:
            user.courses.append(course)

def create_user(db: Session, user: UserCreate) -> User:
    """Create new user"""
    hashed_password = get_password_hash(user.password)
    
    # Set course_ids based on role
    course_ids = []
    if user.role == UserRole.TEACHER and user.course_ids:
        course_ids = user.course_ids
    elif user.role in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        course_ids = []  # Admin and superadmin should not have courses
    
    db_user = User(
        username=user.username,
        hashed_password=hashed_password,
        role=user.role
    )
    db_user.set_course_ids(course_ids)
    
    db.add(db_user)
    db.commit()
    
    # Sync the many-to-many relationships
    sync_user_courses(db, db_user, course_ids)
    db.commit()
    
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
    """Update user"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return None
    
    update_data = user_update.dict(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    # Handle role change first
    if "role" in update_data:
        new_role = update_data.pop("role")
        db_user.role = new_role
        if new_role in [UserRole.ADMIN, UserRole.SUPERADMIN]:
            db_user.set_course_ids([])  # Clear courses for admin/superadmin
    
    # Handle course_ids update
    if "course_ids" in update_data:
        course_ids = update_data.pop("course_ids")
        # Set course_ids based on current role
        current_role_value = db_user.role.value if hasattr(db_user.role, 'value') else str(db_user.role)
        if current_role_value in [UserRole.ADMIN.value, UserRole.SUPERADMIN.value]:
            final_course_ids = []
        elif current_role_value == UserRole.TEACHER.value:
            final_course_ids = course_ids if course_ids else []
        else:
            final_course_ids = []
        
        db_user.set_course_ids(final_course_ids)
        # Sync the many-to-many relationships
        sync_user_courses(db, db_user, final_course_ids)
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int) -> bool:
    """Delete user"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return False
    
    try:
        db.delete(db_user)
        db.commit()
        return True
        
    except Exception as e:
        db.rollback()
        print(f"Error deleting user: {e}")
        return False
