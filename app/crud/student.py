from sqlalchemy.orm import Session
from sqlalchemy import and_, extract, func
from typing import List, Optional
from datetime import date
import json

from ..models import Student, Course, student_courses
from ..schemas import StudentCreate, StudentUpdate, AttendanceRecord

def get_student(db: Session, student_id: int) -> Optional[Student]:
    """Get student by ID"""
    return db.query(Student).filter(Student.id == student_id).first()

def get_students(db: Session, skip: int = 0, limit: int = 100) -> List[Student]:
    """Get list of students with pagination (excluding archived)"""
    return db.query(Student).filter(Student.is_archived == False).offset(skip).limit(limit).all()

def create_student(db: Session, student: StudentCreate) -> Student:
    """Create new student"""
    db_student = Student(
        name=student.name,
        surname=student.surname,
        second_name=student.second_name,
        starting_date=student.starting_date,
        num_lesson=student.num_lesson,
        total_money=student.total_money
    )
    
    # Set attendance - always set to empty list if not provided
    if student.attendance:
        attendance_data = [
            {
                "date": str(record.date),
                "isAbsent": record.isAbsent,
                "reason": record.reason
            }
            for record in student.attendance
        ]
        db_student.set_attendance(attendance_data)
    else:
        # Ensure attendance is set to empty list
        db_student.set_attendance([])
    
    db.add(db_student)
    db.commit()
    
    # Add course relationships
    if student.courses:
        courses = db.query(Course).filter(Course.id.in_(student.courses)).all()
        db_student.courses = courses
        db.commit()
    
    db.refresh(db_student)
    return db_student

def update_student(db: Session, student_id: int, student_update: StudentUpdate) -> Optional[Student]:
    """Update student"""
    db_student = db.query(Student).filter(Student.id == student_id).first()
    if not db_student:
        return None
    
    update_data = student_update.dict(exclude_unset=True)
    
    # Handle courses relationship
    if "courses" in update_data:
        course_ids = update_data.pop("courses")
        courses = db.query(Course).filter(Course.id.in_(course_ids)).all()
        db_student.courses = courses
    
    # Handle attendance
    if "attendance" in update_data:
        attendance_records = update_data.pop("attendance")
        attendance_data = [
            {
                "date": str(record.date),
                "isAbsent": record.isAbsent,
                "reason": record.reason
            }
            for record in attendance_records
        ]
        db_student.set_attendance(attendance_data)
    
    # Update other fields
    for field, value in update_data.items():
        setattr(db_student, field, value)
    
    db.commit()
    db.refresh(db_student)
    return db_student

def delete_student(db: Session, student_id: int) -> bool:
    """Archive student instead of deleting (mark as archived)"""
    db_student = db.query(Student).filter(Student.id == student_id).first()
    if not db_student:
        return False
    
    try:
        # Mark student as archived instead of deleting
        db_student.is_archived = True
        db.commit()
        db.refresh(db_student)
        return True
        
    except Exception as e:
        db.rollback()
        print(f"Error archiving student: {e}")
        return False

def add_attendance_record(db: Session, student_id: int, date: date, is_absent: bool = False, reason: str = "", course_id: Optional[int] = None) -> Optional[Student]:
    """Add attendance record to student"""
    db_student = db.query(Student).filter(Student.id == student_id).first()
    if not db_student:
        return None
    
    db_student.add_attendance_record(date, is_absent, reason, course_id, db)
    db.commit()
    db.refresh(db_student)
    return db_student

def get_students_count(db: Session) -> int:
    """Get total count of students (excluding archived)"""
    return db.query(Student).filter(Student.is_archived == False).count()

def search_students(db: Session, name: Optional[str] = None, surname: Optional[str] = None, course_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[Student]:
    """Search students by name, surname, or course (excluding archived)"""
    query = db.query(Student).filter(Student.is_archived == False)
    
    if name:
        query = query.filter(Student.name.ilike(f"%{name}%"))
    if surname:
        query = query.filter(Student.surname.ilike(f"%{surname}%"))
    if course_id:
        query = query.join(Student.courses).filter(Course.id == course_id)
    
    return query.offset(skip).limit(limit).all()

def get_students_by_course_ids(db: Session, course_ids: List[int], skip: int = 0, limit: int = 100) -> List[Student]:
    """Get students who are enrolled in any of the specified courses (excluding archived)"""
    if not course_ids:
        return []
    
    return db.query(Student).filter(Student.is_archived == False).join(Student.courses).filter(Course.id.in_(course_ids)).distinct().offset(skip).limit(limit).all()

def get_archived_students(db: Session, skip: int = 0, limit: int = 100) -> List[Student]:
    """Get list of archived students"""
    return db.query(Student).filter(Student.is_archived == True).offset(skip).limit(limit).all()

def get_archived_students_count(db: Session) -> int:
    """Get total count of archived students"""
    return db.query(Student).filter(Student.is_archived == True).count()

def update_attendance_record(db: Session, student_id: int, date: date, course_id: Optional[int] = None, is_absent: Optional[bool] = None, reason: Optional[str] = None) -> Optional[Student]:
    """Update a specific attendance record for a student"""
    db_student = db.query(Student).filter(Student.id == student_id).first()
    if not db_student:
        return None
    
    current_attendance = db_student.get_attendance()
    date_str = str(date)
    
    # Find the record to update
    record_found = False
    for record in current_attendance:
        if record["date"] == date_str and record.get("course_id") == course_id:
            # Update the fields that are provided
            if is_absent is not None:
                record["isAbsent"] = is_absent
            if reason is not None:
                record["reason"] = reason
            record_found = True
            break
    
    if record_found:
        db_student.set_attendance(current_attendance)
        db.commit()
        db.refresh(db_student)
        return db_student
    
    return None

def delete_attendance_record(db: Session, student_id: int, date: date, course_id: Optional[int] = None) -> Optional[Student]:
    """Delete a specific attendance record for a student"""
    db_student = db.query(Student).filter(Student.id == student_id).first()
    if not db_student:
        return None
    
    current_attendance = db_student.get_attendance()
    date_str = str(date)
    
    # Find and remove the record
    original_length = len(current_attendance)
    current_attendance = [record for record in current_attendance 
                         if not (record["date"] == date_str and record.get("course_id") == course_id)]
    
    if len(current_attendance) < original_length:
        db_student.set_attendance(current_attendance)
        db.commit()
        db.refresh(db_student)
        return db_student
    
    return None
