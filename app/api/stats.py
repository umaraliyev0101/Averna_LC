from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.dependencies import get_current_teacher_or_admin
from ..models import User
from ..schemas import StatsResponse
from ..crud.stats import get_statistics, get_payment_statistics_by_course, get_monthly_statistics

router = APIRouter()

@router.get("/", response_model=StatsResponse)
def read_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher_or_admin)
):
    """Get general statistics (accessible by all roles)"""
    return get_statistics(db=db)

@router.get("/by-course", response_model=dict)
def read_payment_statistics_by_course(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher_or_admin)
):
    """Get payment statistics grouped by course"""
    return get_payment_statistics_by_course(db=db)

@router.get("/monthly/{year}", response_model=dict)
def read_monthly_statistics(
    year: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher_or_admin)
):
    """Get monthly payment statistics for a given year"""
    return get_monthly_statistics(db=db, year=year)
