"""
JWT Authentication and Authorization
"""

from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import jwt, JWTError
from passlib.context import CryptContext
from pathlib import Path
from app.core.config import settings, PRIVATE_KEY_PATH, PUBLIC_KEY_PATH
import structlog

logger = structlog.get_logger()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def load_private_key() -> bytes:
    """Load RSA private key."""
    try:
        return PRIVATE_KEY_PATH.read_bytes()
    except FileNotFoundError:
        logger.error("Private key not found", path=str(PRIVATE_KEY_PATH))
        raise


def load_public_key() -> bytes:
    """Load RSA public key."""
    try:
        return PUBLIC_KEY_PATH.read_bytes()
    except FileNotFoundError:
        logger.error("Public key not found", path=str(PUBLIC_KEY_PATH))
        raise


def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({"exp": expire, "type": "access"})
    
    private_key = load_private_key()
    encoded_jwt = jwt.encode(
        to_encode,
        private_key,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(data: Dict) -> str:
    """Create JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
    )
    to_encode.update({"exp": expire, "type": "refresh"})
    
    private_key = load_private_key()
    encoded_jwt = jwt.encode(
        to_encode,
        private_key,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> Optional[Dict]:
    """Verify and decode JWT token."""
    try:
        public_key = load_public_key()
        payload = jwt.decode(
            token,
            public_key,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        if payload.get("type") != token_type:
            logger.warning("Invalid token type", expected=token_type, got=payload.get("type"))
            return None
        
        return payload
    except JWTError as e:
        logger.warning("JWT verification failed", error=str(e))
        return None

