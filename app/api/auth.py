from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from ..core.database import get_db
from ..core.auth import authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from ..schemas import Token, LoginRequest

router = APIRouter()

@router.post("/login", response_model=Token)
def simple_login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """Simple login with just username and password - returns JWT token with user info"""
    user = authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username,
        "role": user.role
    }

@router.post("/token", response_model=Token)
def login_for_access_token(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """Authenticate user and return JWT token with user info - alias for /login"""
    user = authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username,
        "role": user.role
    }
