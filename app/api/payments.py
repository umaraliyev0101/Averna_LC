from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..core.database import get_db
from ..core.dependencies import get_current_admin_or_superadmin
from ..models import User
from ..schemas import PaymentCreate, PaymentUpdate, PaymentResponse, PaginationParams
from ..crud.payment import (
    get_payment, get_payments, create_payment, update_payment, delete_payment,
    get_payments_by_student, get_payments_by_course
)

router = APIRouter()

@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_new_payment(
    payment: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_or_superadmin)
):
    """Create a new payment (admin and superadmin only)"""
    return create_payment(db=db, payment=payment)

@router.get("/", response_model=List[PaymentResponse])
def read_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    student_id: Optional[int] = Query(None),
    course_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_or_superadmin)
):
    """Get list of payments with optional filtering (admin and superadmin only)"""
    if student_id:
        return get_payments_by_student(db=db, student_id=student_id, skip=skip, limit=limit)
    elif course_id:
        return get_payments_by_course(db=db, course_id=course_id, skip=skip, limit=limit)
    else:
        return get_payments(db=db, skip=skip, limit=limit)

@router.get("/{payment_id}", response_model=PaymentResponse)
def read_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_or_superadmin)
):
    """Get payment by ID (admin and superadmin only)"""
    payment = get_payment(db=db, payment_id=payment_id)
    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    return payment

@router.put("/{payment_id}", response_model=PaymentResponse)
def update_existing_payment(
    payment_id: int,
    payment_update: PaymentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_or_superadmin)
):
    """Update payment (admin and superadmin only)"""
    payment = update_payment(db=db, payment_id=payment_id, payment_update=payment_update)
    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    return payment

@router.delete("/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_or_superadmin)
):
    """Delete payment (admin and superadmin only)"""
    success = delete_payment(db=db, payment_id=payment_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
