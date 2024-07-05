from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from auth import get_current_user
from models import User
from database import session_scope


def get_db():
    with session_scope() as session:
        yield session


def get_current_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource."
        )
    return current_user


def get_current_regular_user(current_user: User = Depends(get_current_user)):
    if current_user.role != 'user':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource."
        )
    return current_user
