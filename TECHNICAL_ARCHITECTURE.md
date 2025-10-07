# LC Management System - Technical Architecture

## System Overview

LC Management System is a modern, scalable FastAPI-based educational management platform designed for language centers and educational institutions.

## Technology Stack

### Backend Framework
- **FastAPI 0.115.6**: Modern, fast web framework for building APIs
- **Python 3.11+**: Programming language
- **Uvicorn**: ASGI web server implementation

### Database & ORM
- **PostgreSQL**: Production database (Railway)
- **SQLite**: Development database
- **SQLAlchemy 2.0.36**: Python SQL toolkit and ORM
- **Alembic**: Database migration tool (ready for use)

### Authentication & Security
- **JWT (JSON Web Tokens)**: Stateless authentication
- **SHA256 + Salt**: Password hashing (fallback from bcrypt)
- **Role-based Access Control**: Three-tier permission system
- **CORS Middleware**: Cross-origin resource sharing support

### Validation & Serialization
- **Pydantic 2.10.3**: Data validation using Python type annotations
- **Type Hints**: Comprehensive type checking throughout

### Deployment & DevOps
- **Railway**: Cloud platform for deployment
- **Docker**: Containerization support
- **GitHub Actions**: CI/CD ready
- **Environment Variables**: Configuration management

## Architecture Patterns

### 1. Layered Architecture
```
┌─────────────────────────────────────┐
│           API Layer                 │  ← FastAPI routes, HTTP handling
├─────────────────────────────────────┤
│        Business Logic              │  ← CRUD operations, calculations
├─────────────────────────────────────┤
│         Data Access                │  ← SQLAlchemy models, queries
├─────────────────────────────────────┤
│         Database                   │  ← PostgreSQL/SQLite
└─────────────────────────────────────┘
```

### 2. Domain-Driven Design
- **Student Management Domain**: Enrollment, progress tracking
- **Course Management Domain**: Scheduling, curriculum
- **Payment Domain**: Billing, debt calculation, financial tracking
- **Authentication Domain**: Users, permissions, access control
- **Attendance Domain**: Lesson tracking, statistics

### 3. Repository Pattern
- CRUD operations abstracted in `app/crud/` directory
- Database-agnostic business logic
- Testable data access layer

## Database Schema Design

### Entity Relationship Diagram
```
Users (1) ──────────── (0..1) Courses
   │
   └── Role-based permissions

Students (M) ────────── (M) Courses
   │                      │
   │                      │
   ├── (1) ────── (M) Payments ────── (1) Courses
   │
   └── (1) ────── (M) StudentCourseProgress ────── (1) Courses
```

### Key Design Decisions

#### 1. Student-Course Relationship
- **Many-to-Many**: Students can enroll in multiple courses
- **Junction Table**: `student_courses` for basic enrollment
- **Progress Tracking**: `student_course_progress` for detailed tracking

#### 2. Payment System Design
- **Monthly Billing**: Based on enrollment duration
- **Course-Specific**: Each payment linked to specific course
- **Debt Calculation**: Automatic calculation based on enrollment time

#### 3. Attendance Tracking
- **JSON Storage**: Flexible attendance records in JSON format
- **Per-Course Tracking**: Separate lesson counts per course
- **Automatic Updates**: Lesson counts update with attendance

## API Design Principles

### 1. RESTful Design
- Standard HTTP methods (GET, POST, PUT, DELETE)
- Resource-based URLs (`/students/{id}`, `/courses/{id}`)
- Consistent response formats

### 2. OpenAPI/Swagger Integration
- Automatic documentation generation
- Interactive API testing interface
- Type-safe request/response schemas

### 3. Error Handling
- Consistent error response format
- HTTP status codes following REST conventions
- Detailed validation error messages

### 4. Security First
- JWT authentication for all protected endpoints
- Role-based authorization
- Input validation on all endpoints
- SQL injection prevention through ORM

## Monthly Payment System Architecture

### Core Components

#### 1. Enrollment Tracking
```python
class StudentCourseProgress:
    student_id: int
    course_id: int  
    enrollment_date: date
    lessons_attended: int
    
    def calculate_months_enrolled(self) -> int:
        # Calculate billing months from enrollment date
    
    def calculate_owed_amount(self) -> float:
        # Monthly fee × months enrolled
```

#### 2. Debt Calculation Engine
```python
# Debt Calculation Logic
def calculate_student_debt(student_id: int):
    total_owed = 0
    for enrollment in student.course_progress:
        months = enrollment.calculate_months_enrolled()
        course_debt = enrollment.course.cost * months
        total_owed += course_debt
    
    total_paid = sum(payment.money for payment in student.payments)
    balance = total_paid - total_owed
    return balance  # Negative = debt, Positive = credit
```

#### 3. Payment Processing
- **Per-Course Payments**: Track which course each payment is for
- **Automatic Balance Updates**: Real-time debt calculation
- **Payment History**: Complete audit trail with descriptions

## Security Architecture

### Authentication Flow
```
1. User Login Request
   ↓
2. Credentials Validation
   ↓
3. JWT Token Generation
   ↓
4. Token Return to Client
   ↓
5. Token Validation on Protected Routes
   ↓
6. Role-based Authorization Check
   ↓
7. API Access Granted/Denied
```

### Password Security
- **SHA256 + Salt**: Secure password hashing
- **Unique Salt**: Per-password salt generation
- **Bcrypt Fallback**: Backward compatibility for existing passwords

### Role-based Access Control
```python
Permissions Matrix:
                    Teacher  Admin  SuperAdmin
View Students        ✓       ✓        ✓
Manage Students      ✗       ✓        ✓
View Courses         ✓       ✓        ✓
Manage Courses       ✗       ✓        ✓
View Payments        ✗       ✓        ✓
Manage Payments      ✗       ✓        ✓
User Management      ✗       ✗        ✓
System Config        ✗       ✗        ✓
```

## Deployment Architecture

### Railway Deployment
```
GitHub Repository
    ↓ (Auto-deploy on push)
Railway Build System
    ↓ (Docker build)
Railway Container
    ↓ (Environment variables)
PostgreSQL Database
    ↓ (Auto-initialization)
Production Application
```

### Environment Configuration
- **Development**: SQLite database, debug mode
- **Production**: PostgreSQL, optimized settings
- **Environment Variables**: Secure configuration management

## Performance Considerations

### Database Optimization
- **Indexed Fields**: Primary keys, foreign keys, frequently queried fields
- **Query Optimization**: Efficient joins, proper WHERE clauses
- **Connection Pooling**: SQLAlchemy connection management

### API Performance
- **Pagination**: Large datasets split into manageable chunks
- **Lazy Loading**: On-demand relationship loading
- **Response Caching**: Static data caching potential

### Scalability Design
- **Stateless Architecture**: JWT tokens enable horizontal scaling
- **Database Agnostic**: Easy migration between database systems
- **Microservice Ready**: Domain separation enables service splitting

## Data Flow Architecture

### Student Enrollment Process
```
1. Create Student Record
   ↓
2. Create Course Enrollment (StudentCourseProgress)
   ↓
3. Update Student-Course Many-to-Many Relationship
   ↓
4. Begin Monthly Billing Calculation
   ↓
5. Track Attendance and Payments
```

### Payment Processing Flow
```
1. Payment Request
   ↓
2. Validate Student and Course
   ↓
3. Create Payment Record
   ↓
4. Update Student Total Money
   ↓
5. Recalculate Debt Balance
   ↓
6. Return Updated Balance
```

### Attendance Tracking Flow
```
1. Attendance Check Request
   ↓
2. Update Student Attendance JSON
   ↓
3. Update Lesson Count (if present)
   ↓
4. Update Course-Specific Lesson Count
   ↓
5. Recalculate Expected vs Actual Lessons
```

## Error Handling Architecture

### Exception Hierarchy
```python
FastAPI HTTP Exceptions
├── 400 Bad Request (Validation errors)
├── 401 Unauthorized (Authentication required)
├── 403 Forbidden (Insufficient permissions)
├── 404 Not Found (Resource not found)
├── 422 Unprocessable Entity (Validation details)
└── 500 Internal Server Error (System errors)
```

### Validation Strategy
- **Pydantic Models**: Request/response validation
- **Database Constraints**: Data integrity at DB level
- **Business Logic Validation**: Domain-specific rules

## Monitoring & Observability

### Health Checks
- **Basic Health**: `/health` endpoint
- **Detailed Debug**: `/debug` endpoint with system status
- **Database Connectivity**: Connection validation

### Logging Strategy
- **Application Logs**: Business logic events
- **Database Logs**: Query performance monitoring
- **Security Logs**: Authentication attempts, authorization failures

## Future Scalability

### Horizontal Scaling Ready
- **Stateless Design**: No server-side sessions
- **Database Connection Pooling**: Multiple application instances
- **Load Balancer Compatible**: Standard HTTP/REST interface

### Microservice Migration Path
- **Domain Boundaries**: Clear separation of concerns
- **API Contracts**: Well-defined interfaces
- **Database per Service**: Independent data stores

### Feature Extension Points
- **Plugin Architecture**: New payment methods, notification systems
- **API Versioning**: Backward compatibility for mobile apps
- **Multi-tenancy**: Multiple institutions on same system

## Development Workflow

### Code Organization
```
app/
├── main.py              # Application entry point
├── models/              # SQLAlchemy database models
│   └── __init__.py      # All models in single file
├── schemas/             # Pydantic validation schemas  
│   └── __init__.py      # Request/response models
├── api/                 # FastAPI route handlers
│   ├── auth.py          # Authentication endpoints
│   ├── students.py      # Student management
│   ├── courses.py       # Course management
│   ├── payments.py      # Payment processing
│   ├── debt.py          # Monthly debt system
│   ├── attendance.py    # Attendance tracking
│   ├── users.py         # User management
│   └── stats.py         # Statistics and reporting
├── crud/                # Database operations
│   └── student.py       # Student CRUD operations
├── core/                # Core functionality
│   ├── database.py      # Database configuration
│   ├── auth.py          # JWT handling
│   └── dependencies.py  # FastAPI dependencies
└── __init__.py
```

### Development Standards
- **Type Hints**: Comprehensive type annotations
- **Docstrings**: Function and class documentation
- **Error Handling**: Graceful failure modes
- **Testing Ready**: Dependency injection for testability

## Integration Architecture

### External System Integration
- **Telegram Bot**: REST API consumption
- **Mobile Apps**: JSON API with authentication
- **Reporting Tools**: Data export endpoints
- **Payment Gateways**: Extensible payment processing

### API Versioning Strategy
- **URL Versioning**: `/api/v1/` prefix ready
- **Backward Compatibility**: Maintain old endpoints
- **Feature Flags**: Gradual feature rollout

This technical architecture provides a solid foundation for scalable, maintainable educational management system with room for future growth and feature expansion.
