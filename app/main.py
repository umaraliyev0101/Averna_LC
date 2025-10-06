"""
FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
from app.api.auth import router as auth_router
from app.api.students import router as students_router
from app.api.courses import router as courses_router
from app.api.attendance import router as attendance_router
from app.api.payments import router as payments_router
from app.api.users import router as users_router
from app.api.stats import router as stats_router

# Create database tables
Base.metadata.create_all(bind=engine)

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

@app.get("/")
async def root():
    return {"message": "LC Management API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is operational"}

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
