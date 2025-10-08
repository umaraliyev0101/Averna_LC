from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from ..core.database import get_db
from ..core.dependencies import get_current_admin_or_superadmin, get_current_teacher_or_admin
from ..models import User
from ..schemas import CourseCreate, CourseUpdate, CourseResponse
from ..crud.course import (
    get_course, get_courses, create_course, update_course, delete_course, get_courses_by_ids
)

# Constants
COURSE_NOT_FOUND_MSG = "Course not found"

router = APIRouter()

@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_new_course(
    course: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_or_superadmin)
):
    """Create a new course (admin and superadmin only)"""
    created_course = create_course(db=db, course=course)
    
    # Convert to response format
    course_data = {
        "id": created_course.id,
        "name": created_course.name,
        "week_days": created_course.get_week_days(),  # Parse JSON to list
        "lesson_per_month": created_course.lesson_per_month,
        "cost": created_course.cost
    }
    return course_data

@router.get("/", response_model=List[CourseResponse])
def read_courses(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher_or_admin)
):
    """Get list of courses (teachers, admin and superadmin)"""
    # Get courses based on user role
    if current_user.role.value == "teacher":
        # Teachers can only see their assigned courses
        teacher_course_ids = current_user.get_course_ids()
        if not teacher_course_ids:
            return []  # Teacher has no assigned courses
        courses = get_courses_by_ids(db=db, course_ids=teacher_course_ids)
    else:
        # Admin and superadmin can see all courses
        courses = get_courses(db=db, skip=skip, limit=limit)
    
    # Convert to response format
    response_data = []
    for course in courses:
        course_data = {
            "id": course.id,
            "name": course.name,
            "week_days": course.get_week_days(),  # Parse JSON to list
            "lesson_per_month": course.lesson_per_month,
            "cost": course.cost
        }
        response_data.append(course_data)
    
    return response_data

@router.get("/{course_id}", response_model=CourseResponse)
def read_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher_or_admin)
):
    """Get course by ID (teachers, admin and superadmin)"""
    course = get_course(db=db, course_id=course_id)
    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=COURSE_NOT_FOUND_MSG
        )
    
    # Check if teacher has access to this course
    if current_user.role.value == "teacher":
        teacher_course_ids = current_user.get_course_ids()
        if course_id not in teacher_course_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You can only view courses assigned to you"
            )
    
    # Convert to response format
    course_data = {
        "id": course.id,
        "name": course.name,
        "week_days": course.get_week_days(),  # Parse JSON to list
        "lesson_per_month": course.lesson_per_month,
        "cost": course.cost
    }
    return course_data

@router.put("/{course_id}", response_model=CourseResponse)
def update_existing_course(
    course_id: int,
    course_update: CourseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_or_superadmin)
):
    """Update course (admin and superadmin only)"""
    course = update_course(db=db, course_id=course_id, course_update=course_update)
    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=COURSE_NOT_FOUND_MSG
        )
    
    # Convert to response format
    course_data = {
        "id": course.id,
        "name": course.name,
        "week_days": course.get_week_days(),  # Parse JSON to list
        "lesson_per_month": course.lesson_per_month,
        "cost": course.cost
    }
    return course_data

@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_or_superadmin)
):
    """Delete course (admin and superadmin only)"""
    try:
        success = delete_course(db=db, course_id=course_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=COURSE_NOT_FOUND_MSG
            )
    except Exception as e:
        # Handle database constraint errors
        error_msg = str(e).lower()
        if "constraint" in error_msg or "foreign key" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot delete course: It has associated students, payments, or teachers. Please remove these associations first."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error occurred: {str(e)}"
            )
