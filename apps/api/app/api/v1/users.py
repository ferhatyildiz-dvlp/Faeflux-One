"""
User Management Endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlmodel import Session, select
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.database import get_session
from app.core.auth import get_password_hash
from app.core.dependencies import get_current_user, create_audit_log
from app.core.permissions import Permission, has_permission
from app.core.config import settings
from app.models.user import User, UserCreate, UserUpdate, UserResponse, UserRole
from app.models.audit_log import AuditAction

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.get("", response_model=List[UserResponse])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """List users (requires USER_VIEW permission)."""
    if not has_permission(current_user, Permission.USER_VIEW):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        )
    
    statement = select(User).offset(skip).limit(limit)
    users = session.exec(statement).all()
    return users


@router.post("", response_model=UserResponse)
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def create_user(
    user_data: UserCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Create user (requires USER_CREATE permission)."""
    if not has_permission(current_user, Permission.USER_CREATE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        )
    
    # Check if email exists
    statement = select(User).where(User.email == user_data.email)
    existing = session.exec(statement).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        role=user_data.role,
        site_id=user_data.site_id,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    
    # Audit log
    create_audit_log(
        session,
        current_user.id,
        AuditAction.CREATE,
        "user",
        user.id,
        f"Created user: {user.email}",
        request.client.host if request.client else None,
        request.headers.get("user-agent"),
    )
    
    return user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get user by ID (requires USER_VIEW permission)."""
    if not has_permission(current_user, Permission.USER_VIEW):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        )
    
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Update user (requires USER_EDIT permission)."""
    if not has_permission(current_user, Permission.USER_EDIT):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        )
    
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Update fields
    update_data = user_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    from datetime import datetime
    user.updated_at = datetime.utcnow()
    
    session.add(user)
    session.commit()
    session.refresh(user)
    
    # Audit log
    create_audit_log(
        session,
        current_user.id,
        AuditAction.UPDATE,
        "user",
        user.id,
        f"Updated user: {user.email}",
        request.client.host if request.client else None,
        request.headers.get("user-agent"),
    )
    
    return user


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Delete user (requires USER_DELETE permission)."""
    if not has_permission(current_user, Permission.USER_DELETE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        )
    
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Prevent self-deletion
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete own account",
        )
    
    # Audit log
    create_audit_log(
        session,
        current_user.id,
        AuditAction.DELETE,
        "user",
        user.id,
        f"Deleted user: {user.email}",
        request.client.host if request.client else None,
        request.headers.get("user-agent"),
    )
    
    session.delete(user)
    session.commit()
    
    return {"message": "User deleted successfully"}

