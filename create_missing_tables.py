#!/usr/bin/env python3
"""
Database migration script to create missing tables in production
This script will create the student_course_progress table that's missing
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the app directory to the path so we can import our models
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def create_missing_tables():
    """Create any missing tables in the database"""
    
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL environment variable not set")
        return False
    
    print(f"🔗 Connecting to database...")
    
    try:
        # Create engine
        engine = create_engine(database_url)
        
        # Import models after engine creation
        from app.models import Base, StudentCourseProgress
        
        print("📋 Checking existing tables...")
        
        # Check if table exists
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'student_course_progress'
            """))
            
            table_exists = result.fetchone() is not None
            
            if table_exists:
                print("✅ student_course_progress table already exists")
                return True
            else:
                print("❌ student_course_progress table missing - creating now...")
        
        # Create all tables (this will only create missing ones)
        Base.metadata.create_all(bind=engine)
        
        # Verify table was created
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'student_course_progress'
            """))
            
            table_exists = result.fetchone() is not None
            
            if table_exists:
                print("✅ student_course_progress table created successfully!")
                
                # Show the table structure
                result = conn.execute(text("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_name = 'student_course_progress'
                    ORDER BY ordinal_position
                """))
                
                print("📊 Table structure:")
                for row in result:
                    print(f"  - {row[0]}: {row[1]} {'(nullable)' if row[2] == 'YES' else '(required)'}")
                
                return True
            else:
                print("❌ Failed to create student_course_progress table")
                return False
                
    except Exception as e:
        print(f"❌ Database migration failed: {e}")
        return False

def add_sample_enrollments():
    """Add sample enrollment data if table is empty"""
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        return False
        
    try:
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        from app.models import StudentCourseProgress, Student, Course
        from datetime import date
        
        db = SessionLocal()
        
        # Check if there are any enrollments
        existing_count = db.query(StudentCourseProgress).count()
        
        if existing_count > 0:
            print(f"ℹ️ Found {existing_count} existing enrollments - skipping sample data")
            db.close()
            return True
        
        print("🎯 Adding sample enrollment data...")
        
        # Get existing students and courses
        students = db.query(Student).limit(4).all()
        courses = db.query(Course).limit(4).all()
        
        if len(students) == 0 or len(courses) == 0:
            print("⚠️ No students or courses found - cannot create sample enrollments")
            db.close()
            return False
        
        # Create sample enrollments
        enrollments = [
            StudentCourseProgress(
                student_id=students[0].id, 
                course_id=courses[0].id, 
                lessons_attended=12, 
                enrollment_date=date(2024, 9, 1)
            ),
            StudentCourseProgress(
                student_id=students[1].id, 
                course_id=courses[1].id, 
                lessons_attended=8, 
                enrollment_date=date(2024, 9, 15)
            ),
            StudentCourseProgress(
                student_id=students[2].id, 
                course_id=courses[0].id, 
                lessons_attended=6, 
                enrollment_date=date(2024, 10, 1)
            ),
        ]
        
        if len(students) > 3 and len(courses) > 3:
            enrollments.append(
                StudentCourseProgress(
                    student_id=students[3].id, 
                    course_id=courses[3].id, 
                    lessons_attended=15, 
                    enrollment_date=date(2024, 8, 20)
                )
            )
        
        db.add_all(enrollments)
        db.commit()
        
        print(f"✅ Added {len(enrollments)} sample enrollments")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to add sample enrollments: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting database migration...")
    
    # Create missing tables
    if create_missing_tables():
        print("✅ Tables created successfully")
        
        # Add sample data
        if add_sample_enrollments():
            print("✅ Sample data added successfully")
        else:
            print("⚠️ Sample data creation failed")
    else:
        print("❌ Table creation failed")
        sys.exit(1)
    
    print("🎉 Database migration completed!")
