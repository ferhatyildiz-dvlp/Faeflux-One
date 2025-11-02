"""
Agent Communication Endpoints
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
from app.models.agent import (
    Agent,
    AgentCreate,
    AgentUpdate,
    AgentResponse,
    AgentHeartbeat,
    AgentInventory,
    AgentStatus,
)
from app.models.user import User
from app.models.audit_log import AuditAction
from datetime import datetime

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.get("", response_model=List[AgentResponse])
async def list_agents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """List agents (requires AGENT_VIEW permission)."""
    if not has_permission(current_user, Permission.AGENT_VIEW):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        )
    
    statement = select(Agent).offset(skip).limit(limit)
    agents = session.exec(statement).all()
    return agents


@router.post("/heartbeat")
@limiter.limit("300/minute")  # Allow more frequent heartbeats
async def agent_heartbeat(
    heartbeat_data: AgentHeartbeat,
    request: Request,
    session: Session = Depends(get_session),
):
    """Agent heartbeat endpoint (no authentication required for agents)."""
    # Find or create agent
    statement = select(Agent).where(Agent.hostname == heartbeat_data.hostname)
    agent = session.exec(statement).first()
    
    if not agent:
        # Create new agent
        agent = Agent(
            name=heartbeat_data.hostname,
            hostname=heartbeat_data.hostname,
            os_type=heartbeat_data.os_type,
            os_version=heartbeat_data.os_version,
            ip_address=heartbeat_data.ip_address or request.client.host if request.client else None,
            status=AgentStatus.ONLINE,
            last_heartbeat=datetime.utcnow(),
        )
        session.add(agent)
    else:
        # Update existing agent
        agent.os_type = heartbeat_data.os_type
        agent.os_version = heartbeat_data.os_version or agent.os_version
        agent.ip_address = heartbeat_data.ip_address or request.client.host if request.client else agent.ip_address
        agent.status = AgentStatus.ONLINE
        agent.last_heartbeat = datetime.utcnow()
        agent.updated_at = datetime.utcnow()
    
    session.commit()
    session.refresh(agent)
    
    return {"status": "ok", "agent_id": agent.id}


@router.post("/inventory")
@limiter.limit("10/minute")  # Limit inventory submissions
async def agent_inventory(
    inventory_data: AgentInventory,
    request: Request,
    session: Session = Depends(get_session),
):
    """Agent inventory submission endpoint (no authentication required for agents)."""
    # Find agent
    statement = select(Agent).where(Agent.hostname == inventory_data.hostname)
    agent = session.exec(statement).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found. Please send heartbeat first.",
        )
    
    # Update inventory
    agent.inventory_data = inventory_data.inventory
    agent.updated_at = datetime.utcnow()
    
    session.add(agent)
    session.commit()
    
    return {"status": "ok", "message": "Inventory updated"}


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get agent by ID (requires AGENT_VIEW permission)."""
    if not has_permission(current_user, Permission.AGENT_VIEW):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        )
    
    agent = session.get(Agent, agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )
    
    return agent


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: int,
    agent_data: AgentUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Update agent (requires AGENT_MANAGE permission)."""
    if not has_permission(current_user, Permission.AGENT_MANAGE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        )
    
    agent = session.get(Agent, agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )
    
    # Update fields
    update_data = agent_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(agent, field, value)
    
    agent.updated_at = datetime.utcnow()
    
    session.add(agent)
    session.commit()
    session.refresh(agent)
    
    # Audit log
    create_audit_log(
        session,
        current_user.id,
        AuditAction.UPDATE,
        "agent",
        agent.id,
        f"Updated agent: {agent.name}",
        request.client.host if request.client else None,
        request.headers.get("user-agent"),
    )
    
    return agent

