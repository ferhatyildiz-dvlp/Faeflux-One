"""
Role-Based Access Control (RBAC)
"""

from enum import Enum
from typing import List, Dict
from fastapi import HTTPException, status
from app.models.user import User, UserRole


class Permission(str, Enum):
    """Available permissions."""
    
    # Users
    USER_VIEW = "user:view"
    USER_CREATE = "user:create"
    USER_EDIT = "user:edit"
    USER_DELETE = "user:delete"
    
    # Assets
    ASSET_VIEW = "asset:view"
    ASSET_CREATE = "asset:create"
    ASSET_EDIT = "asset:edit"
    ASSET_DELETE = "asset:delete"
    
    # Tickets
    TICKET_VIEW = "ticket:view"
    TICKET_CREATE = "ticket:create"
    TICKET_EDIT = "ticket:edit"
    TICKET_DELETE = "ticket:delete"
    
    # Sites
    SITE_VIEW = "site:view"
    SITE_CREATE = "site:create"
    SITE_EDIT = "site:edit"
    SITE_DELETE = "site:delete"
    
    # Agents
    AGENT_VIEW = "agent:view"
    AGENT_MANAGE = "agent:manage"
    
    # System
    SYSTEM_ADMIN = "system:admin"
    AUDIT_VIEW = "audit:view"


ROLE_PERMISSIONS: Dict[UserRole, List[Permission]] = {
    UserRole.ADMIN: list(Permission),  # All permissions
    
    UserRole.MANAGER: [
        Permission.USER_VIEW,
        Permission.USER_CREATE,
        Permission.USER_EDIT,
        Permission.ASSET_VIEW,
        Permission.ASSET_CREATE,
        Permission.ASSET_EDIT,
        Permission.ASSET_DELETE,
        Permission.TICKET_VIEW,
        Permission.TICKET_CREATE,
        Permission.TICKET_EDIT,
        Permission.SITE_VIEW,
        Permission.SITE_CREATE,
        Permission.SITE_EDIT,
        Permission.AGENT_VIEW,
        Permission.AUDIT_VIEW,
    ],
    
    UserRole.ANALYST: [
        Permission.USER_VIEW,
        Permission.ASSET_VIEW,
        Permission.ASSET_EDIT,
        Permission.TICKET_VIEW,
        Permission.TICKET_CREATE,
        Permission.TICKET_EDIT,
        Permission.SITE_VIEW,
        Permission.AGENT_VIEW,
    ],
    
    UserRole.VIEWER: [
        Permission.USER_VIEW,
        Permission.ASSET_VIEW,
        Permission.TICKET_VIEW,
        Permission.SITE_VIEW,
    ],
}


def get_user_permissions(role: UserRole) -> List[Permission]:
    """Get permissions for a role."""
    return ROLE_PERMISSIONS.get(role, [])


def has_permission(user: User, permission: Permission) -> bool:
    """Check if user has a specific permission."""
    user_permissions = get_user_permissions(user.role)
    return permission in user_permissions


def require_permission(permission: Permission):
    """Decorator to require a specific permission."""
    def decorator(func):
        async def wrapper(*args, user: User = None, **kwargs):
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            if not has_permission(user, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: {permission}"
                )
            
            return await func(*args, user=user, **kwargs)
        return wrapper
    return decorator

