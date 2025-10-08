"""
Database initialization and migration utilities
"""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from app.core.database import Base, engine
import logging

logger = logging.getLogger(__name__)

def run_migrations():
    """Run database migrations on startup"""
    try:
        # Create all tables first
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified")
        
        # Run specific migrations
        add_course_ids_column()
        logger.info("Database migrations completed successfully")
        
    except Exception as e:
        logger.error(f"Error during database migration: {e}")
        raise

def add_course_ids_column():
    """Add course_ids column to users table if it doesn't exist"""
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./education_management.db")
    
    try:
        with engine.connect() as connection:
            # Check if course_ids column exists
            if DATABASE_URL.startswith("postgresql"):
                check_query = """
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'course_ids';
                """
            else:
                # SQLite
                check_query = "PRAGMA table_info(users);"
            
            result = connection.execute(text(check_query))
            columns = result.fetchall()
            
            course_ids_exists = False
            if DATABASE_URL.startswith("postgresql"):
                course_ids_exists = len(columns) > 0
            else:
                # SQLite - check column names in PRAGMA result
                column_names = [col[1] for col in columns]  # column[1] is column name in PRAGMA result
                course_ids_exists = 'course_ids' in column_names
            
            if not course_ids_exists:
                logger.info("Adding course_ids column to users table...")
                
                # Add the column
                alter_query = "ALTER TABLE users ADD COLUMN course_ids TEXT DEFAULT '[]';"
                connection.execute(text(alter_query))
                
                # Migrate existing data from course_id to course_ids
                logger.info("Migrating existing course_id data to course_ids...")
                
                # Update users with existing course_id values
                migrate_query = """
                UPDATE users 
                SET course_ids = CASE 
                    WHEN course_id IS NOT NULL THEN '[' || course_id || ']'
                    ELSE '[]'
                END
                WHERE course_ids IS NULL OR course_ids = '';
                """
                connection.execute(text(migrate_query))
                
                connection.commit()
                logger.info("course_ids column migration completed!")
            else:
                logger.info("course_ids column already exists")
                
    except SQLAlchemyError as e:
        logger.error(f"Database error during course_ids migration: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during course_ids migration: {e}")
        raise
