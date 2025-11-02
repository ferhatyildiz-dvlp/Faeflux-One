"""
Asset Model
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship, Column, Text

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.site import Site
    from app.models.ticket import Ticket


class AssetType(str, Enum):
    """Asset types."""
    COMPUTER = "computer"
    SERVER = "server"
    NETWORK_DEVICE = "network_device"
    PRINTER = "printer"
    MOBILE_DEVICE = "mobile_device"
    SOFTWARE = "software"
    OTHER = "other"


class AssetStatus(str, Enum):
    """Asset status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    RETIRED = "retired"


class AssetBase(SQLModel):
    """Base asset model."""
    name: str = Field(max_length=255, index=True)
    asset_type: AssetType
    status: AssetStatus = Field(default=AssetStatus.ACTIVE)
    serial_number: Optional[str] = Field(default=None, max_length=255, index=True)
    model: Optional[str] = Field(default=None, max_length=255)
    manufacturer: Optional[str] = Field(default=None, max_length=255)
    purchase_date: Optional[datetime] = None
    warranty_expiry: Optional[datetime] = None
    cost: Optional[float] = None
    location: Optional[str] = Field(default=None, max_length=255)
    notes: Optional[str] = Field(default=None, sa_column=Column(Text))
    site_id: Optional[int] = Field(default=None, foreign_key="site.id")


class Asset(AssetBase, table=True):
    """Asset table model."""
    __tablename__ = "asset"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by_id: int = Field(foreign_key="user.id")
    
    # Relationships
    site: Optional["Site"] = Relationship(back_populates="assets")
    created_by_user: "User" = Relationship(
        back_populates="created_assets",
        sa_relationship_kwargs={"foreign_keys": "[Asset.created_by_id]"}
    )
    tickets: List["Ticket"] = Relationship(back_populates="asset")


class AssetCreate(SQLModel):
    """Asset creation schema."""
    name: str
    asset_type: AssetType
    status: AssetStatus = AssetStatus.ACTIVE
    serial_number: Optional[str] = None
    model: Optional[str] = None
    manufacturer: Optional[str] = None
    purchase_date: Optional[datetime] = None
    warranty_expiry: Optional[datetime] = None
    cost: Optional[float] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    site_id: Optional[int] = None


class AssetUpdate(SQLModel):
    """Asset update schema."""
    name: Optional[str] = None
    asset_type: Optional[AssetType] = None
    status: Optional[AssetStatus] = None
    serial_number: Optional[str] = None
    model: Optional[str] = None
    manufacturer: Optional[str] = None
    purchase_date: Optional[datetime] = None
    warranty_expiry: Optional[datetime] = None
    cost: Optional[float] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    site_id: Optional[int] = None


class AssetResponse(SQLModel):
    """Asset response schema."""
    id: int
    name: str
    asset_type: AssetType
    status: AssetStatus
    serial_number: Optional[str] = None
    model: Optional[str] = None
    manufacturer: Optional[str] = None
    purchase_date: Optional[datetime] = None
    warranty_expiry: Optional[datetime] = None
    cost: Optional[float] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    site_id: Optional[int] = None
    created_by_id: int
    created_at: datetime
    updated_at: datetime

