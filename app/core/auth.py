from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from passlib.hash import bcrypt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

from ..models import User, UserRole
from ..schemas import TokenData

load_dotenv()

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Simple password hashing using hashlib (avoiding bcrypt issues)
import hashlib
import secrets

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash"""
    try:
        # Try bcrypt first (for existing passwords)
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # Fallback to SHA256 + salt verification
        if ':' in hashed_password:
            salt, hash_part = hashed_password.split(':', 1)
            return hash_part == hashlib.sha256((salt + plain_password).encode()).hexdigest()
        return False

def get_password_hash(password: str) -> str:
    """Hash a password using SHA256 + salt (avoiding bcrypt issues)"""
    # Generate a random salt
    salt = secrets.token_hex(16)
    # Create hash with salt
    hash_part = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}:{hash_part}"

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> TokenData:
    """Verify JWT token and extract user data"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token_data = TokenData(username=username, role=role)
        return token_data
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Authenticate user credentials"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


