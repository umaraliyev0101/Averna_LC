"""
User management script for Railway deployment
Run this to add/manage users after deployment
"""
from app.core.database import SessionLocal, engine
from app.models import User
from app.core.auth import get_password_hash
import sys

def create_user(username, password, role):
    """Create a new user"""
    db = SessionLocal()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            print(f"❌ User '{username}' already exists")
            return False
        
        # Create new user
        new_user = User(
            username=username,
            hashed_password=get_password_hash(password),
            role=role
        )
        db.add(new_user)
        db.commit()
        print(f"✅ User '{username}' created with role '{role}'")
        return True
        
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def list_users():
    """List all users"""
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print("\n📋 Current Users:")
        print("-" * 40)
        for user in users:
            print(f"  Username: {user.username}")
            print(f"  Role: {user.role}")
            print(f"  ID: {user.id}")
            print("-" * 40)
    except Exception as e:
        print(f"❌ Error listing users: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("🔧 User Management Commands:")
        print("  python manage_users.py list")
        print("  python manage_users.py create <username> <password> <role>")
        print("")
        print("Available roles: admin, teacher, superadmin")
        print("Example: python manage_users.py create superadmin super123 superadmin")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "list":
        list_users()
    elif command == "create" and len(sys.argv) == 5:
        username = sys.argv[2]
        password = sys.argv[3]
        role = sys.argv[4]
        
        if role not in ["admin", "teacher", "superadmin"]:
            print("❌ Invalid role. Use: admin, teacher, or superadmin")
            sys.exit(1)
            
        create_user(username, password, role)
    else:
        print("❌ Invalid command format")
        print("Use: python manage_users.py list")
        print("Or:  python manage_users.py create <username> <password> <role>")
