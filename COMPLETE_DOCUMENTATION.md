# LC Management System - Complete Documentation

## Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Installation & Setup](#installation--setup)
4. [API Documentation](#api-documentation)
5. [Database Schema](#database-schema)
6. [Authentication & Authorization](#authentication--authorization)
7. [Monthly Payment System](#monthly-payment-system)
8. [Usage Examples](#usage-examples)
9. [Deployment](#deployment)
10. [Troubleshooting](#troubleshooting)

---

## Overview

LC Management System is a comprehensive FastAPI-based backend designed for educational institutions to manage:
- **Student enrollment and progress tracking**
- **Course management with scheduling**
- **Monthly payment system with debt tracking**
- **Attendance monitoring**
- **User management with role-based access**
- **Financial reporting and statistics**

### Key Features
- 🔐 **JWT-based authentication** with role-based permissions
- 💰 **Monthly payment system** with automatic debt calculation
- 📊 **Real-time statistics** and reporting
- 🎓 **Student progress tracking** per course
- 📅 **Attendance management** with lesson counting
- 🏫 **Multi-course enrollment** support
- 🌐 **RESTful API** with comprehensive documentation
- 🚀 **Production-ready** with Railway deployment

---

## System Architecture

```
LC Management API
├── Authentication Layer (JWT)
├── Authorization Layer (Role-based)
├── API Layer (FastAPI)
├── Business Logic Layer
├── Data Access Layer (SQLAlchemy)
└── Database Layer (PostgreSQL/SQLite)
```

### Technology Stack
- **Framework**: FastAPI 0.115.6
- **Database**: PostgreSQL (Production), SQLite (Development)
- **ORM**: SQLAlchemy 2.0.36
- **Authentication**: JWT tokens with bcrypt/SHA256 hashing
- **Validation**: Pydantic 2.10.3
- **Deployment**: Railway (Cloud), Docker support
- **API Documentation**: Automatic OpenAPI/Swagger

---

## Installation & Setup

### Prerequisites
- Python 3.11+
- PostgreSQL (for production)
- Git

### Local Development Setup

1. **Clone the repository**
```bash
git clone https://github.com/umaraliyev0101/Averna_LC.git
cd Averna_LC
```

2. **Create virtual environment**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment setup**
```bash
# Create .env file
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./education_management.db
CORS_ORIGINS=*
```

5. **Start the application**
```bash
python start.py
```

6. **Access the API**
- API Base URL: `http://localhost:8000`
- Interactive Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

### Production Deployment (Railway)

The application is configured for automatic deployment on Railway:
- Automatic database initialization
- Environment variable configuration
- Docker containerization
- PostgreSQL database integration

---

## API Documentation

### Base URL
- **Development**: `http://localhost:8000`
- **Production**: `https://your-railway-url.com`

### Authentication Required
Most endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

---

## Authentication Endpoints

### POST `/auth/login`
Authenticate user and receive JWT token.

**Request Body:**
```json
{
  "username": "admin",
  "password": "admin"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "user_id": 1,
  "username": "admin",
  "role": "admin"
}
```

**Default Users:**
- `admin` / `admin` (Administrator)
- `superadmin` / `super` (Super Administrator)
- `teacher1` / `teach` (Teacher)

---

## Student Management Endpoints

### GET `/students/`
Get list of all students with pagination.

**Query Parameters:**
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum records to return (default: 100)

**Response:**
```json
[
  {
    "id": 1,
    "name": "John",
    "surname": "Doe",
    "second_name": "Michael",
    "starting_date": "2024-09-01",
    "num_lesson": 12,
    "total_money": 450.0,
    "courses": [1, 3],
    "attendance": []
  }
]
```

### POST `/students/`
Create a new student.

**Request Body:**
```json
{
  "name": "Jane",
  "surname": "Smith",
  "second_name": "",
  "starting_date": "2025-10-07",
  "num_lesson": 0,
  "total_money": 0.0,
  "courses": [1, 2],
  "attendance": []
}
```

### GET `/students/{student_id}`
Get specific student by ID.

### PUT `/students/{student_id}`
Update student information.

### DELETE `/students/{student_id}`
Delete student (admin/superadmin only).

---

## Course Management Endpoints

### GET `/courses/`
Get list of all courses.

**Response:**
```json
[
  {
    "id": 1,
    "name": "English Language",
    "week_days": ["Monday", "Wednesday", "Friday"],
    "lesson_per_month": 8,
    "cost": 150.0
  }
]
```

### POST `/courses/`
Create a new course.

**Request Body:**
```json
{
  "name": "Mathematics Advanced",
  "week_days": ["Tuesday", "Thursday"],
  "lesson_per_month": 8,
  "cost": 200.0
}
```

### GET `/courses/{course_id}`
Get specific course by ID.

### PUT `/courses/{course_id}`
Update course information.

### DELETE `/courses/{course_id}`
Delete course.

---

## Payment Management Endpoints

### GET `/payments/`
Get list of all payments with filtering.

**Query Parameters:**
- `student_id`: Filter by student
- `course_id`: Filter by course
- `start_date`: Filter from date (YYYY-MM-DD)
- `end_date`: Filter to date (YYYY-MM-DD)

### POST `/payments/`
Record a new payment.

**Request Body:**
```json
{
  "money": 150.0,
  "date": "2025-10-07",
  "student_id": 1,
  "course_id": 1,
  "description": "Monthly payment for English course"
}
```

### GET `/payments/{payment_id}`
Get specific payment by ID.

### PUT `/payments/{payment_id}`
Update payment information.

### DELETE `/payments/{payment_id}`
Delete payment.

---

## Debt Management Endpoints (Monthly System)

### GET `/debt/student/{student_id}/monthly-debt`
Calculate student's debt based on monthly course fees.

**Response:**
```json
{
  "student_id": 1,
  "student_name": "John Doe",
  "course_breakdown": [
    {
      "course_id": 1,
      "course_name": "English Language",
      "monthly_fee": 150.0,
      "months_enrolled": 2,
      "lessons_attended": 12,
      "expected_lessons": 16,
      "total_owed_for_course": 300.0,
      "enrollment_date": "2024-09-01"
    }
  ],
  "total_monthly_owed": 300.0,
  "total_paid": 250.0,
  "balance": -50.0,
  "owes_money": true,
  "debt_amount": 50.0,
  "overpaid_amount": 0.0
}
```

### POST `/debt/student/{student_id}/enroll-course`
Enroll student in a course (starts monthly billing).

**Request Body:**
```json
{
  "course_id": 1,
  "enrollment_date": "2025-10-07"
}
```

### PUT `/debt/student/{student_id}/course/{course_id}/add-lessons`
Add lessons attended for specific course.

**Request Body:**
```json
{
  "lessons_count": 3
}
```

### GET `/debt/monthly-summary`
Get debt summary for all students.

**Response:**
```json
{
  "students": [
    {
      "student_id": 1,
      "student_name": "John Doe",
      "monthly_owed": 300.0,
      "total_paid": 250.0,
      "debt": 50.0,
      "balance": -50.0
    }
  ],
  "total_debt_all_students": 150.0,
  "students_with_debt": 2
}
```

### POST `/debt/student/{student_id}/payment`
Record payment for a student.

**Request Body:**
```json
{
  "course_id": 1,
  "amount": 150.0,
  "description": "Monthly payment",
  "payment_date": "2025-10-07"
}
```

### GET `/debt/course/{course_id}/students-debt`
Get debt status for all students in a specific course.

---

## Attendance Management Endpoints

### POST `/attendance/check`
Record attendance for a student.

**Request Body:**
```json
{
  "student_id": 1,
  "date": "2025-10-07",
  "isAbsent": false,
  "reason": ""
}
```

### GET `/attendance/student/{student_id}`
Get attendance history for a student.

### PUT `/attendance/student/{student_id}`
Update attendance record.

---

## User Management Endpoints

### GET `/users/`
Get list of all users (admin/superadmin only).

### POST `/users/`
Create a new user (superadmin only).

**Request Body:**
```json
{
  "username": "teacher2",
  "password": "teacher123",
  "role": "teacher",
  "course_id": 1
}
```

### GET `/users/{user_id}`
Get specific user by ID.

### PUT `/users/{user_id}`
Update user information.

### DELETE `/users/{user_id}`
Delete user (superadmin only).

---

## Statistics Endpoints

### GET `/stats/overview`
Get system overview statistics.

**Response:**
```json
{
  "total_money": 1500.0,
  "monthly_money": 450.0,
  "unpaid": 200.0,
  "monthly_unpaid": 100.0,
  "total_students": 25
}
```

### GET `/stats/payments`
Get payment statistics with date filtering.

### GET `/stats/attendance`
Get attendance statistics.

---

## Database Schema

### Core Tables

#### `users`
- `id` (Primary Key)
- `username` (Unique)
- `hashed_password`
- `role` (teacher, admin, superadmin)
- `course_id` (Foreign Key, nullable)

#### `students`
- `id` (Primary Key)
- `name`
- `surname`
- `second_name` (nullable)
- `starting_date`
- `num_lesson` (total lessons attended)
- `total_money` (total amount paid)
- `attendance` (JSON string)

#### `courses`
- `id` (Primary Key)
- `name`
- `week_days` (JSON string)
- `lesson_per_month`
- `cost` (monthly fee)

#### `payments`
- `id` (Primary Key)
- `money`
- `date`
- `student_id` (Foreign Key)
- `course_id` (Foreign Key)
- `description`

#### `student_course_progress`
- `id` (Primary Key)
- `student_id` (Foreign Key)
- `course_id` (Foreign Key)
- `lessons_attended`
- `enrollment_date`

#### `student_courses` (Many-to-Many)
- `student_id` (Foreign Key)
- `course_id` (Foreign Key)

---

## Authentication & Authorization

### User Roles
1. **Teacher**: Can view assigned students and courses
2. **Admin**: Can manage students, courses, payments, attendance
3. **Superadmin**: Full system access including user management

### JWT Token
- **Algorithm**: HS256
- **Expiration**: 30 minutes (configurable)
- **Payload**: Contains username and role
- **Header**: `Authorization: Bearer <token>`

### Role-based Access Control
```python
# Endpoint access levels:
- Public: /health, /docs
- Any authenticated: /auth/login
- Teacher+: Basic student/course viewing
- Admin+: Student/course/payment management
- Superadmin: User management, system configuration
```

---

## Monthly Payment System

### How It Works
1. **Enrollment**: Student enrolls in course with enrollment date
2. **Monthly Billing**: System calculates months enrolled × course cost
3. **Payment Tracking**: Records payments per course
4. **Debt Calculation**: Total owed - Total paid = Balance
5. **Automatic Updates**: Enrollment duration updates monthly

### Example Calculation
```
Student: John Doe
Course: English Language (150,000 UZS/month)
Enrolled: September 1, 2024 (2 months ago)
Total Owed: 150,000 × 2 = 300,000 UZS
Total Paid: 250,000 UZS
Balance: -50,000 UZS (Student owes 50,000 UZS)
```

### Key Features
- ✅ **Automatic monthly billing**
- ✅ **Multi-course enrollment support**
- ✅ **Individual course payment tracking**
- ✅ **Lesson attendance tracking per course**
- ✅ **Comprehensive debt reporting**
- ✅ **Payment history with descriptions**

---

## Usage Examples

### 1. Student Enrollment Workflow
```bash
# 1. Create student
POST /students/
{
  "name": "Alice",
  "surname": "Johnson",
  "starting_date": "2025-10-07",
  "courses": []
}

# 2. Enroll in course
POST /debt/student/1/enroll-course
{
  "course_id": 1,
  "enrollment_date": "2025-10-07"
}

# 3. Record attendance
PUT /debt/student/1/course/1/add-lessons
{
  "lessons_count": 4
}

# 4. Record payment
POST /debt/student/1/payment
{
  "course_id": 1,
  "amount": 150.0,
  "description": "October payment"
}

# 5. Check debt status
GET /debt/student/1/monthly-debt
```

### 2. Monthly Reporting Workflow
```bash
# 1. Get all students debt summary
GET /debt/monthly-summary

# 2. Get course-specific debt
GET /debt/course/1/students-debt

# 3. Get payment statistics
GET /stats/payments?start_date=2025-10-01&end_date=2025-10-31

# 4. Get attendance overview
GET /stats/attendance
```

### 3. Administrative Tasks
```bash
# 1. Create new teacher
POST /users/
{
  "username": "teacher_math",
  "password": "secure123",
  "role": "teacher",
  "course_id": 2
}

# 2. Create new course
POST /courses/
{
  "name": "Advanced Physics",
  "week_days": ["Monday", "Wednesday", "Friday"],
  "lesson_per_month": 12,
  "cost": 250.0
}

# 3. Bulk payment processing
POST /payments/
{
  "money": 500.0,
  "student_id": 1,
  "course_id": 1,
  "description": "Quarterly payment"
}
```

---

## Deployment

### Railway Deployment (Current)
The application is deployed on Railway with:
- **Automatic deployments** from GitHub
- **PostgreSQL database** integration
- **Environment variables** configuration
- **Custom domain** support
- **SSL/HTTPS** enabled

### Environment Variables
```bash
DATABASE_URL=postgresql://username:password@hostname:port/database
SECRET_KEY=your-secret-key-for-jwt
CORS_ORIGINS=*
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Docker Deployment
```dockerfile
# Dockerfile included for containerization
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "start.py"]
```

### Manual Deployment Steps
1. Set up PostgreSQL database
2. Configure environment variables
3. Install dependencies: `pip install -r requirements.txt`
4. Run database initialization (automatic on first startup)
5. Start application: `python start.py`

---

## Troubleshooting

### Common Issues

#### 1. Authentication Errors
```
Problem: 401 Unauthorized
Solution: Check JWT token validity and format
Fix: Re-login to get fresh token
```

#### 2. Database Connection
```
Problem: Database connection failed
Solution: Verify DATABASE_URL environment variable
Fix: Check PostgreSQL service status
```

#### 3. Import Errors
```
Problem: Module not found
Solution: Ensure virtual environment is activated
Fix: pip install -r requirements.txt
```

#### 4. Permission Denied
```
Problem: 403 Forbidden
Solution: Check user role permissions
Fix: Use admin/superadmin account for restricted endpoints
```

### Debug Endpoints

#### GET `/debug`
System health and configuration check.

**Response:**
```json
{
  "database_url_set": true,
  "secret_key_set": true,
  "cors_origins": "*",
  "database_connection": "success",
  "users_table": "exists, 3 users"
}
```

#### GET `/health`
Basic health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "message": "API is operational"
}
```

### Logging
- Application logs are output to console
- Database queries can be logged by setting SQLAlchemy echo=True
- Error tracking includes stack traces in development mode

---

## API Response Formats

### Success Response
```json
{
  "id": 1,
  "field1": "value1",
  "field2": "value2"
}
```

### Error Response
```json
{
  "detail": "Error message description"
}
```

### Validation Error
```json
{
  "detail": [
    {
      "loc": ["field_name"],
      "msg": "Validation error message",
      "type": "value_error"
    }
  ]
}
```

---

## Contributing

### Development Guidelines
1. Follow PEP 8 coding standards
2. Write comprehensive tests for new features
3. Update documentation for API changes
4. Use type hints throughout the codebase
5. Maintain backward compatibility

### Code Structure
```
app/
├── main.py              # FastAPI application entry point
├── models/              # SQLAlchemy database models
├── schemas/             # Pydantic validation schemas
├── api/                 # API route handlers
├── core/                # Core functionality (auth, database)
└── crud/                # Database operations
```

---

## License

This project is licensed under the MIT License. See LICENSE file for details.

---

## Support

For support and questions:
- GitHub Issues: [Create an issue](https://github.com/umaraliyev0101/Averna_LC/issues)
- Documentation: This README and `/docs` endpoint
- API Testing: Use the interactive docs at `/docs`

---

## Version History

### v1.0.0 (Current)
- ✅ Complete FastAPI backend implementation
- ✅ JWT authentication with role-based access
- ✅ Monthly payment system with debt tracking
- ✅ Student and course management
- ✅ Attendance tracking with lesson counting
- ✅ Payment processing with descriptions
- ✅ Statistics and reporting
- ✅ Railway deployment with PostgreSQL
- ✅ Auto-initialization for production deployment
- ✅ Comprehensive API documentation

---

*Last updated: October 7, 2025*
