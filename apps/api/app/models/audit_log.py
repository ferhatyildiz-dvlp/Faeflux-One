"""
Audit Log Model
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship, Column, Text
from app.models.user import User


class AuditAction(str, Enum):
    """Audit action types."""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    VIEW = "view"
    EXPORT = "export"


class AuditLog(SQLModel, table=True):
    """Audit log table model."""
    __tablename__ = "audit_log"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    action: AuditAction
    resource_type: str = Field(max_length=100, index=True)
    resource_id: Optional[int] = Field(default=None, index=True)
    details: Optional[str] = Field(default=None, sa_column=Column(Text))
    ip_address: Optional[str] = Field(default=None, max_length=45)
    user_agent: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    # Relationships
    user: Optional["User"] = Relationship(back_populates="audit_logs")


class AuditLogResponse(SQLModel):
    """Audit log response schema."""
    id: int
    user_id: Optional[int] = None
    action: AuditAction
    resource_type: str
    resource_id: Optional[int] = None
    details: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime

