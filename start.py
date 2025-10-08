#!/usr/bin/env python3
"""
Railway startup script - handles PORT environment variable and ensures database schema
"""
import os
import sys
import logging
import uvicorn
from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import ProgrammingError

# Configure logging
logging.basicConfig(level=logging.INFO)

def ensure_database_tables():
    """Ensure all required tables exist before starting the app"""
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("⚠️ DATABASE_URL not found - using SQLite fallback")
        return True  # SQLite will auto-create on first use
    
    try:
        print("🔧 Ensuring database schema is up to date...")
        
        # Create engine
        engine = create_engine(database_url, pool_pre_ping=True)
        
        # Import models to register them with SQLAlchemy
        from app.models import Base
        
        # Create all tables (only missing ones will be created)
        Base.metadata.create_all(bind=engine)
        
        # Run database migrations
        from app.db_migrations import run_migrations
        run_migrations()
        
        # Verify critical tables exist
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        required_tables = ['users', 'courses', 'students', 'payments']
        missing_critical = [table for table in required_tables if table not in existing_tables]
        
        if missing_critical:
            print(f"❌ Critical tables still missing: {', '.join(missing_critical)}")
            return False
        
        print(f"✅ Database ready with {len(existing_tables)} tables")
        return True
        
    except Exception as e:
        print(f"⚠️ Database schema check failed: {e}")
        print("🚀 Continuing startup - app will handle missing tables gracefully")
        return True  # Continue anyway, app has error handling

if __name__ == "__main__":
    # Ensure database schema
    ensure_database_tables()
    
    # Start the server
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 Starting server on port {port}")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        workers=1
    )
