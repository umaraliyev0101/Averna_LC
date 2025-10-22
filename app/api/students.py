from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..core.database import get_db
from ..core.dependencies import get_current_admin_or_superadmin, get_current_teacher_or_admin
from ..models import User
from ..schemas import StudentCreate, StudentUpdate, StudentResponse
from ..crud.student import (
    get_student, get_students, create_student, update_student, delete_student,
    search_students, get_students_by_course_ids, get_archived_students, get_archived_students_count
)

# Constants
STUDENT_NOT_FOUND_MSG = "Student not found"

router = APIRouter()

@router.post("/", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_new_student(
    student: StudentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_or_superadmin)
):
    """Create a new student (admin and superadmin only)"""
    db_student = create_student(db=db, student=student)
    
    # Convert to response format
    student_data = {
        "id": db_student.id,
        "name": db_student.name,
        "surname": db_student.surname,
        "second_name": db_student.second_name,
        "starting_date": db_student.starting_date,
        "num_lesson": db_student.num_lesson,
        "total_money": db_student.total_money,
        "courses": [course.id for course in db_student.courses],
        "attendance": db_student.get_attendance() or [],
        "is_archived": db_student.is_archived
    }
    return student_data

@router.get("/", response_model=List[StudentResponse])
def read_students(
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=10000),
    name: Optional[str] = Query(None),
    surname: Optional[str] = Query(None),
    course_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher_or_admin)
):
    """Get list of students with optional filtering (teachers, admin and superadmin)"""
    # Check if any search filters are provided
    has_search_filters = name is not None or surname is not None or course_id is not None
    
    # Get students from database based on user role and search filters
    if current_user.role.value == "teacher":
        # Teachers can only see students in their assigned courses
        teacher_course_ids = current_user.get_course_ids()
        if not teacher_course_ids:
            return []  # Teacher has no assigned courses
        
        if has_search_filters:
            # Use search_students and filter by teacher's courses
            all_matching_students = search_students(db=db, name=name, surname=surname, course_id=course_id, skip=0, limit=10000)
            # Filter to only students in teacher's courses
            students = []
            for student in all_matching_students:
                student_course_ids = [course.id for course in student.courses]
                if any(cid in teacher_course_ids for cid in student_course_ids):
                    students.append(student)
            # Apply pagination manually
            students = students[skip:skip + limit]
        else:
            students = get_students_by_course_ids(db=db, course_ids=teacher_course_ids, skip=skip, limit=limit)
    else:
        # Admin and superadmin can see all students
        if has_search_filters:
            # Use search functionality when filters are provided
            students = search_students(db=db, name=name, surname=surname, course_id=course_id, skip=skip, limit=limit)
        else:
            # Get all students without filters
            students = get_students(db=db, skip=skip, limit=limit)
    
    # Convert to response format
    response_data = []
    for student in students:
        student_data = {
            "id": student.id,
            "name": student.name,
            "surname": student.surname,
            "second_name": student.second_name,
            "starting_date": student.starting_date,
            "num_lesson": student.num_lesson,
            "total_money": student.total_money,
            "courses": [course.id for course in student.courses],
            "attendance": student.get_attendance(),
            "is_archived": student.is_archived
        }
        response_data.append(student_data)
    
    return response_data

@router.get("/{student_id}", response_model=StudentResponse)
def read_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher_or_admin)
):
    """Get student by ID (teachers, admin and superadmin)"""
    student = get_student(db=db, student_id=student_id)
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=STUDENT_NOT_FOUND_MSG
        )
    
    # Check if teacher has access to this student
    if current_user.role.value == "teacher":
        teacher_course_ids = current_user.get_course_ids()
        student_course_ids = [course.id for course in student.courses]
        # Check if teacher and student share any courses
        if not any(course_id in teacher_course_ids for course_id in student_course_ids):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You can only view students in your assigned courses"
            )
    
    # Convert to response format
    student_data = {
        "id": student.id,
        "name": student.name,
        "surname": student.surname,
        "second_name": student.second_name,
        "starting_date": student.starting_date,
        "num_lesson": student.num_lesson,
        "total_money": student.total_money,
        "courses": [course.id for course in student.courses],
        "attendance": student.get_attendance(),
        "is_archived": student.is_archived
    }
    return student_data

@router.put("/{student_id}", response_model=StudentResponse)
def update_existing_student(
    student_id: int,
    student_update: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_or_superadmin)
):
    """Update student (admin and superadmin only)"""
    student = update_student(db=db, student_id=student_id, student_update=student_update)
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=STUDENT_NOT_FOUND_MSG
        )
    
    # Convert to response format
    student_data = {
        "id": student.id,
        "name": student.name,
        "surname": student.surname,
        "second_name": student.second_name,
        "starting_date": student.starting_date,
        "num_lesson": student.num_lesson,
        "total_money": student.total_money,
        "courses": [course.id for course in student.courses],
        "attendance": student.get_attendance() or [],
        "is_archived": student.is_archived
    }
    return student_data

@router.delete("/{student_id}")
def delete_existing_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_or_superadmin)
):
    """Archive student instead of deleting (admin and superadmin only)"""
    try:
        success = delete_student(db=db, student_id=student_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=STUDENT_NOT_FOUND_MSG
            )
        
        return {
            "message": "Student archived successfully",
            "student_id": student_id,
            "action": "archived"
        }
        
    except Exception as e:
        # Handle database errors gracefully
        error_msg = str(e).lower()
        if "student_course_progress" in error_msg and "does not exist" in error_msg:
            # This is the missing table error - try to create the table and retry
            try:
                from app.models import Base
                from app.core.database import engine
                Base.metadata.create_all(bind=engine)
                
                # Retry the deletion
                success = delete_student(db=db, student_id=student_id)
                if not success:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=STUDENT_NOT_FOUND_MSG
                    )
                return {
                    "message": "Student archived successfully",
                    "student_id": student_id,
                    "action": "archived"
                }
            except Exception as retry_error:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Database schema error. Please contact administrator. Error: {retry_error}"
                )
        else:
            # Other database errors
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error occurred: {str(e)}"
            )

@router.get("/archived/", response_model=List[StudentResponse])
def read_archived_students(
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=10000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_or_superadmin)
):
    """Get list of archived students (admin and superadmin only)"""
    students = get_archived_students(db=db, skip=skip, limit=limit)
    
    # Convert to response format
    response_data = []
    for student in students:
        student_data = {
            "id": student.id,
            "name": student.name,
            "surname": student.surname,
            "second_name": student.second_name,
            "starting_date": student.starting_date,
            "num_lesson": student.num_lesson,
            "total_money": student.total_money,
            "courses": [course.id for course in student.courses],
            "attendance": student.get_attendance(),
            "is_archived": student.is_archived
        }
        response_data.append(student_data)
    
    return response_data
