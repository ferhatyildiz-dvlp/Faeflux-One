"""
Asset Management Endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlmodel import Session, select
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.database import get_session
from app.core.dependencies import get_current_user, create_audit_log
from app.core.permissions import Permission, has_permission
from app.core.config import settings
from app.models.asset import Asset, AssetCreate, AssetUpdate, AssetResponse
from app.models.user import User
from app.models.audit_log import AuditAction
from datetime import datetime

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.get("", response_model=List[AssetResponse])
async def list_assets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """List assets (requires ASSET_VIEW permission)."""
    if not has_permission(current_user, Permission.ASSET_VIEW):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        )
    
    statement = select(Asset).offset(skip).limit(limit)
    assets = session.exec(statement).all()
    return assets


@router.post("", response_model=AssetResponse)
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def create_asset(
    asset_data: AssetCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Create asset (requires ASSET_CREATE permission)."""
    if not has_permission(current_user, Permission.ASSET_CREATE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        )
    
    asset = Asset(
        **asset_data.dict(),
        created_by_id=current_user.id,
    )
    session.add(asset)
    session.commit()
    session.refresh(asset)
    
    # Audit log
    create_audit_log(
        session,
        current_user.id,
        AuditAction.CREATE,
        "asset",
        asset.id,
        f"Created asset: {asset.name}",
        request.client.host if request.client else None,
        request.headers.get("user-agent"),
    )
    
    return asset


@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(
    asset_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get asset by ID (requires ASSET_VIEW permission)."""
    if not has_permission(current_user, Permission.ASSET_VIEW):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        )
    
    asset = session.get(Asset, asset_id)
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found",
        )
    
    return asset


@router.put("/{asset_id}", response_model=AssetResponse)
async def update_asset(
    asset_id: int,
    asset_data: AssetUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Update asset (requires ASSET_EDIT permission)."""
    if not has_permission(current_user, Permission.ASSET_EDIT):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        )
    
    asset = session.get(Asset, asset_id)
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found",
        )
    
    # Update fields
    update_data = asset_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(asset, field, value)
    
    asset.updated_at = datetime.utcnow()
    
    session.add(asset)
    session.commit()
    session.refresh(asset)
    
    # Audit log
    create_audit_log(
        session,
        current_user.id,
        AuditAction.UPDATE,
        "asset",
        asset.id,
        f"Updated asset: {asset.name}",
        request.client.host if request.client else None,
        request.headers.get("user-agent"),
    )
    
    return asset


@router.delete("/{asset_id}")
async def delete_asset(
    asset_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Delete asset (requires ASSET_DELETE permission)."""
    if not has_permission(current_user, Permission.ASSET_DELETE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        )
    
    asset = session.get(Asset, asset_id)
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found",
        )
    
    # Audit log
    create_audit_log(
        session,
        current_user.id,
        AuditAction.DELETE,
        "asset",
        asset.id,
        f"Deleted asset: {asset.name}",
        request.client.host if request.client else None,
        request.headers.get("user-agent"),
    )
    
    session.delete(asset)
    session.commit()
    
    return {"message": "Asset deleted successfully"}

