# Quick Fix Guide - After Installation Failure

If your installation stopped at the pnpm step, follow these steps to continue:

## Step 1: Install pnpm

```bash
sudo npm install -g pnpm
```

Or use the pnpm installer:
```bash
curl -fsSL https://get.pnpm.io/install.sh | sh -
source ~/.bashrc
```

Verify installation:
```bash
pnpm --version
```

## Step 2: Continue with Backend Setup

```bash
cd ~/Faeflux-One/apps/api

# Create virtual environment if not exists
python3.12 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install PostgreSQL dev headers if psycopg2 fails
sudo apt-get install -y postgresql-server-dev-16 libpq-dev

# Retry if needed
pip install -r requirements.txt
```

## Step 3: Generate RSA Keys (if not done)

```bash
cd ~/Faeflux-One/apps/api

# Generate keys if they don't exist
if [ ! -f "private.pem" ]; then
    openssl genrsa -out private.pem 2048
    openssl rsa -in private.pem -pubout -out public.pem
    chmod 600 private.pem
    chmod 644 public.pem
fi
```

## Step 4: Configure Environment

```bash
cd ~/Faeflux-One/apps/api

# Create .env file if not exists
if [ ! -f ".env" ]; then
    cp .env.example .env
    # Edit with your database password
    nano .env
fi
```

Update `.env` with your database password:
```env
DATABASE_URL=postgresql://faeflux:YOUR_PASSWORD@localhost:5432/faeflux_one
```

## Step 5: Run Database Migrations

```bash
cd ~/Faeflux-One/apps/api
source venv/bin/activate

# Run migrations
alembic upgrade head

# If first time, create initial migration
if [ $? -ne 0 ]; then
    alembic revision --autogenerate -m "Initial migration"
    alembic upgrade head
fi
```

## Step 6: Create Admin User

```bash
cd ~/Faeflux-One/apps/api
source venv/bin/activate

python scripts/create_admin.py
```

Or manually:
```bash
python <<PYTHON_SCRIPT
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
from sqlmodel import Session
from app.core.database import engine
from app.core.auth import get_password_hash
from app.models.user import User, UserRole

with Session(engine) as session:
    admin_email = "admin@faeflux.com"  # Change if needed
    admin_password = "YourPassword123!"  # Change this!
    
    from sqlmodel import select
    statement = select(User).where(User.email == admin_email)
    existing = session.exec(statement).first()
    
    if existing:
        print("Admin user already exists.")
    else:
        admin = User(
            email=admin_email,
            hashed_password=get_password_hash(admin_password),
            full_name="System Administrator",
            role=UserRole.ADMIN,
            is_active=True,
        )
        session.add(admin)
        session.commit()
        print(f"Admin user created: {admin_email}")
PYTHON_SCRIPT
```

## Step 7: Setup Frontend

```bash
cd ~/Faeflux-One/apps/web

# Install dependencies
pnpm install

# Create .env.local
cat > .env.local <<EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
EOF
```

## Step 8: Test Installation

**Terminal 1 - Backend:**
```bash
cd ~/Faeflux-One/apps/api
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd ~/Faeflux-One/apps/web
pnpm dev
```

## Verify Everything Works

1. **Backend API:** http://localhost:8000/docs
2. **Frontend:** http://localhost:3000
3. **Health Check:** http://localhost:8000/health

## If You Still Have Issues

Check the installation log:
```bash
ls -lt ~/faeflux_install_*.log | head -1
```

Review errors and see TROUBLESHOOTING.md for more help.

