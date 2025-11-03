#!/bin/bash
# Faeflux One - Production Setup Script
# Run as root or with sudo

set -e

echo "🚀 Faeflux One Production Setup"
echo "================================"

# Variables
INSTALL_DIR="/opt/faeflux-one"
APP_USER="www-data"
DOMAIN="${1:-your-domain.com}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run as root or with sudo"
    exit 1
fi

echo "📦 Installing system dependencies..."
apt-get update
apt-get install -y \
    python3.12 \
    python3.12-venv \
    python3-pip \
    postgresql-16 \
    postgresql-contrib \
    nginx \
    certbot \
    python3-certbot-nginx \
    curl \
    git \
    build-essential \
    nodejs \
    npm

# Install pnpm
npm install -g pnpm

echo "👤 Creating application user..."
if ! id "$APP_USER" &>/dev/null; then
    useradd -r -s /bin/bash -d "$INSTALL_DIR" "$APP_USER" || true
fi

echo "📁 Setting up directory structure..."
mkdir -p "$INSTALL_DIR"
chown "$APP_USER:$APP_USER" "$INSTALL_DIR"

echo "🐘 Setting up PostgreSQL..."
# Create database and user
sudo -u postgres psql <<EOF || true
CREATE USER faeflux WITH PASSWORD 'changeme_in_production';
CREATE DATABASE faeflux_one;
GRANT ALL PRIVILEGES ON DATABASE faeflux_one TO faeflux;
\q
EOF

echo "✅ Basic setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Copy your application code to $INSTALL_DIR"
echo "2. Setup Python virtual environment in $INSTALL_DIR/apps/api/venv"
echo "3. Install dependencies (pip install -r requirements.txt)"
echo "4. Generate RSA keys for JWT (openssl genrsa -out private.pem 2048)"
echo "5. Configure .env files"
echo "6. Run database migrations (alembic upgrade head)"
echo "7. Create admin user (python scripts/create_admin.py)"
echo "8. Install systemd services"
echo "9. Configure Nginx with domain: $DOMAIN"
echo "10. Setup SSL with Certbot"


