from sqlalchemy.orm import Session
from sqlalchemy import and_, extract, func
from typing import List, Optional
from datetime import date

from ..models import Payment, Student, Course
from ..schemas import PaymentCreate, PaymentUpdate

def get_payment(db: Session, payment_id: int) -> Optional[Payment]:
    """Get payment by ID"""
    return db.query(Payment).filter(Payment.id == payment_id).first()

def get_payments(db: Session, skip: int = 0, limit: int = 100) -> List[Payment]:
    """Get list of payments with pagination"""
    return db.query(Payment).offset(skip).limit(limit).all()

def create_payment(db: Session, payment: PaymentCreate) -> Payment:
    """Create new payment"""
    db_payment = Payment(
        money=payment.money,
        date=payment.date,
        student_id=payment.student_id,
        course_id=payment.course_id,
        description=payment.description or ""
    )
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment

def update_payment(db: Session, payment_id: int, payment_update: PaymentUpdate) -> Optional[Payment]:
    """Update payment"""
    db_payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not db_payment:
        return None
    
    update_data = payment_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_payment, field, value)
    
    db.commit()
    db.refresh(db_payment)
    return db_payment

def delete_payment(db: Session, payment_id: int) -> bool:
    """Delete payment"""
    db_payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not db_payment:
        return False
    
    try:
        db.delete(db_payment)
        db.commit()
        return True
        
    except Exception as e:
        db.rollback()
        print(f"Error deleting payment: {e}")
        return False

def get_payments_by_student(db: Session, student_id: int, skip: int = 0, limit: int = 100) -> List[Payment]:
    """Get payments by student ID"""
    return db.query(Payment).filter(Payment.student_id == student_id).offset(skip).limit(limit).all()

def get_payments_by_course(db: Session, course_id: int, skip: int = 0, limit: int = 100) -> List[Payment]:
    """Get payments by course ID"""
    return db.query(Payment).filter(Payment.course_id == course_id).offset(skip).limit(limit).all()

def get_payments_by_date_range(db: Session, start_date: date, end_date: date, skip: int = 0, limit: int = 100) -> List[Payment]:
    """Get payments within date range"""
    return db.query(Payment).filter(
        and_(Payment.date >= start_date, Payment.date <= end_date)
    ).offset(skip).limit(limit).all()

def get_total_payments(db: Session) -> float:
    """Get total amount of all payments"""
    result = db.query(func.sum(Payment.money)).scalar()
    return result or 0.0

def get_monthly_payments(db: Session, year: int, month: int) -> float:
    """Get total payments for a specific month"""
    result = db.query(func.sum(Payment.money)).filter(
        and_(
            extract('year', Payment.date) == year,
            extract('month', Payment.date) == month
        )
    ).scalar()
    return result or 0.0

def get_payments_count(db: Session) -> int:
    """Get total count of payments"""
    return db.query(Payment).count()
