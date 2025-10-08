from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..core.database import get_db
from ..core.dependencies import get_current_teacher_or_admin
from ..models import User
from ..schemas import AttendanceCheck
from ..crud.student import get_student, add_attendance_record

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
        reason=attendance.reason,
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
