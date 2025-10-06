# LC Management System

A comprehensive FastAPI backend for education management system with Telegram bot integration. Provides JWT authentication, role-based access control, and complete CRUD operations for educational institutions.

## Features

### User Roles & Permissions

- **Teacher**: Can check attendance
- **Admin**: Can check attendance + CRUD operations on payments, students, and courses
- **Superadmin**: All above permissions + CRUD operations on users

### Core Functionality

- **JWT Authentication** with role-based access control
- **User Management** (superadmin only)
- **Course Management** (admin/superadmin)
- **Student Management** (admin/superadmin)
- **Payment Management** (admin/superadmin)
- **Attendance Tracking** (all roles)
- **Statistics & Reporting** (all roles)

## Project Structure

```
LC management/
├── app/
│   ├── __init__.py
│   ├── models/           # SQLAlchemy models
│   │   └── __init__.py
│   ├── schemas/          # Pydantic models
│   │   └── __init__.py
│   ├── crud/             # Database operations
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── course.py
│   │   ├── student.py
│   │   ├── payment.py
│   │   └── stats.py
│   ├── api/              # FastAPI routes
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── courses.py
│   │   ├── students.py
│   │   ├── payments.py
│   │   ├── attendance.py
│   │   └── stats.py
│   └── core/             # Configuration & auth
│       ├── __init__.py
│       ├── database.py
│       └── auth.py
├── main.py               # FastAPI application
├── populate_sample_data.py
├── requirements.txt
├── .env
└── data.txt             # Sample data source
```

## Database Models

### User
- `username`: str (unique)
- `hashed_password`: str
- `role`: Enum('teacher', 'admin', 'superadmin')
- `course_id`: Optional[int] (for teachers)

### Course
- `name`: str
- `week_days`: List[str] (JSON stored)
- `lesson_per_month`: int
- `cost`: float

### Student
- `name`, `surname`, `second_name`: str
- `starting_date`: date
- `num_lesson`: int
- `total_money`: float
- `attendance`: List[AttendanceRecord] (JSON stored)
- `courses`: Many-to-many relationship

### Payment
- `money`: float
- `date`: date
- `student_id`: int (FK)
- `course_id`: int (FK)

## API Endpoints

### Authentication
- `POST /auth/token` - Login and get JWT token

### Attendance (Teacher/Admin/Superadmin)
- `POST /attendance/check` - Record attendance
- `GET /attendance/student/{student_id}` - Get student attendance

### Payments (Admin/Superadmin)
- `GET /payments/` - List payments (with filtering)
- `POST /payments/` - Create payment
- `GET /payments/{payment_id}` - Get payment
- `PUT /payments/{payment_id}` - Update payment
- `DELETE /payments/{payment_id}` - Delete payment

### Students (Admin/Superadmin)
- `GET /students/` - List students (with search)
- `POST /students/` - Create student
- `GET /students/{student_id}` - Get student
- `PUT /students/{student_id}` - Update student
- `DELETE /students/{student_id}` - Delete student

### Courses (Admin/Superadmin)
- `GET /courses/` - List courses
- `POST /courses/` - Create course
- `GET /courses/{course_id}` - Get course
- `PUT /courses/{course_id}` - Update course
- `DELETE /courses/{course_id}` - Delete course

### Users (Superadmin only)
- `GET /users/` - List users
- `POST /users/` - Create user
- `GET /users/{user_id}` - Get user
- `PUT /users/{user_id}` - Update user
- `DELETE /users/{user_id}` - Delete user

### Statistics (All roles)
- `GET /stats/` - General statistics
- `GET /stats/by-course` - Payment stats by course
- `GET /stats/monthly/{year}` - Monthly statistics

## Installation & Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   - Copy `.env` file and update values:
   ```
   DATABASE_URL=sqlite:///./education_management.db
   SECRET_KEY=your-super-secret-key-change-in-production
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

3. **Populate sample data:**
   ```bash
   python populate_sample_data.py
   ```

4. **Run the application:**
   ```bash
   python main.py
   ```
   or
   ```bash
   uvicorn main:app --reload
   ```

## Sample Users

The sample data includes these test users:

| Username   | Password   | Role       |
|------------|------------|------------|
| admin      | admin123   | admin      |
| teacher1   | teacher123 | teacher    |
| teacher2   | teacher456 | teacher    |
| superadmin | super123   | superadmin |

## Authentication

1. **Get token:**
   ```bash
   curl -X POST "http://localhost:8000/auth/token" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=admin&password=admin123"
   ```

2. **Use token in requests:**
   ```bash
   curl -X GET "http://localhost:8000/students/" \
        -H "Authorization: Bearer YOUR_TOKEN_HERE"
   ```

## API Documentation

Once running, visit:
- **Interactive docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Key Features Implementation

### Role-Based Access Control
- JWT tokens include user role
- Dependency injection for role checking
- Decorator functions for different permission levels

### Attendance Management
- Embedded JSON in Student model
- Flexible attendance recording
- Historical attendance tracking

### Payment Tracking
- Complete CRUD operations
- Filtering by student, course, date range
- Statistical aggregations

### Database Design
- Proper foreign key relationships
- Many-to-many student-course relationships
- JSON fields for complex data (attendance, week_days)

### Error Handling
- Proper HTTP status codes
- Detailed error messages
- Database transaction safety

## Production Considerations

1. **Security:**
   - Change SECRET_KEY in production
   - Use proper CORS origins
   - Implement rate limiting
   - Add request validation

2. **Database:**
   - Use PostgreSQL for production
   - Implement database migrations with Alembic
   - Add database connection pooling

3. **Monitoring:**
   - Add logging
   - Implement health checks
   - Add metrics collection

4. **Performance:**
   - Add caching for statistics
   - Implement pagination consistently
   - Add database indexing
