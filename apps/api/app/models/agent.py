"""
Agent Model
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict
from sqlmodel import SQLModel, Field, Column, JSON


class AgentStatus(str, Enum):
    """Agent status."""
    ONLINE = "online"
    OFFLINE = "offline"
    UNKNOWN = "unknown"


class AgentBase(SQLModel):
    """Base agent model."""
    name: str = Field(max_length=255, index=True)
    hostname: str = Field(max_length=255, index=True, unique=True)
    os_type: str = Field(max_length=50)  # windows, linux
    os_version: Optional[str] = Field(default=None, max_length=255)
    ip_address: Optional[str] = Field(default=None, max_length=45)
    status: AgentStatus = Field(default=AgentStatus.UNKNOWN)
    site_id: Optional[int] = Field(default=None, foreign_key="site.id")


class Agent(AgentBase, table=True):
    """Agent table model."""
    __tablename__ = "agent"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    last_heartbeat: Optional[datetime] = None
    inventory_data: Optional[Dict] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AgentCreate(SQLModel):
    """Agent creation schema."""
    name: str
    hostname: str
    os_type: str
    os_version: Optional[str] = None
    ip_address: Optional[str] = None
    site_id: Optional[int] = None


class AgentUpdate(SQLModel):
    """Agent update schema."""
    name: Optional[str] = None
    os_version: Optional[str] = None
    ip_address: Optional[str] = None
    status: Optional[AgentStatus] = None
    site_id: Optional[int] = None


class AgentResponse(SQLModel):
    """Agent response schema."""
    id: int
    name: str
    hostname: str
    os_type: str
    os_version: Optional[str] = None
    ip_address: Optional[str] = None
    status: AgentStatus
    site_id: Optional[int] = None
    last_heartbeat: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class AgentHeartbeat(SQLModel):
    """Agent heartbeat request."""
    hostname: str
    os_type: str
    os_version: Optional[str] = None
    ip_address: Optional[str] = None


class AgentInventory(SQLModel):
    """Agent inventory submission."""
    hostname: str
    inventory: Dict


