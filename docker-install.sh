#!/bin/bash

# Faeflux One - Docker Installation Script
# This script sets up Faeflux One using Docker Compose

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║      Faeflux One - Docker Installation Script       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo -e "${YELLOW}Installing Docker...${NC}"
    
    if grep -q "Ubuntu" /etc/os-release 2>/dev/null; then
        sudo apt-get update
        sudo apt-get install -y docker.io docker-compose
        sudo systemctl start docker
        sudo systemctl enable docker
        sudo usermod -aG docker $USER
        echo -e "${GREEN}✓ Docker installed. Please log out and log back in, or run: newgrp docker${NC}"
    else
        echo -e "${RED}Please install Docker manually from https://docs.docker.com/get-docker/${NC}"
        exit 1
    fi
fi

# Check if Docker Compose is available
if ! docker compose version &> /dev/null && ! docker-compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker found: $(docker --version)${NC}"

# Check if user is in docker group
if ! groups | grep -q docker; then
    echo -e "${YELLOW}⚠️  You are not in the docker group${NC}"
    echo -e "${BLUE}Adding you to docker group...${NC}"
    sudo usermod -aG docker $USER
    echo -e "${YELLOW}Please log out and log back in, or run: newgrp docker${NC}"
    echo -e "${YELLOW}Then run this script again.${NC}"
    exit 0
fi

# Get script directory
INSTALL_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "$INSTALL_DIR"

echo ""
echo -e "${GREEN}📋 Step 1/5: Collecting configuration...${NC}"

# Ask for database password
read -sp "Enter PostgreSQL password (default: changeme_in_production): " DB_PASSWORD
DB_PASSWORD=${DB_PASSWORD:-changeme_in_production}
echo ""

# Ask for admin credentials
read -p "Enter admin email (default: admin@faeflux.local): " ADMIN_EMAIL
ADMIN_EMAIL=${ADMIN_EMAIL:-admin@faeflux.local}

read -sp "Enter admin password (min 8 chars, default: Admin@123!): " ADMIN_PASSWORD
ADMIN_PASSWORD=${ADMIN_PASSWORD:-Admin@123!}
echo ""

if [ ${#ADMIN_PASSWORD} -lt 8 ]; then
    echo -e "${YELLOW}⚠️  Password too short, using default${NC}"
    ADMIN_PASSWORD="Admin@123!"
fi

echo ""
echo -e "${GREEN}🔑 Step 2/5: Generating RSA keys...${NC}"

# Generate RSA keys if they don't exist
if [ ! -f "apps/api/private.pem" ] || [ ! -f "apps/api/public.pem" ]; then
    echo -e "${BLUE}Generating RSA key pair...${NC}"
    openssl genrsa -out apps/api/private.pem 2048
    openssl rsa -in apps/api/private.pem -pubout -out apps/api/public.pem
    chmod 600 apps/api/private.pem
    chmod 644 apps/api/public.pem
    echo -e "${GREEN}✓ RSA keys generated${NC}"
else
    echo -e "${GREEN}✓ RSA keys already exist${NC}"
fi

echo ""
echo -e "${GREEN}⚙️  Step 3/5: Creating environment file...${NC}"

# Generate secret key
SECRET_KEY=$(openssl rand -hex 32)

# Create .env.docker file
cat > .env.docker <<EOF
# Database
DB_PASSWORD=$DB_PASSWORD

# Security
SECRET_KEY=$SECRET_KEY

# API URLs
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000

# CORS (JSON array format)
CORS_ORIGINS=["http://localhost:3000"]

# Allowed Hosts (JSON array format)
ALLOWED_HOSTS=["localhost"]

# Debug
DEBUG=false
ENVIRONMENT=production
EOF

chmod 600 .env.docker
echo -e "${GREEN}✓ Environment file created${NC}"

# Set admin credentials for create_admin.py
export ADMIN_EMAIL
export ADMIN_PASSWORD

echo ""
echo -e "${GREEN}🐳 Step 4/5: Building Docker images...${NC}"

# Load environment variables
export $(grep -v '^#' .env.docker | xargs)

# Build images
docker-compose build || docker compose build

echo ""
echo -e "${GREEN}🚀 Step 5/5: Starting containers...${NC}"

# Start containers
docker-compose up -d || docker compose up -d

echo ""
echo -e "${GREEN}⏳ Waiting for services to be ready...${NC}"
sleep 10

# Wait for PostgreSQL to be ready
echo -e "${BLUE}Waiting for PostgreSQL...${NC}"
timeout=60
while ! docker-compose exec -T postgres pg_isready -U faeflux > /dev/null 2>&1; do
    sleep 2
    timeout=$((timeout - 2))
    if [ $timeout -le 0 ]; then
        echo -e "${RED}❌ PostgreSQL failed to start${NC}"
        docker-compose logs postgres
        exit 1
    fi
done
echo -e "${GREEN}✓ PostgreSQL is ready${NC}"

# Run migrations and create admin
echo -e "${BLUE}Running database migrations...${NC}"
docker-compose exec -T api alembic upgrade head || {
    echo -e "${YELLOW}⚠️  Creating initial migration...${NC}"
    docker-compose exec -T api alembic revision --autogenerate -m "Initial migration" || true
    docker-compose exec -T api alembic upgrade head
}

echo -e "${BLUE}Creating admin user...${NC}"
docker-compose exec -T api python scripts/create_admin.py || {
    echo -e "${YELLOW}⚠️  Admin creation failed, will be created on next container restart${NC}"
}

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Installation Complete!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}📊 Service Status:${NC}"
docker-compose ps || docker compose ps

echo ""
echo -e "${GREEN}🌐 Access URLs:${NC}"
echo -e "  Frontend:   ${BLUE}http://localhost:3000${NC}"
echo -e "  Backend:    ${BLUE}http://localhost:8000${NC}"
echo -e "  API Docs:   ${BLUE}http://localhost:8000/docs${NC}"
echo ""
echo -e "${GREEN}👤 Admin Login:${NC}"
echo -e "  Email:    ${BLUE}$ADMIN_EMAIL${NC}"
echo -e "  Password: ${BLUE}${ADMIN_PASSWORD}${NC}"
echo ""
echo -e "${YELLOW}📝 Useful Commands:${NC}"
echo -e "  View logs:       ${BLUE}docker-compose logs -f${NC}"
echo -e "  Stop services:   ${BLUE}docker-compose stop${NC}"
echo -e "  Start services:  ${BLUE}docker-compose start${NC}"
echo -e "  Restart:         ${BLUE}docker-compose restart${NC}"
echo -e "  Remove all:      ${BLUE}docker-compose down -v${NC}"
echo ""

