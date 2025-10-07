#!/usr/bin/env python3
"""
Railway startup script to ensure database schema is properly initialized
This script runs before the FastAPI app starts
"""

import os
import sys
import time
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import ProgrammingError

def ensure_database_schema():
    """Ensure all required tables exist in the database"""
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not found - using SQLite fallback")
        database_url = "sqlite:///./education_management.db"
    
    print(f"🔗 Checking database schema...")
    
    max_retries = 5
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # Create engine with connection retry
            engine = create_engine(database_url, pool_pre_ping=True)
            
            # Import models
            from app.models import Base
            
            # Check existing tables
            inspector = inspect(engine)
            existing_tables = inspector.get_table_names()
            
            print(f"📋 Found {len(existing_tables)} existing tables")
            
            # Required tables
            required_tables = [
                'users', 'courses', 'students', 'payments', 
                'student_courses', 'student_course_progress'
            ]
            
            missing_tables = [table for table in required_tables if table not in existing_tables]
            
            if missing_tables:
                print(f"⚠️ Missing tables: {', '.join(missing_tables)}")
                print("🔧 Creating missing tables...")
                
                # Create all tables (only missing ones will be created)
                Base.metadata.create_all(bind=engine)
                
                # Verify tables were created
                inspector = inspect(engine)
                existing_tables = inspector.get_table_names()
                
                still_missing = [table for table in required_tables if table not in existing_tables]
                
                if still_missing:
                    print(f"❌ Failed to create tables: {', '.join(still_missing)}")
                    return False
                else:
                    print("✅ All tables created successfully!")
            else:
                print("✅ All required tables exist")
            
            # Test a simple query to ensure everything works
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
            
            print("✅ Database schema validation completed")
            return True
            
        except Exception as e:
            retry_count += 1
            print(f"⚠️ Database connection attempt {retry_count}/{max_retries} failed: {e}")
            
            if retry_count < max_retries:
                wait_time = min(2 ** retry_count, 30)  # Exponential backoff, max 30s
                print(f"⏳ Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print("❌ Maximum retries exceeded - database schema validation failed")
                return False
    
    return False

if __name__ == "__main__":
    print("🚀 Starting database schema validation...")
    
    # Add the app directory to Python path
    app_dir = os.path.dirname(os.path.abspath(__file__))
    if app_dir not in sys.path:
        sys.path.insert(0, app_dir)
    
    success = ensure_database_schema()
    
    if success:
        print("🎉 Database schema is ready!")
        sys.exit(0)
    else:
        print("💥 Database schema validation failed!")
        sys.exit(1)
