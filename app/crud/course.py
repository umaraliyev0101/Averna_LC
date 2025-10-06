from sqlalchemy.orm import Session
from sqlalchemy import and_, extract, func
from typing import List, Optional
from datetime import date
import json

from ..models import Course
from ..schemas import CourseCreate, CourseUpdate

def get_course(db: Session, course_id: int) -> Optional[Course]:
    """Get course by ID"""
    return db.query(Course).filter(Course.id == course_id).first()

def get_courses(db: Session, skip: int = 0, limit: int = 100) -> List[Course]:
    """Get list of courses with pagination"""
    return db.query(Course).offset(skip).limit(limit).all()

def create_course(db: Session, course: CourseCreate) -> Course:
    """Create new course"""
    db_course = Course(
        name=course.name,
        lesson_per_month=course.lesson_per_month,
        cost=course.cost
    )
    db_course.set_week_days(course.week_days)
    
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

def update_course(db: Session, course_id: int, course_update: CourseUpdate) -> Optional[Course]:
    """Update course"""
    db_course = db.query(Course).filter(Course.id == course_id).first()
    if not db_course:
        return None
    
    update_data = course_update.dict(exclude_unset=True)
    
    if "week_days" in update_data:
        db_course.set_week_days(update_data.pop("week_days"))
    
    for field, value in update_data.items():
        setattr(db_course, field, value)
    
    db.commit()
    db.refresh(db_course)
    return db_course

def delete_course(db: Session, course_id: int) -> bool:
    """Delete course"""
    db_course = db.query(Course).filter(Course.id == course_id).first()
    if not db_course:
        return False
    
    db.delete(db_course)
    db.commit()
    return True

def get_courses_count(db: Session) -> int:
    """Get total count of courses"""
    return db.query(Course).count()
