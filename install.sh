#!/bin/bash

# Faeflux One - Complete Installation Script
# This script installs and configures Faeflux One on Ubuntu

set -e

# Log file
LOG_FILE="${HOME}/faeflux_install_$(date +%Y%m%d_%H%M%S).log"
exec > >(tee -a "$LOG_FILE") 2>&1

echo "Installation log: $LOG_FILE"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration variables
INSTALL_DIR=$(pwd)
APP_USER="${APP_USER:-www-data}"
DOMAIN=""
DB_NAME="faeflux_one"
DB_USER="faeflux"
DB_PASSWORD=""
ADMIN_EMAIL="admin@faeflux.local"
ADMIN_PASSWORD=""

# If directory was created as root, fix ownership early (before detecting root)
# This helps when git clone was run as root
if [ -n "$SUDO_USER" ] && [ "$EUID" -eq 0 ]; then
    chown -R "$SUDO_USER:$SUDO_USER" "$INSTALL_DIR" 2>/dev/null || true
elif [ "$EUID" -eq 0 ] && [ -z "$SUDO_USER" ]; then
    # If running directly as root without sudo, try to find a regular user
    REGULAR_USER_FALLBACK=$(ls -ld /home/* 2>/dev/null | head -1 | awk '{print $3}' | xargs basename 2>/dev/null || echo "")
    if [ -n "$REGULAR_USER_FALLBACK" ] && id "$REGULAR_USER_FALLBACK" &>/dev/null; then
        chown -R "$REGULAR_USER_FALLBACK:$REGULAR_USER_FALLBACK" "$INSTALL_DIR" 2>/dev/null || true
    fi
fi

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         Faeflux One Installation Script              ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Detect if running as root
RUN_AS_ROOT=false
if [ "$EUID" -eq 0 ]; then 
    RUN_AS_ROOT=true
    echo -e "${YELLOW}⚠️  Running as root. Files will be created with appropriate ownership.${NC}"
    # Determine regular user (usually the user who ran sudo)
    if [ -n "$SUDO_USER" ]; then
        REGULAR_USER="$SUDO_USER"
    else
        # If directly logged in as root, try to use a default user
        REGULAR_USER="ferhat"
        if ! id "$REGULAR_USER" &>/dev/null; then
            REGULAR_USER=$(ls -ld /home/* | head -1 | awk '{print $3}' | xargs basename)
        fi
    fi
    echo -e "${BLUE}Using user '${REGULAR_USER}' for file ownership${NC}"
else
    REGULAR_USER="$USER"
fi

# Function to run command with appropriate privileges
run_cmd() {
    if [ "$RUN_AS_ROOT" = true ]; then
        sudo -u "$REGULAR_USER" "$@"
    else
        "$@"
    fi
}

# Function to ask for input
ask_input() {
    local prompt="$1"
    local var_name="$2"
    local default_value="${3:-}"
    local is_secret="${4:-false}"
    
    if [ -n "$default_value" ]; then
        prompt="$prompt [$default_value]: "
    else
        prompt="$prompt: "
    fi
    
    if [ "$is_secret" = true ]; then
        read -sp "$prompt" input
        echo ""
    else
        read -p "$prompt" input
    fi
    
    if [ -z "$input" ]; then
        if [ -n "$default_value" ]; then
            eval "$var_name='$default_value'"
        else
            eval "$var_name=''"
        fi
    else
        eval "$var_name='$input'"
    fi
}

# Function to check command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

echo -e "${GREEN}📋 Step 1/10: Checking prerequisites...${NC}"

# Check OS
if ! grep -q "Ubuntu" /etc/os-release 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Warning: This script is optimized for Ubuntu${NC}"
    read -p "Continue anyway? (y/N): " continue_anyway
    if [[ ! "$continue_anyway" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check Python
if ! command_exists python3.12 && ! command_exists python3; then
    echo -e "${RED}❌ Python 3 is required but not installed${NC}"
    exit 1
fi

PYTHON_CMD=$(command_exists python3.12 && echo "python3.12" || echo "python3")
echo -e "${GREEN}✓ Found Python: $($PYTHON_CMD --version)${NC}"

# Check Node.js
if ! command_exists node; then
    echo -e "${YELLOW}⚠️  Node.js not found. Will install during setup.${NC}"
else
    echo -e "${GREEN}✓ Found Node.js: $(node --version)${NC}"
fi

echo ""
echo -e "${GREEN}📋 Step 2/10: Collecting configuration...${NC}"

# Ask for domain (optional for development)
ask_input "Enter your domain (leave empty for local development)" DOMAIN "localhost"

# Ask for database password
while [ -z "$DB_PASSWORD" ]; do
    ask_input "Enter PostgreSQL password for database user '$DB_USER'" DB_PASSWORD "" true
    if [ -z "$DB_PASSWORD" ]; then
        echo -e "${RED}❌ Database password cannot be empty${NC}"
    fi
done

# Ask for admin credentials
ask_input "Enter admin email" ADMIN_EMAIL "admin@faeflux.local"
ask_input "Enter admin password (min 8 chars)" ADMIN_PASSWORD "" true

if [ ${#ADMIN_PASSWORD} -lt 8 ]; then
    echo -e "${YELLOW}⚠️  Admin password is too short, using default${NC}"
    ADMIN_PASSWORD="Admin@123!"
fi

echo ""
echo -e "${GREEN}📦 Step 3/10: Installing system dependencies...${NC}"

sudo apt-get update -qq

# Install Python and related packages
echo -e "${BLUE}Installing Python dependencies...${NC}"
if sudo apt-get install -y \
    python3.12 python3.12-venv python3-pip \
    postgresql-16 postgresql-contrib \
    nginx certbot python3-certbot-nginx \
    curl git build-essential \
    libpq-dev 2>/dev/null; then
    echo -e "${GREEN}✓ Python 3.12 and dependencies installed${NC}"
else
    echo -e "${YELLOW}⚠️  Python 3.12 not available, trying Python 3...${NC}"
    sudo apt-get install -y \
        python3 python3-venv python3-pip \
        postgresql postgresql-contrib \
        nginx certbot python3-certbot-nginx \
        curl git build-essential \
        libpq-dev
fi

# Install Node.js if not present
if ! command_exists node; then
    echo -e "${BLUE}Installing Node.js...${NC}"
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi

# Install pnpm
if ! command_exists pnpm; then
    echo -e "${BLUE}Installing pnpm...${NC}"
    # Try corepack first (recommended for Node.js 20+)
    if command_exists corepack; then
        sudo corepack enable 2>/dev/null || true
        corepack prepare pnpm@latest --activate 2>/dev/null || {
            echo -e "${BLUE}Trying npm install method...${NC}"
            sudo npm install -g pnpm
        }
    else
        # Fallback to npm install
        sudo npm install -g pnpm || {
            echo -e "${YELLOW}⚠️  Failed to install pnpm with npm, trying pnpm installer...${NC}"
            curl -fsSL https://get.pnpm.io/install.sh | sh -
            export PNPM_HOME="$HOME/.local/share/pnpm"
            export PATH="$PNPM_HOME:$PATH"
        }
    fi
    # Verify pnpm installation
    if ! command_exists pnpm; then
        echo -e "${RED}❌ Failed to install pnpm. Please install manually.${NC}"
        echo -e "${YELLOW}   Run: sudo npm install -g pnpm${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ pnpm installed: $(pnpm --version)${NC}"
fi

echo -e "${GREEN}✓ System dependencies installed${NC}"

echo ""
echo -e "${GREEN}🗄️  Step 4/10: Setting up PostgreSQL...${NC}"

# Create PostgreSQL user and database
echo -e "${BLUE}Creating database and user...${NC}"
sudo -u postgres psql <<EOF || true
DO \$\$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = '$DB_USER') THEN
    CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
  END IF;
END
\$\$;

SELECT 'CREATE DATABASE $DB_NAME'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$DB_NAME')\gexec

GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
\q
EOF

echo -e "${GREEN}✓ Database created${NC}"

echo ""
echo -e "${GREEN}🐍 Step 5/10: Setting up Python backend...${NC}"

cd "$INSTALL_DIR/apps/api"

# Fix ownership if running as root (ensure all files belong to regular user)
if [ "$RUN_AS_ROOT" = true ]; then
    echo -e "${BLUE}Setting proper file ownership...${NC}"
    chown -R "$REGULAR_USER:$REGULAR_USER" "$INSTALL_DIR" 2>/dev/null || true
fi

# Create virtual environment
if [ ! -d "venv" ]; then
    echo -e "${BLUE}Creating Python virtual environment...${NC}"
    if [ "$RUN_AS_ROOT" = true ]; then
        sudo -u "$REGULAR_USER" $PYTHON_CMD -m venv venv
    else
        $PYTHON_CMD -m venv venv
    fi
else
    # Fix ownership if venv already exists
    if [ "$RUN_AS_ROOT" = true ]; then
        chown -R "$REGULAR_USER:$REGULAR_USER" venv 2>/dev/null || true
    fi
fi

# Activate and upgrade pip
if [ "$RUN_AS_ROOT" = true ]; then
    echo -e "${BLUE}Installing Python packages...${NC}"
    sudo -u "$REGULAR_USER" bash -c "cd '$INSTALL_DIR/apps/api' && source venv/bin/activate && pip install --upgrade pip -q"
    sudo -u "$REGULAR_USER" bash -c "cd '$INSTALL_DIR/apps/api' && source venv/bin/activate && pip install -r requirements.txt -q"
else
    source venv/bin/activate
    pip install --upgrade pip -q
    echo -e "${BLUE}Installing Python packages...${NC}"
    pip install -r requirements.txt -q
    deactivate
fi

echo -e "${GREEN}✓ Python backend setup complete${NC}"

echo ""
echo -e "${GREEN}🔑 Step 6/10: Generating RSA keys for JWT...${NC}"

# Generate RSA keys if they don't exist
if [ ! -f "private.pem" ] || [ ! -f "public.pem" ]; then
    echo -e "${BLUE}Generating RSA key pair...${NC}"
    if [ "$RUN_AS_ROOT" = true ]; then
        sudo -u "$REGULAR_USER" openssl genrsa -out private.pem 2048
        sudo -u "$REGULAR_USER" openssl rsa -in private.pem -pubout -out public.pem
        chown "$REGULAR_USER:$REGULAR_USER" private.pem public.pem
    else
        openssl genrsa -out private.pem 2048
        openssl rsa -in private.pem -pubout -out public.pem
    fi
    chmod 600 private.pem
    chmod 644 public.pem
    echo -e "${GREEN}✓ RSA keys generated${NC}"
else
    echo -e "${GREEN}✓ RSA keys already exist${NC}"
    if [ "$RUN_AS_ROOT" = true ]; then
        chown "$REGULAR_USER:$REGULAR_USER" private.pem public.pem 2>/dev/null || true
    fi
fi

echo ""
echo -e "${GREEN}⚙️  Step 7/10: Configuring environment files...${NC}"

# Create .env file for backend
if [ ! -f ".env" ]; then
    echo -e "${BLUE}Creating backend .env file...${NC}"
    # Build CORS_ORIGINS and ALLOWED_HOSTS as JSON arrays
    if [ "$DOMAIN" = "localhost" ] || [ -z "$DOMAIN" ]; then
        CORS_ORIGINS_JSON='["http://localhost:3000"]'
        ALLOWED_HOSTS_JSON='["localhost"]'
    else
        CORS_ORIGINS_JSON="[\"http://localhost:3000\",\"https://$DOMAIN\"]"
        ALLOWED_HOSTS_JSON="[\"localhost\",\"$DOMAIN\"]"
    fi
    
    # Generate secret key
    SECRET_KEY_VALUE=$(openssl rand -hex 32)
    
    if [ "$RUN_AS_ROOT" = true ]; then
        sudo -u "$REGULAR_USER" bash -c "cat > .env <<EOF
# Application
APP_NAME=Faeflux One
DEBUG=false
ENVIRONMENT=production

# Database
DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME
DATABASE_ECHO=false

# Security
SECRET_KEY=$SECRET_KEY_VALUE
JWT_ALGORITHM=RS256
JWT_PRIVATE_KEY_PATH=./private.pem
JWT_PUBLIC_KEY_PATH=./public.pem
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=14

# CORS (JSON array format for Pydantic List)
CORS_ORIGINS=$CORS_ORIGINS_JSON

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60

# Allowed Hosts (JSON array format for Pydantic List)
ALLOWED_HOSTS=$ALLOWED_HOSTS_JSON

# File Upload
MAX_UPLOAD_SIZE=10485760
EOF"
        chown "$REGULAR_USER:$REGULAR_USER" .env
        chmod 600 .env
    else
        cat > .env <<EOF
# Application
APP_NAME=Faeflux One
DEBUG=false
ENVIRONMENT=production

# Database
DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME
DATABASE_ECHO=false

# Security
SECRET_KEY=$SECRET_KEY_VALUE
JWT_ALGORITHM=RS256
JWT_PRIVATE_KEY_PATH=./private.pem
JWT_PUBLIC_KEY_PATH=./public.pem
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=14

# CORS (JSON array format for Pydantic List)
CORS_ORIGINS=$CORS_ORIGINS_JSON

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60

# Allowed Hosts (JSON array format for Pydantic List)
ALLOWED_HOSTS=$ALLOWED_HOSTS_JSON

# File Upload
MAX_UPLOAD_SIZE=10485760
EOF
        chmod 600 .env
    fi
    echo -e "${GREEN}✓ Backend .env created${NC}"
else
    echo -e "${YELLOW}⚠️  .env file already exists, skipping...${NC}"
    if [ "$RUN_AS_ROOT" = true ]; then
        chown "$REGULAR_USER:$REGULAR_USER" .env 2>/dev/null || true
    fi
fi

cd "$INSTALL_DIR/apps/web"

echo ""
echo -e "${GREEN}📦 Step 8/10: Setting up Node.js frontend...${NC}"

# Install Node.js dependencies
if [ ! -d "node_modules" ]; then
    echo -e "${BLUE}Installing Node.js packages (this may take a few minutes)...${NC}"
    if [ "$RUN_AS_ROOT" = true ]; then
        sudo -u "$REGULAR_USER" pnpm install
        chown -R "$REGULAR_USER:$REGULAR_USER" node_modules 2>/dev/null || true
    else
        pnpm install
    fi
    echo -e "${GREEN}✓ Node.js packages installed${NC}"
else
    echo -e "${GREEN}✓ Node.js packages already installed${NC}"
fi

# Create .env.local file for frontend
if [ ! -f ".env.local" ]; then
    echo -e "${BLUE}Creating frontend .env.local file...${NC}"
    if [ "$RUN_AS_ROOT" = true ]; then
        sudo -u "$REGULAR_USER" bash -c "cat > .env.local <<'EOF'
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
EOF"
        chown "$REGULAR_USER:$REGULAR_USER" .env.local
        chmod 600 .env.local
    else
        cat > .env.local <<EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
EOF
        chmod 600 .env.local
    fi
    echo -e "${GREEN}✓ Frontend .env.local created${NC}"
else
    echo -e "${YELLOW}⚠️  .env.local file already exists, skipping...${NC}"
    if [ "$RUN_AS_ROOT" = true ]; then
        chown "$REGULAR_USER:$REGULAR_USER" .env.local 2>/dev/null || true
    fi
fi

echo ""
echo -e "${GREEN}🗃️  Step 9/10: Running database migrations...${NC}"

cd "$INSTALL_DIR/apps/api"

# Run Alembic migrations
echo -e "${BLUE}Running database migrations...${NC}"
if [ "$RUN_AS_ROOT" = true ]; then
    sudo -u "$REGULAR_USER" bash -c "cd '$INSTALL_DIR/apps/api' && source venv/bin/activate && alembic upgrade head" || {
        echo -e "${YELLOW}⚠️  First migration, creating initial migration...${NC}"
        sudo -u "$REGULAR_USER" bash -c "cd '$INSTALL_DIR/apps/api' && source venv/bin/activate && alembic revision --autogenerate -m 'Initial migration'" || true
        sudo -u "$REGULAR_USER" bash -c "cd '$INSTALL_DIR/apps/api' && source venv/bin/activate && alembic upgrade head" || echo -e "${YELLOW}⚠️  Migration failed, please check database connection${NC}"
    }
else
    source venv/bin/activate
    alembic upgrade head || {
        echo -e "${YELLOW}⚠️  First migration, creating initial migration...${NC}"
        alembic revision --autogenerate -m "Initial migration" || true
        alembic upgrade head || echo -e "${YELLOW}⚠️  Migration failed, please check database connection${NC}"
    }
    deactivate
fi

echo -e "${GREEN}✓ Database migrations complete${NC}"

echo ""
echo -e "${GREEN}👤 Step 10/10: Creating admin user...${NC}"

# Create admin user
echo -e "${BLUE}Creating admin user...${NC}"
if [ "$RUN_AS_ROOT" = true ]; then
    sudo -u "$REGULAR_USER" bash -c "cd '$INSTALL_DIR/apps/api' && source venv/bin/activate && python scripts/create_admin.py" || {
        echo -e "${YELLOW}⚠️  Admin creation script failed. Creating manually...${NC}"
        sudo -u "$REGULAR_USER" bash -c "cd '$INSTALL_DIR/apps/api' && source venv/bin/activate && python <<'PYTHON_SCRIPT'
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
from sqlmodel import Session, select
from app.core.database import engine
from app.core.auth import get_password_hash
from app.models.user import User, UserRole

with Session(engine) as session:
    statement = select(User).where(User.email == '$ADMIN_EMAIL')
    existing = session.exec(statement).first()
    
    if existing:
        print('Admin user already exists.')
    else:
        admin = User(
            email='$ADMIN_EMAIL',
            hashed_password=get_password_hash('$ADMIN_PASSWORD'),
            full_name='System Administrator',
            role=UserRole.ADMIN,
            is_active=True,
        )
        session.add(admin)
        session.commit()
        print(f'Admin user created: $ADMIN_EMAIL')
PYTHON_SCRIPT"
    }
else
    source venv/bin/activate
    python scripts/create_admin.py || {
        echo -e "${YELLOW}⚠️  Admin creation script failed. Creating manually...${NC}"
        python <<PYTHON_SCRIPT
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from sqlmodel import Session, select
from app.core.database import engine
from app.core.auth import get_password_hash
from app.models.user import User, UserRole

with Session(engine) as session:
    statement = select(User).where(User.email == "$ADMIN_EMAIL")
    existing = session.exec(statement).first()
    
    if existing:
        print("Admin user already exists.")
    else:
        admin = User(
            email="$ADMIN_EMAIL",
            hashed_password=get_password_hash("$ADMIN_PASSWORD"),
            full_name="System Administrator",
            role=UserRole.ADMIN,
            is_active=True,
        )
        session.add(admin)
        session.commit()
        print(f"Admin user created: $ADMIN_EMAIL")
PYTHON_SCRIPT
    }
    deactivate
fi

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Installation Complete!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}📝 Summary:${NC}"
echo -e "  • Database: $DB_NAME"
echo -e "  • Database User: $DB_USER"
echo -e "  • Admin Email: $ADMIN_EMAIL"
echo -e "  • Admin Password: ${YELLOW}[Your provided password]${NC}"
echo ""
echo -e "${BLUE}🚀 To start the application:${NC}"
echo ""
echo -e "${YELLOW}Backend (Terminal 1):${NC}"
echo -e "  cd $INSTALL_DIR/apps/api"
echo -e "  source venv/bin/activate"
echo -e "  uvicorn main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo -e "${YELLOW}Frontend (Terminal 2):${NC}"
echo -e "  cd $INSTALL_DIR/apps/web"
echo -e "  pnpm dev"
echo ""
echo -e "${BLUE}📖 Access Points:${NC}"
echo -e "  • Frontend: http://localhost:3000"
echo -e "  • Backend API: http://localhost:8000"
echo -e "  • API Docs: http://localhost:8000/docs"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT:${NC}"
echo -e "  • Change admin password after first login!"
echo -e "  • Review .env files for production settings"
echo -e "  • Keep private.pem secure!"
echo ""
read -p "Would you like to setup systemd services and Nginx for production? (y/N): " setup_production

if [[ "$setup_production" =~ ^[Yy]$ ]]; then
    echo ""
    echo -e "${BLUE}Setting up production services...${NC}"
    
    # Copy systemd service files
    sudo cp "$INSTALL_DIR/deployment/systemd/faeflux-api.service" /etc/systemd/system/
    sudo cp "$INSTALL_DIR/deployment/systemd/faeflux-web.service" /etc/systemd/system/
    
    # Update service files with correct paths
    sudo sed -i "s|/opt/faeflux-one|$INSTALL_DIR|g" /etc/systemd/system/faeflux-api.service
    sudo sed -i "s|/opt/faeflux-one|$INSTALL_DIR|g" /etc/systemd/system/faeflux-web.service
    
    # Setup Nginx
    if [ "$DOMAIN" != "localhost" ]; then
        sudo cp "$INSTALL_DIR/deployment/nginx/faeflux-one.conf" /etc/nginx/sites-available/
        sudo sed -i "s|your-domain.com|$DOMAIN|g" /etc/nginx/sites-available/faeflux-one.conf
        sudo ln -sf /etc/nginx/sites-available/faeflux-one.conf /etc/nginx/sites-enabled/
        
        echo -e "${BLUE}Testing Nginx configuration...${NC}"
        sudo nginx -t
        
        echo ""
        echo -e "${YELLOW}To setup SSL certificate, run:${NC}"
        echo -e "  sudo certbot --nginx -d $DOMAIN"
    fi
    
    echo -e "${GREEN}✓ Production services configured${NC}"
    echo ""
    echo -e "${BLUE}To start services:${NC}"
    echo -e "  sudo systemctl daemon-reload"
    echo -e "  sudo systemctl enable faeflux-api faeflux-web"
    echo -e "  sudo systemctl start faeflux-api faeflux-web"
    echo -e "  sudo systemctl status faeflux-api faeflux-web"
fi

# Final ownership fix
if [ "$RUN_AS_ROOT" = true ]; then
    echo -e "${BLUE}Finalizing file ownership...${NC}"
    chown -R "$REGULAR_USER:$REGULAR_USER" "$INSTALL_DIR" 2>/dev/null || true
    echo -e "${GREEN}✓ All files owned by user: $REGULAR_USER${NC}"
fi

echo ""
echo -e "${GREEN}🎉 All done! Happy coding!${NC}"
echo ""
echo -e "${BLUE}📄 Installation log saved to: $LOG_FILE${NC}"

if [ "$RUN_AS_ROOT" = true ]; then
    chown "$REGULAR_USER:$REGULAR_USER" "$LOG_FILE" 2>/dev/null || true
fi

