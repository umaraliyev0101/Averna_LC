from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional

from ..core.database import get_db
from ..core.dependencies import get_current_teacher_or_admin
from ..models import User
from ..schemas import AttendanceCheck, AttendanceUpdate
from ..crud.student import get_student, add_attendance_record, update_attendance_record, delete_attendance_record

router = APIRouter()

@router.post("/check", response_model=dict)
def check_attendance(
    attendance: AttendanceCheck,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher_or_admin)
):
    """
    Check attendance for a student (accessible by teachers, admins, and superadmins)
    """
    # Verify student exists
    student = get_student(db, attendance.student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Add attendance record
    updated_student = add_attendance_record(
        db=db,
        student_id=attendance.student_id,
        date=attendance.date,
        is_absent=attendance.isAbsent,
        reason=attendance.reason or "",
        course_id=attendance.course_id
    )
    
    if not updated_student:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to add attendance record"
        )
    
    return {
        "message": "Attendance recorded successfully",
        "student_id": attendance.student_id,
        "course_id": attendance.course_id,
        "date": attendance.date,
        "isAbsent": attendance.isAbsent,
        "reason": attendance.reason
    }

@router.get("/student/{student_id}", response_model=list)
def get_student_attendance(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher_or_admin)
):
    """
    Get attendance records for a specific student
    """
    student = get_student(db, student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    return student.get_attendance()

@router.put("/student/{student_id}")
def update_student_attendance(
    student_id: int,
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    course_id: Optional[int] = Query(None, description="Course ID (optional)"),
    attendance_update: AttendanceUpdate = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher_or_admin)
):
    """
    Update a specific attendance record for a student
    """
    from datetime import datetime
    
    # Parse the date
    try:
        attendance_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    
    # Verify student exists
    student = get_student(db, student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Update attendance record
    updated_student = update_attendance_record(
        db=db,
        student_id=student_id,
        date=attendance_date,
        course_id=course_id,
        is_absent=attendance_update.isAbsent if attendance_update else None,
        reason=attendance_update.reason if attendance_update else None
    )
    
    if not updated_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance record not found for the specified date and course"
        )
    
    return {
        "message": "Attendance record updated successfully",
        "student_id": student_id,
        "date": date,
        "course_id": course_id,
        "isAbsent": attendance_update.isAbsent if attendance_update else None,
        "reason": attendance_update.reason if attendance_update else None
    }

@router.delete("/student/{student_id}")
def delete_student_attendance(
    student_id: int,
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    course_id: Optional[int] = Query(None, description="Course ID (optional)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher_or_admin)
):
    """
    Delete a specific attendance record for a student
    """
    from datetime import datetime
    
    # Parse the date
    try:
        attendance_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    
    # Verify student exists
    student = get_student(db, student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Delete attendance record
    updated_student = delete_attendance_record(
        db=db,
        student_id=student_id,
        date=attendance_date,
        course_id=course_id
    )
    
    if not updated_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance record not found for the specified date and course"
        )
    
    return {
        "message": "Attendance record deleted successfully",
        "student_id": student_id,
        "date": date,
        "course_id": course_id
    }
