from sqlalchemy import Column, Integer, String, Float, Date, Boolean, Text, ForeignKey, Enum as SQLEnum, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSON
from enum import Enum
import json

Base = declarative_base()

# Constants for table references
COURSES_TABLE_REF = "courses.id"
STUDENTS_TABLE_REF = "students.id"

class UserRole(str, Enum):
    TEACHER = "teacher"
    ADMIN = "admin"
    SUPERADMIN = "superadmin"

# Association table for many-to-many relationship between students and courses
student_courses = Table(
    'student_courses',
    Base.metadata,
    Column('student_id', Integer, ForeignKey('students.id'), primary_key=True),
    Column('course_id', Integer, ForeignKey('courses.id'), primary_key=True)
)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False)
    course_id = Column(Integer, ForeignKey(COURSES_TABLE_REF), nullable=True)
    
    # Relationship to course (for teachers)
    course = relationship("Course", back_populates="teacher")

class Course(Base):
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    week_days = Column(Text, nullable=False)  # JSON string of list
    lesson_per_month = Column(Integer, nullable=False)
    cost = Column(Float, nullable=False)
    
    # Relationships
    teacher = relationship("User", back_populates="course")
    students = relationship("Student", secondary=student_courses, back_populates="courses")
    payments = relationship("Payment", back_populates="course")
    student_progress = relationship("StudentCourseProgress", back_populates="course")
    
    def get_week_days(self):
        """Parse JSON string to list"""
        if isinstance(self.week_days, str) and self.week_days:
            return json.loads(self.week_days)
        return []
    
    def set_week_days(self, days_list):
        """Convert list to JSON string"""
        self.week_days = json.dumps(days_list)

class Student(Base):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    surname = Column(String(50), nullable=False)
    second_name = Column(String(50), nullable=True)
    starting_date = Column(Date, nullable=False)
    num_lesson = Column(Integer, default=0)
    total_money = Column(Float, default=0.0)
    attendance = Column(Text, nullable=True)  # JSON string of attendance records
    
    # Relationships
    courses = relationship("Course", secondary=student_courses, back_populates="students")
    payments = relationship("Payment", back_populates="student")
    course_progress = relationship("StudentCourseProgress", back_populates="student")
    
    def get_attendance(self):
        """Parse JSON string to list of attendance records"""
        if isinstance(self.attendance, str) and self.attendance:
            return json.loads(self.attendance)
        return []
    
    def set_attendance(self, attendance_list):
        """Convert list to JSON string"""
        self.attendance = json.dumps(attendance_list, default=str)
    
    def add_attendance_record(self, date, is_absent=False, reason=""):
        """Add single attendance record and update lesson count"""
        current_attendance = self.get_attendance()
        
        # Check if attendance for this date already exists
        date_str = str(date)
        existing_record = next((record for record in current_attendance if record["date"] == date_str), None)
        
        if existing_record:
            # Update existing record
            was_absent_before = existing_record["isAbsent"]
            existing_record["isAbsent"] = is_absent
            existing_record["reason"] = reason
            
            # Adjust lesson count if attendance status changed
            if was_absent_before and not is_absent:
                # Was absent before, now present - increment lesson count
                self.num_lesson += 1
            elif not was_absent_before and is_absent:
                # Was present before, now absent - decrement lesson count
                self.num_lesson = max(0, self.num_lesson - 1)
        else:
            # Add new record
            current_attendance.append({
                "date": date_str,
                "isAbsent": is_absent,
                "reason": reason
            })
            
            # If student is present, increment lesson count
            if not is_absent:
                self.num_lesson += 1
        
        self.set_attendance(current_attendance)

class StudentCourseProgress(Base):
    """Track student enrollment and progress in specific courses"""
    __tablename__ = "student_course_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey(STUDENTS_TABLE_REF), nullable=False)
    course_id = Column(Integer, ForeignKey(COURSES_TABLE_REF), nullable=False)
    lessons_attended = Column(Integer, default=0)  # Total lessons attended for this course
    enrollment_date = Column(Date, nullable=False)  # When student enrolled in this course
    
    # Relationships
    student = relationship("Student")
    course = relationship("Course")
    
    def calculate_months_enrolled(self):
        """Calculate how many months student has been enrolled"""
        from datetime import date
        today = date.today()
        months = (today.year - self.enrollment_date.year) * 12 + (today.month - self.enrollment_date.month)
        return max(1, months)  # At least 1 month
    
    def calculate_owed_amount(self):
        """Calculate total amount owed for this course"""
        months_enrolled = self.calculate_months_enrolled()
        return self.course.cost * months_enrolled

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    money = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    student_id = Column(Integer, ForeignKey(STUDENTS_TABLE_REF), nullable=False)
    course_id = Column(Integer, ForeignKey(COURSES_TABLE_REF), nullable=False)
    description = Column(String(200), nullable=True, default="")
    
    # Relationships
    student = relationship("Student", back_populates="payments")
    course = relationship("Course", back_populates="payments")
