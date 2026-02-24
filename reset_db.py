import os
import sys
import logging
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Add current directory to path so we can import from app
sys.path.append(os.getcwd())

from app.core.database import Base, engine, SessionLocal
from app.db_migrations import run_migrations
from app.models import User, UserRole
from app.schemas import UserCreate
from app.crud.user import create_user

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def reset_database():
    """Drops all tables and recreates them, effectively cleaning all data"""
    try:
        logger.info("⚠️ WARNING: This will delete ALL data from the database!")
        # On Railway, stdin might not be available, so check for env var override
        force_reset = os.getenv("FORCE_RESET_DB", "false").lower() == "true"
        
        if not force_reset:
            confirm = input("Are you absolutely sure you want to proceed? (y/N): ")
            if confirm.lower() != 'y':
                logger.info("Database reset cancelled.")
                return

        logger.info("Cleaning data (dropping all tables)...")
        Base.metadata.drop_all(bind=engine)
        logger.info("All tables dropped successfully.")

        logger.info("Recreating database schema...")
        Base.metadata.create_all(bind=engine)
        
        logger.info("Running migrations...")
        run_migrations()
        
        # Create a default admin user
        create_admin = os.getenv("CREATE_ADMIN", "true").lower() == "true"
        if create_admin:
            db = SessionLocal()
            try:
                admin_user = "admin"
                admin_pass = os.getenv("ADMIN_PASSWORD", "admin123")
                
                logger.info(f"Creating default superadmin user: {admin_user}...")
                
                # Check if user already exists (shouldn't since we just dropped tables)
                user_in = UserCreate(
                    username=admin_user,
                    password=admin_pass,
                    role=UserRole.SUPERADMIN
                )
                create_user(db, user_in)
                logger.info(f"✅ Default superadmin created (username: {admin_user}, password: {admin_pass})")
                logger.info("⚠️ PLEASE CHANGE THE DEFAULT PASSWORD AFTER LOGIN!")
            finally:
                db.close()

        logger.info("✅ Database reset successfully! All data has been cleared.")

    except Exception as e:
        logger.error(f"Error resetting database: {e}")
        raise

if __name__ == "__main__":
    load_dotenv()
    reset_database()
