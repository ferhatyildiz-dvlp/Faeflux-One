"""
User Model
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.audit_log import AuditLog
    from app.models.asset import Asset
    from app.models.ticket import Ticket
    from app.models.site import Site


class UserRole(str, Enum):
    """User roles."""
    ADMIN = "admin"
    MANAGER = "manager"
    ANALYST = "analyst"
    VIEWER = "viewer"


class UserBase(SQLModel):
    """Base user model."""
    email: str = Field(unique=True, index=True, max_length=255)
    full_name: str = Field(max_length=255)
    is_active: bool = Field(default=True)
    role: UserRole = Field(default=UserRole.VIEWER)
    site_id: Optional[int] = Field(default=None, foreign_key="site.id")


class User(UserBase, table=True):
    """User table model."""
    __tablename__ = "user"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    
    # Relationships
    site: Optional["Site"] = Relationship(back_populates="users")
    audit_logs: list["AuditLog"] = Relationship(back_populates="user")
    created_assets: list["Asset"] = Relationship(
        back_populates="created_by_user",
        sa_relationship_kwargs={"foreign_keys": "[Asset.created_by_id]"}
    )
    created_tickets: list["Ticket"] = Relationship(
        back_populates="created_by_user",
        sa_relationship_kwargs={"foreign_keys": "[Ticket.created_by_id]"}
    )


class UserCreate(SQLModel):
    """User creation schema."""
    email: str
    password: str
    full_name: str
    role: UserRole = UserRole.VIEWER
    site_id: Optional[int] = None


class UserUpdate(SQLModel):
    """User update schema."""
    email: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None
    site_id: Optional[int] = None


class UserResponse(SQLModel):
    """User response schema."""
    id: int
    email: str
    full_name: str
    is_active: bool
    role: UserRole
    site_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

