"""
Monthly debt management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from datetime import date, datetime

from ..core.database import get_db
from ..core.dependencies import get_current_admin_or_superadmin
from ..models import User, Student, Course, Payment, StudentCourseProgress

router = APIRouter()

# Constants for error messages
STUDENT_NOT_FOUND = "Student not found"
COURSE_NOT_FOUND = "Course not found"
ENROLLMENT_NOT_FOUND = "Student not enrolled in this course"

@router.get("/student/{student_id}/monthly-debt")
def calculate_monthly_debt(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_or_superadmin)
):
    """Calculate student debt based on monthly course fees"""
    
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail=STUDENT_NOT_FOUND)
    
    total_monthly_owed = 0
    course_breakdown = []
    
    # Get student's course progress
    for progress in db.query(StudentCourseProgress).filter(
        StudentCourseProgress.student_id == student_id
    ).all():
        course = progress.course
        months_enrolled = progress.calculate_months_enrolled()
        total_owed_for_course = course.cost * months_enrolled
        total_monthly_owed += total_owed_for_course
        
        course_breakdown.append({
            "course_id": course.id,
            "course_name": course.name,
            "monthly_fee": course.cost,
            "months_enrolled": months_enrolled,
            "lessons_attended": progress.lessons_attended,
            "expected_lessons": course.lesson_per_month * months_enrolled,
            "total_owed_for_course": total_owed_for_course,
            "enrollment_date": progress.enrollment_date
        })
    
    # Calculate balance
    total_paid = sum(payment.money for payment in student.payments)
    balance = total_paid - total_monthly_owed
    
    return {
        "student_id": student_id,
        "student_name": f"{student.name} {student.surname}",
        "course_breakdown": course_breakdown,
        "total_monthly_owed": total_monthly_owed,
        "total_paid": total_paid,
        "balance": balance,
        "owes_money": balance < 0,
        "debt_amount": abs(balance) if balance < 0 else 0,
        "overpaid_amount": balance if balance > 0 else 0
    }

@router.post("/student/{student_id}/enroll-course")
def enroll_student_in_course(
    student_id: int,
    course_id: int,
    enrollment_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_or_superadmin)
):
    """Enroll student in a course (starts monthly billing)"""
    
    enrollment_date_obj = None
    if enrollment_date:
        enrollment_date_obj = datetime.strptime(enrollment_date, "%Y-%m-%d").date()
    else:
        enrollment_date_obj = date.today()
    
    # Verify student and course exist
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Check if already enrolled
    existing = db.query(StudentCourseProgress).filter(
        StudentCourseProgress.student_id == student_id,
        StudentCourseProgress.course_id == course_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Student already enrolled in this course")
    
    # Create progress record
    progress = StudentCourseProgress(
        student_id=student_id,
        course_id=course_id,
        enrollment_date=enrollment_date_obj,
        lessons_attended=0
    )
    db.add(progress)
    
    # Add to student-course relationship if not already there
    if course not in student.courses:
        student.courses.append(course)
    
    db.commit()
    
    return {
        "message": "Student enrolled successfully",
        "student_id": student_id,
        "course_id": course_id,
        "course_name": course.name,
        "enrollment_date": enrollment_date_obj,
        "monthly_fee": course.cost
    }

@router.put("/student/{student_id}/course/{course_id}/add-lessons")
def add_lessons_to_course(
    student_id: int,
    course_id: int,
    lessons_count: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_or_superadmin)
):
    """Add lessons attended for specific course"""
    
    progress = db.query(StudentCourseProgress).filter(
        StudentCourseProgress.student_id == student_id,
        StudentCourseProgress.course_id == course_id
    ).first()
    
    if not progress:
        raise HTTPException(status_code=404, detail="Student not enrolled in this course")
    
    # Update lessons attended
    new_lesson_count = progress.lessons_attended + lessons_count
    db.query(StudentCourseProgress).filter(
        StudentCourseProgress.student_id == student_id,
        StudentCourseProgress.course_id == course_id
    ).update({"lessons_attended": new_lesson_count})
    
    # Update student's total lesson count
    student = db.query(Student).filter(Student.id == student_id).first()
    if student:
        new_total_lessons = student.num_lesson + lessons_count
        db.query(Student).filter(Student.id == student_id).update({"num_lesson": new_total_lessons})
    else:
        new_total_lessons = lessons_count
    
    db.commit()
    
    return {
        "message": f"Added {lessons_count} lessons",
        "course_lessons_attended": new_lesson_count,
        "total_lessons_attended": new_total_lessons
    }

@router.get("/monthly-summary")
def get_monthly_debt_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_or_superadmin)
):
    """Get monthly debt summary for all students"""
    
    summary = []
    total_debt = 0
    
    students = db.query(Student).all()
    
    for student in students:
        student_monthly_owed = 0
        
        # Calculate monthly debt for this student
        for progress in db.query(StudentCourseProgress).filter(
            StudentCourseProgress.student_id == student.id
        ).all():
            student_monthly_owed += progress.calculate_owed_amount()
        
        total_paid = sum(payment.money for payment in student.payments)
        balance = total_paid - student_monthly_owed
        debt = abs(balance) if balance < 0 else 0
        total_debt += debt
        
        summary.append({
            "student_id": student.id,
            "student_name": f"{student.name} {student.surname}",
            "monthly_owed": student_monthly_owed,
            "total_paid": total_paid,
            "debt": debt,
            "balance": balance
        })
    
    return {
        "students": summary,
        "total_debt_all_students": total_debt,
        "students_with_debt": len([s for s in summary if s["debt"] > 0])
    }

@router.post("/student/{student_id}/payment")
def record_payment(
    student_id: int,
    course_id: int,
    amount: float,
    description: str = "Monthly payment",
    payment_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_or_superadmin)
):
    """Record a payment for a student"""
    
    payment_date_obj = None
    if payment_date:
        payment_date_obj = datetime.strptime(payment_date, "%Y-%m-%d").date()
    else:
        payment_date_obj = date.today()
    
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Create payment record
    payment = Payment(
        student_id=student_id,
        course_id=course_id,
        money=amount,
        date=payment_date_obj,
        description=description
    )
    db.add(payment)
    
    # Update student's total_money
    new_total_money = student.total_money + amount
    db.query(Student).filter(Student.id == student_id).update({"total_money": new_total_money})
    
    db.commit()
    db.refresh(payment)
    
    # Refresh student record and calculate updated balance
    db.refresh(student)
    student_monthly_owed = 0
    for progress in db.query(StudentCourseProgress).filter(
        StudentCourseProgress.student_id == student_id
    ).all():
        student_monthly_owed += progress.calculate_owed_amount()
    
    # Calculate balance using simple arithmetic
    total_paid = float(student.total_money) if student.total_money else 0.0
    balance_amount = total_paid - student_monthly_owed
    still_owes = balance_amount < 0
    remaining_debt = abs(balance_amount) if still_owes else 0.0
    
    return {
        "payment_id": payment.id,
        "amount": amount,
        "description": description,
        "payment_date": payment_date_obj,
        "student_balance": balance_amount,
        "still_owes": still_owes,
        "remaining_debt": remaining_debt
    }

@router.get("/course/{course_id}/students-debt")
def get_course_students_debt(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_or_superadmin)
):
    """Get debt status for all students in a specific course"""
    
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    students_debt = []
    total_course_debt = 0
    
    # Get all students enrolled in this course
    progress_records = db.query(StudentCourseProgress).filter(
        StudentCourseProgress.course_id == course_id
    ).all()
    
    for progress in progress_records:
        student = progress.student
        course_owed = progress.calculate_owed_amount()
        
        # Calculate payments made for this specific course
        course_payments = sum(
            payment.money for payment in student.payments 
            if payment.course_id == course_id
        )
        
        balance = course_payments - course_owed
        debt = abs(balance) if balance < 0 else 0
        total_course_debt += debt
        
        students_debt.append({
            "student_id": student.id,
            "student_name": f"{student.name} {student.surname}",
            "months_enrolled": progress.calculate_months_enrolled(),
            "lessons_attended": progress.lessons_attended,
            "expected_lessons": course.lesson_per_month * progress.calculate_months_enrolled(),
            "course_owed": course_owed,
            "course_payments": course_payments,
            "balance": balance,
            "debt": debt
        })
    
    return {
        "course_id": course_id,
        "course_name": course.name,
        "monthly_fee": course.cost,
        "students": students_debt,
        "total_course_debt": total_course_debt,
        "students_with_debt": len([s for s in students_debt if s["debt"] > 0])
    }
