"""
Ticket Management Endpoints
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
from app.models.ticket import Ticket, TicketCreate, TicketUpdate, TicketResponse
from app.models.user import User
from app.models.audit_log import AuditAction
from datetime import datetime

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.get("", response_model=List[TicketResponse])
async def list_tickets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """List tickets (requires TICKET_VIEW permission)."""
    if not has_permission(current_user, Permission.TICKET_VIEW):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        )
    
    statement = select(Ticket).offset(skip).limit(limit)
    tickets = session.exec(statement).all()
    return tickets


@router.post("", response_model=TicketResponse)
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def create_ticket(
    ticket_data: TicketCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Create ticket (requires TICKET_CREATE permission)."""
    if not has_permission(current_user, Permission.TICKET_CREATE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        )
    
    ticket = Ticket(
        **ticket_data.dict(),
        created_by_id=current_user.id,
    )
    session.add(ticket)
    session.commit()
    session.refresh(ticket)
    
    # Audit log
    create_audit_log(
        session,
        current_user.id,
        AuditAction.CREATE,
        "ticket",
        ticket.id,
        f"Created ticket: {ticket.title}",
        request.client.host if request.client else None,
        request.headers.get("user-agent"),
    )
    
    return ticket


@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    ticket_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get ticket by ID (requires TICKET_VIEW permission)."""
    if not has_permission(current_user, Permission.TICKET_VIEW):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        )
    
    ticket = session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )
    
    return ticket


@router.put("/{ticket_id}", response_model=TicketResponse)
async def update_ticket(
    ticket_id: int,
    ticket_data: TicketUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Update ticket (requires TICKET_EDIT permission)."""
    if not has_permission(current_user, Permission.TICKET_EDIT):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        )
    
    ticket = session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )
    
    # Update fields
    update_data = ticket_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(ticket, field, value)
    
    # Auto-set resolved_at if status is resolved/closed
    if ticket.status.value in ["resolved", "closed"] and not ticket.resolved_at:
        ticket.resolved_at = datetime.utcnow()
    
    ticket.updated_at = datetime.utcnow()
    
    session.add(ticket)
    session.commit()
    session.refresh(ticket)
    
    # Audit log
    create_audit_log(
        session,
        current_user.id,
        AuditAction.UPDATE,
        "ticket",
        ticket.id,
        f"Updated ticket: {ticket.title}",
        request.client.host if request.client else None,
        request.headers.get("user-agent"),
    )
    
    return ticket


@router.delete("/{ticket_id}")
async def delete_ticket(
    ticket_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Delete ticket (requires TICKET_DELETE permission)."""
    if not has_permission(current_user, Permission.TICKET_DELETE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        )
    
    ticket = session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )
    
    # Audit log
    create_audit_log(
        session,
        current_user.id,
        AuditAction.DELETE,
        "ticket",
        ticket.id,
        f"Deleted ticket: {ticket.title}",
        request.client.host if request.client else None,
        request.headers.get("user-agent"),
    )
    
    session.delete(ticket)
    session.commit()
    
    return {"message": "Ticket deleted successfully"}

