from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import date, datetime
from typing import Dict

from ..models import Payment, Student, Course
from ..schemas import StatsResponse
from .payment import get_total_payments, get_monthly_payments
from .student import get_students_count

def get_total_student_money(db: Session) -> float:
    """Get total money from all students' total_money field"""
    result = db.query(func.sum(Student.total_money)).scalar()
    return float(result) if result is not None else 0.0

def get_statistics(db: Session) -> StatsResponse:
    """Get comprehensive statistics"""
    current_date = datetime.now()
    current_year = current_date.year
    current_month = current_date.month
    
    # Total money from all students (reflects all money in the system)
    total_money = get_total_student_money(db)
    
    # Monthly money (current month payments)
    monthly_money = get_monthly_payments(db, current_year, current_month)
    
    # Total students
    total_students = get_students_count(db)
    
    # Calculate unpaid amounts (simplified - assume no debt tracking for now)
    # In a real system, you'd have expected payments vs actual payments
    unpaid = 0.0
    monthly_unpaid = 0.0
    
    return StatsResponse(
        total_money=total_money,
        monthly_money=monthly_money,
        unpaid=unpaid,
        monthly_unpaid=monthly_unpaid,
        total_students=total_students
    )

def get_payment_statistics_by_course(db: Session) -> Dict[str, float]:
    """Get payment statistics grouped by course"""
    results = db.query(
        Course.name,
        func.sum(Payment.money).label('total_amount')
    ).join(Payment, Course.id == Payment.course_id).group_by(Course.name).all()
    
    return {course_name: float(total_amount) for course_name, total_amount in results}

def get_monthly_statistics(db: Session, year: int) -> Dict[int, float]:
    """Get monthly payment statistics for a given year"""
    results = db.query(
        extract('month', Payment.date).label('month'),
        func.sum(Payment.money).label('total_amount')
    ).filter(extract('year', Payment.date) == year).group_by(
        extract('month', Payment.date)
    ).all()
    
    # Initialize all months with 0
    monthly_stats = {month: 0.0 for month in range(1, 13)}
    
    # Update with actual data
    for month, total_amount in results:
        monthly_stats[int(month)] = float(total_amount)
    
    return monthly_stats

def get_student_payment_summary(db: Session, student_id: int):
    """Get payment summary for a specific student"""
    result = db.query(func.sum(Payment.money)).filter(Payment.student_id == student_id).scalar()
    total_paid = float(result) if result is not None else 0.0
    
    # Get student's courses and calculate expected payment
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        return {"total_paid": 0.0, "expected_payment": 0.0, "balance": 0.0}
    
    expected_payment = student.total_money if student.total_money is not None else 0.0
    balance = expected_payment - total_paid
    
    return {
        "total_paid": total_paid,
        "expected_payment": expected_payment,
        "balance": balance
    }
