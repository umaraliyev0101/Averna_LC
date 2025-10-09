from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import date as date_type
from enum import Enum

class UserRole(str, Enum):
    TEACHER = "teacher"
    ADMIN = "admin"
    SUPERADMIN = "superadmin"

# Attendance schemas
class AttendanceRecord(BaseModel):
    date: date_type
    course_id: Optional[int] = None  # Optional for backward compatibility
    isAbsent: bool = False
    reason: Optional[str] = ""

class AttendanceCheck(BaseModel):
    student_id: int
    course_id: int
    date: date_type
    isAbsent: bool = False
    reason: Optional[str] = ""

# User schemas
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    role: UserRole
    course_ids: Optional[List[int]] = Field(default=[])
    
    @validator('course_ids')
    def validate_course_ids(cls, v, values):
        role = values.get('role')
        if role in [UserRole.ADMIN, UserRole.SUPERADMIN]:
            # Admin and superadmin should have empty course lists
            return []
        return v if v is not None else []

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    password: Optional[str] = Field(None, min_length=6)
    role: Optional[UserRole] = None
    course_ids: Optional[List[int]] = None
    
    @validator('course_ids')
    def validate_course_ids(cls, v, values):
        role = values.get('role')
        if role in [UserRole.ADMIN, UserRole.SUPERADMIN]:
            # Admin and superadmin should have empty course lists
            return []
        return v

class UserResponse(BaseModel):
    id: int
    username: str
    role: UserRole
    course_ids: List[int] = []
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_orm(cls, obj):
        """Custom from_orm to handle course_ids conversion"""
        course_ids = obj.get_course_ids() if hasattr(obj, 'get_course_ids') else []
        # Ensure course_ids is always a list, never a string
        if isinstance(course_ids, str):
            try:
                import json
                course_ids = json.loads(course_ids)
            except (json.JSONDecodeError, TypeError):
                course_ids = []
        elif course_ids is None:
            course_ids = []
        # Ensure all items in the list are integers
        if isinstance(course_ids, list):
            course_ids = [int(x) for x in course_ids if isinstance(x, (int, str)) and str(x).isdigit()]
        else:
            course_ids = []
            
        return cls(
            id=obj.id,
            username=obj.username,
            role=obj.role,
            course_ids=course_ids
        )

# Course schemas
class CourseBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    week_days: List[str] = Field(..., min_length=1)
    lesson_per_month: int = Field(..., gt=0)
    cost: float = Field(..., gt=0)

    @validator('week_days')
    def validate_week_days(cls, v):
        valid_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for day in v:
            if day not in valid_days:
                raise ValueError(f'Invalid day: {day}. Must be one of {valid_days}')
        return v

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    week_days: Optional[List[str]] = None
    lesson_per_month: Optional[int] = Field(None, gt=0)
    cost: Optional[float] = Field(None, gt=0)

    @validator('week_days')
    def validate_week_days(cls, v):
        if v is not None:
            valid_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            for day in v:
                if day not in valid_days:
                    raise ValueError(f'Invalid day: {day}. Must be one of {valid_days}')
        return v

class CourseResponse(BaseModel):
    id: int
    name: str
    week_days: List[str]
    lesson_per_month: int
    cost: float
    
    class Config:
        from_attributes = True

# Student schemas
class StudentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    surname: str = Field(..., min_length=1, max_length=50)
    second_name: Optional[str] = Field(None, max_length=50)
    starting_date: date_type
    num_lesson: int = Field(default=0, ge=0)
    total_money: float = Field(default=0.0)
    courses: List[int] = Field(default=[])
    is_archived: bool = Field(default=False)

class StudentCreate(StudentBase):
    attendance: Optional[List[AttendanceRecord]] = Field(default=[])

class StudentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    surname: Optional[str] = Field(None, min_length=1, max_length=50)
    second_name: Optional[str] = Field(None, max_length=50)
    starting_date: Optional[date_type] = None
    num_lesson: Optional[int] = Field(None, ge=0)
    total_money: Optional[float] = None
    courses: Optional[List[int]] = None
    attendance: Optional[List[AttendanceRecord]] = None
    is_archived: Optional[bool] = None

class StudentResponse(BaseModel):
    id: int
    name: str
    surname: str
    second_name: Optional[str] = None
    starting_date: date_type
    num_lesson: int = 0
    total_money: float = 0.0
    courses: List[int] = []
    attendance: List[dict] = []  # Changed to dict to be more flexible
    is_archived: bool = False
    
    class Config:
        from_attributes = True

# Payment schemas
class PaymentBase(BaseModel):
    money: float = Field(..., gt=0)
    date: date_type  
    student_id: int = Field(..., gt=0)
    course_id: int = Field(..., gt=0)
    description: Optional[str] = Field(None, max_length=200)

class PaymentCreate(PaymentBase):
    pass

class PaymentUpdate(BaseModel):
    money: Optional[float] = Field(None, gt=0)
    date: Optional[date_type] = None
    student_id: Optional[int] = Field(None, gt=0)
    course_id: Optional[int] = Field(None, gt=0)
    description: Optional[str] = Field(None, max_length=200)

class PaymentResponse(PaymentBase):
    id: int
    
    class Config:
        from_attributes = True

# Stats schema
class StatsResponse(BaseModel):
    total_money: float
    monthly_money: float
    unpaid: float
    monthly_unpaid: float
    total_students: int

# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    username: str
    role: UserRole

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[UserRole] = None

class LoginRequest(BaseModel):
    username: str
    password: str

# Pagination schema
class PaginationParams(BaseModel):
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)

# Response wrapper
class PaginatedResponse(BaseModel):
    items: List
    total: int
    skip: int
    limit: int

# Debt management schemas
class StudentCourseProgressBase(BaseModel):
    student_id: int
    course_id: int
    lessons_attended: int = 0
    enrollment_date: date_type

class StudentCourseProgressCreate(StudentCourseProgressBase):
    pass

class StudentCourseProgressResponse(StudentCourseProgressBase):
    id: int
    
    class Config:
        from_attributes = True

class CourseDebtBreakdown(BaseModel):
    course_id: int
    course_name: str
    monthly_fee: float
    months_enrolled: int
    lessons_attended: int
    expected_lessons: int
    total_owed_for_course: float
    enrollment_date: date_type

class StudentDebtResponse(BaseModel):
    student_id: int
    student_name: str
    course_breakdown: List[CourseDebtBreakdown]
    total_monthly_owed: float
    total_paid: float
    balance: float
    owes_money: bool
    debt_amount: float
    overpaid_amount: float

class EnrollmentRequest(BaseModel):
    course_id: int
    enrollment_date: Optional[str] = None

class PaymentRequest(BaseModel):
    course_id: int
    amount: float = Field(..., gt=0)
    description: Optional[str] = "Monthly payment"
    payment_date: Optional[str] = None
