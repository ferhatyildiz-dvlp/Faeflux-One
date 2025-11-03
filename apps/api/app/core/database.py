"""
Database Configuration and Session Management
"""

from sqlmodel import SQLModel, Session, create_engine
from app.core.config import settings
import structlog

logger = structlog.get_logger()

engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)


async def init_db():
    """Initialize database tables."""
    logger.info("Initializing database")
    SQLModel.metadata.create_all(engine)
    logger.info("Database initialized")


def get_session():
    """Get database session."""
    with Session(engine) as session:
        yield session


