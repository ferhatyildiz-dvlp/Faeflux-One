"""
Application Configuration
"""

from pydantic_settings import BaseSettings
from typing import List
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "Faeflux One"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"

    # Database
    DATABASE_URL: str = "postgresql://faeflux:changeme@localhost:5432/faeflux_one"
    DATABASE_ECHO: bool = False

    # Security
    SECRET_KEY: str = "change-this-secret-key-in-production"
    JWT_ALGORITHM: str = "RS256"
    JWT_PRIVATE_KEY_PATH: str = "./private.pem"
    JWT_PUBLIC_KEY_PATH: str = "./public.pem"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 14

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # Allowed Hosts
    ALLOWED_HOSTS: List[str] = ["localhost"]

    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# Load RSA keys
BASE_DIR = Path(__file__).resolve().parent.parent.parent
PRIVATE_KEY_PATH = BASE_DIR / settings.JWT_PRIVATE_KEY_PATH
PUBLIC_KEY_PATH = BASE_DIR / settings.JWT_PUBLIC_KEY_PATH

# Ensure keys exist
if not PRIVATE_KEY_PATH.exists() or not PUBLIC_KEY_PATH.exists():
    import warnings
    warnings.warn(
        "JWT keys not found. Please generate RSA key pair using:\n"
        "openssl genrsa -out private.pem 2048\n"
        "openssl rsa -in private.pem -pubout -out public.pem"
    )


