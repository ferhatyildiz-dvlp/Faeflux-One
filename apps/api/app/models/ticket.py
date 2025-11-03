"""
Ticket Model
"""

from datetime import datetime
from enum import Enum
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship, Column, Text

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.asset import Asset


class TicketStatus(str, Enum):
    """Ticket status."""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class TicketPriority(str, Enum):
    """Ticket priority."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TicketBase(SQLModel):
    """Base ticket model."""
    title: str = Field(max_length=255, index=True)
    description: str = Field(sa_column=Column(Text))
    status: TicketStatus = Field(default=TicketStatus.OPEN)
    priority: TicketPriority = Field(default=TicketPriority.MEDIUM)
    asset_id: Optional[int] = Field(default=None, foreign_key="asset.id")
    assigned_to_id: Optional[int] = Field(default=None, foreign_key="user.id")


class Ticket(TicketBase, table=True):
    """Ticket table model."""
    __tablename__ = "ticket"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    created_by_id: int = Field(foreign_key="user.id")
    
    # Relationships
    asset: Optional["Asset"] = Relationship(back_populates="tickets")
    created_by_user: "User" = Relationship(
        back_populates="created_tickets",
        sa_relationship_kwargs={"foreign_keys": "[Ticket.created_by_id]"}
    )
    assigned_to: Optional["User"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Ticket.assigned_to_id]"}
    )


class TicketCreate(SQLModel):
    """Ticket creation schema."""
    title: str
    description: str
    priority: TicketPriority = TicketPriority.MEDIUM
    asset_id: Optional[int] = None
    assigned_to_id: Optional[int] = None


class TicketUpdate(SQLModel):
    """Ticket update schema."""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    asset_id: Optional[int] = None
    assigned_to_id: Optional[int] = None


class TicketResponse(SQLModel):
    """Ticket response schema."""
    id: int
    title: str
    description: str
    status: TicketStatus
    priority: TicketPriority
    asset_id: Optional[int] = None
    assigned_to_id: Optional[int] = None
    created_by_id: int
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None

