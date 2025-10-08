"""
FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base, SessionLocal
from app.api.auth import router as auth_router
from app.api.students import router as students_router
from app.api.courses import router as courses_router
from app.api.attendance import router as attendance_router
from app.api.payments import router as payments_router
from app.api.users import router as users_router
from app.api.stats import router as stats_router
from app.api.debt import router as debt_router

# Create database tables
Base.metadata.create_all(bind=engine)

# Auto-initialize database with sample data
def auto_initialize_database():
    """Initialize database with sample data if empty"""
    try:
        from app.models import User, Course, Student, Payment, StudentCourseProgress
        from app.core.auth import get_password_hash
        from datetime import date, datetime
        
        db = SessionLocal()
        
        # Check if database is empty
        user_count = db.query(User).count()
        if user_count > 0:
            print("ℹ️ Database already initialized")
            db.close()
            return
        
        print("🚀 Auto-initializing database with sample data...")
        
        # Create users with shorter passwords to avoid bcrypt 72-byte limit
        admin_user = User(
            username="admin",
            hashed_password=get_password_hash("admin"),
            role="admin"
        )
        superadmin_user = User(
            username="superadmin", 
            hashed_password=get_password_hash("super"),
            role="superadmin"
        )
        teacher_user = User(
            username="teacher1",
            hashed_password=get_password_hash("teach"),
            role="teacher"
        )
        
        db.add_all([admin_user, superadmin_user, teacher_user])
        db.commit()
        
        # Create courses (week_days must be JSON string)
        import json
        courses = [
            Course(name="English Language", week_days=json.dumps(["Monday", "Wednesday"]), lesson_per_month=8, cost=150.0),
            Course(name="Mathematics", week_days=json.dumps(["Tuesday", "Thursday"]), lesson_per_month=8, cost=200.0),
            Course(name="Science", week_days=json.dumps(["Monday", "Friday"]), lesson_per_month=8, cost=180.0),
            Course(name="History", week_days=json.dumps(["Wednesday", "Friday"]), lesson_per_month=6, cost=120.0)
        ]
        
        db.add_all(courses)
        db.commit()
        
        # Create students
        students = [
            Student(name="John", surname="Doe", second_name="Michael", starting_date=date(2024, 9, 1), num_lesson=12, total_money=450.0),
            Student(name="Jane", surname="Smith", second_name="Elizabeth", starting_date=date(2024, 9, 15), num_lesson=8, total_money=320.0),
            Student(name="Bob", surname="Johnson", second_name="Robert", starting_date=date(2024, 10, 1), num_lesson=6, total_money=240.0),
            Student(name="Alice", surname="Brown", second_name="Marie", starting_date=date(2024, 8, 20), num_lesson=15, total_money=600.0)
        ]
        
        db.add_all(students)
        db.commit()
        
        # Create student course enrollments for monthly tracking
        enrollments = [
            StudentCourseProgress(student_id=1, course_id=1, lessons_attended=12, enrollment_date=date(2024, 9, 1)),
            StudentCourseProgress(student_id=1, course_id=3, lessons_attended=8, enrollment_date=date(2024, 9, 1)),
            StudentCourseProgress(student_id=2, course_id=2, lessons_attended=8, enrollment_date=date(2024, 9, 15)),
            StudentCourseProgress(student_id=3, course_id=1, lessons_attended=6, enrollment_date=date(2024, 10, 1)),
            StudentCourseProgress(student_id=4, course_id=4, lessons_attended=15, enrollment_date=date(2024, 8, 20))
        ]
        
        db.add_all(enrollments)
        db.commit()
        
        # Create sample payments
        payments = [
            Payment(money=150.0, date=date(2024, 9, 1), student_id=1, course_id=1, description="September tuition"),
            Payment(money=200.0, date=date(2024, 9, 1), student_id=2, course_id=2, description="Math course enrollment"),
            Payment(money=180.0, date=date(2024, 9, 15), student_id=3, course_id=3, description="Science course payment"),
            Payment(money=120.0, date=date(2024, 10, 1), student_id=4, course_id=4, description="History class fee"),
            Payment(money=150.0, date=date(2024, 10, 1), student_id=1, course_id=1, description="October tuition")
        ]
        
        db.add_all(payments)
        db.commit()
        db.close()
        
        print("✅ Database auto-initialized successfully!")
        print("✅ Created 3 users: admin (pwd: admin), superadmin (pwd: super), teacher1 (pwd: teach)")
        print("✅ Created 4 courses")
        print("✅ Created 4 students") 
        print("✅ Created 5 sample payments")
        
    except Exception as e:
        print(f"❌ Auto-initialization failed: {e}")
        if 'db' in locals():
            db.rollback()
            db.close()

# Run auto-initialization
auto_initialize_database()

app = FastAPI(
    title="LC Management API",
    description="FastAPI backend for Telegram bot education management system",
    version="1.0.0"
)

# Configure CORS for production and development
import os

cors_origins = os.getenv("CORS_ORIGINS", "*")
if cors_origins == "*":
    origins = ["*"]
else:
    origins = [origin.strip() for origin in cors_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(students_router, prefix="/students", tags=["Students"])
app.include_router(courses_router, prefix="/courses", tags=["Courses"])
app.include_router(attendance_router, prefix="/attendance", tags=["Attendance"])
app.include_router(payments_router, prefix="/payments", tags=["Payments"])
app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(stats_router, prefix="/stats", tags=["Statistics"])
app.include_router(debt_router, prefix="/debt", tags=["Debt Management"])

@app.get("/")
async def root():
    return {"message": "LC Management API is running!"}

@app.get("/health")
async def health_check():
    """Enhanced health check including database status"""
    health_status = {
        "status": "healthy",
        "message": "API is operational",
        "database": "unknown"
    }
    
    try:
        from app.core.database import SessionLocal
        from app.models import User, StudentCourseProgress
        
        db = SessionLocal()
        
        # Test basic database connectivity
        users_count = db.query(User).count()
        health_status["database"] = "connected"
        health_status["users"] = str(users_count)
        
        # Test if StudentCourseProgress table exists
        try:
            progress_count = db.query(StudentCourseProgress).count()
            health_status["student_progress_table"] = f"exists ({progress_count} records)"
        except Exception as table_error:
            if "student_course_progress" in str(table_error).lower():
                health_status["student_progress_table"] = "missing - will be created on demand"
                health_status["status"] = "degraded"
            else:
                health_status["student_progress_table"] = f"error: {table_error}"
        
        db.close()
        
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["database"] = f"error: {str(e)}"
    
    return health_status

@app.get("/debug")
async def debug_info():
    """Debug endpoint to check environment and database"""
    import os
    from app.core.database import SessionLocal
    from app.models import User
    
    debug_info = {
        "database_url_set": bool(os.getenv("DATABASE_URL")),
        "secret_key_set": bool(os.getenv("SECRET_KEY")),
        "cors_origins": os.getenv("CORS_ORIGINS", "not_set")
    }
    
    # Test database connection
    try:
        db = SessionLocal()
        users_count = db.query(User).count()
        debug_info["database_connection"] = "success"
        debug_info["users_table"] = f"exists, {users_count} users"
        db.close()
    except Exception as e:
        debug_info["database_connection"] = f"error: {str(e)}"
        debug_info["users_table"] = "error accessing table"
    
    return debug_info
