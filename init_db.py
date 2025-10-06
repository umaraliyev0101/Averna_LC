"""
Database initialization script
Run this once after deployment to create tables and initial data
"""
from app.core.database import engine
from app.models import Base
from app.core.auth import get_password_hash
from sqlalchemy.orm import sessionmaker
from app.models import User, UserRole

def init_database():
    """Initialize database with tables and admin user"""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")
    
    # Create session
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = session_local()
    
    try:
        # Check if admin user exists
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            # Create admin user
            admin_user = User(
                username="admin",
                hashed_password=get_password_hash("admin123"),
                role="admin"  # Use string instead of enum
            )
            db.add(admin_user)
            print("✅ Admin user created (username: admin, password: admin123)")
        else:
            print("ℹ️ Admin user already exists")
            
        # Check if superadmin user exists
        superadmin_user = db.query(User).filter(User.username == "superadmin").first()
        if not superadmin_user:
            # Create superadmin user
            superadmin_user = User(
                username="superadmin",
                hashed_password=get_password_hash("super123"),
                role="superadmin"
            )
            db.add(superadmin_user)
            print("✅ Superadmin user created (username: superadmin, password: super123)")
        else:
            print("ℹ️ Superadmin user already exists")
            
        db.commit()
            
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🗄️ Initializing database...")
    init_database()
    print("✅ Database initialization complete!")
