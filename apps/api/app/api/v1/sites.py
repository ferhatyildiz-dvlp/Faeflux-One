"""
Site Management Endpoints
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
from app.models.site import Site, SiteCreate, SiteUpdate, SiteResponse
from app.models.user import User
from app.models.audit_log import AuditAction
from datetime import datetime

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.get("", response_model=List[SiteResponse])
async def list_sites(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """List sites (requires SITE_VIEW permission)."""
    if not has_permission(current_user, Permission.SITE_VIEW):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        )
    
    statement = select(Site).offset(skip).limit(limit)
    sites = session.exec(statement).all()
    return sites


@router.post("", response_model=SiteResponse)
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def create_site(
    site_data: SiteCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Create site (requires SITE_CREATE permission)."""
    if not has_permission(current_user, Permission.SITE_CREATE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        )
    
    site = Site(**site_data.dict())
    session.add(site)
    session.commit()
    session.refresh(site)
    
    # Audit log
    create_audit_log(
        session,
        current_user.id,
        AuditAction.CREATE,
        "site",
        site.id,
        f"Created site: {site.name}",
        request.client.host if request.client else None,
        request.headers.get("user-agent"),
    )
    
    return site


@router.get("/{site_id}", response_model=SiteResponse)
async def get_site(
    site_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get site by ID (requires SITE_VIEW permission)."""
    if not has_permission(current_user, Permission.SITE_VIEW):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        )
    
    site = session.get(Site, site_id)
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found",
        )
    
    return site


@router.put("/{site_id}", response_model=SiteResponse)
async def update_site(
    site_id: int,
    site_data: SiteUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Update site (requires SITE_EDIT permission)."""
    if not has_permission(current_user, Permission.SITE_EDIT):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        )
    
    site = session.get(Site, site_id)
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found",
        )
    
    # Update fields
    update_data = site_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(site, field, value)
    
    site.updated_at = datetime.utcnow()
    
    session.add(site)
    session.commit()
    session.refresh(site)
    
    # Audit log
    create_audit_log(
        session,
        current_user.id,
        AuditAction.UPDATE,
        "site",
        site.id,
        f"Updated site: {site.name}",
        request.client.host if request.client else None,
        request.headers.get("user-agent"),
    )
    
    return site


@router.delete("/{site_id}")
async def delete_site(
    site_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Delete site (requires SITE_DELETE permission)."""
    if not has_permission(current_user, Permission.SITE_DELETE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        )
    
    site = session.get(Site, site_id)
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found",
        )
    
    # Audit log
    create_audit_log(
        session,
        current_user.id,
        AuditAction.DELETE,
        "site",
        site.id,
        f"Deleted site: {site.name}",
        request.client.host if request.client else None,
        request.headers.get("user-agent"),
    )
    
    session.delete(site)
    session.commit()
    
    return {"message": "Site deleted successfully"}

