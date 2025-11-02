"""
Create initial admin user
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from sqlmodel import Session, select
from app.core.database import engine
from app.core.auth import get_password_hash
from app.models.user import User, UserRole

def create_admin():
    """Create admin user if it doesn't exist."""
    with Session(engine) as session:
        # Check if admin exists
        statement = select(User).where(User.email == "admin@faeflux.local")
        existing = session.exec(statement).first()
        
        if existing:
            print("Admin user already exists.")
            return
        
        # Create admin user
        admin = User(
            email="admin@faeflux.local",
            hashed_password=get_password_hash("Admin@123!"),
            full_name="System Administrator",
            role=UserRole.ADMIN,
            is_active=True,
        )
        
        session.add(admin)
        session.commit()
        
        print("Admin user created successfully!")
        print(f"Email: admin@faeflux.local")
        print(f"Password: Admin@123!")
        print("\n⚠️  IMPORTANT: Change the password immediately after first login!")

if __name__ == "__main__":
    create_admin()

