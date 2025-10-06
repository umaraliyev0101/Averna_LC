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
