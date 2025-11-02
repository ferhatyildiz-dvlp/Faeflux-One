# Faeflux One - IT Operations & Asset Management System

Enterprise-grade IT Operations and Asset Management platform built with FastAPI (Python 3.12) and Next.js 15.

## 🏗️ Architecture

- **Backend**: FastAPI + SQLModel + PostgreSQL 16
- **Frontend**: Next.js 15 + TypeScript + TailwindCSS
- **Deployment**: Ubuntu 22.04+ (Native, no Docker)
- **Security**: JWT (RS256), RBAC, CORS, CSRF, Rate Limiting, HSTS, CSP, Audit Logging

## 📋 Prerequisites

- Ubuntu 22.04 or later
- Python 3.12+
- Node.js 20+ and pnpm
- PostgreSQL 16+
- Nginx
- Certbot (for TLS)

## 🚀 Quick Start

### Download and Install on Ubuntu

**New to Faeflux One?** Start here: **[DOWNLOAD_AND_INSTALL.md](./DOWNLOAD_AND_INSTALL.md)**

Quick commands:
```bash
# Clone the repository
git clone https://github.com/ferhatyildiz-dvlp/Faeflux-One.git
cd Faeflux-One

# Run automated installation
chmod +x install.sh
./install.sh
```

### Automated Installation (Recommended)

Run the interactive installation script:

```bash
./install.sh
```

The script will:
- ✅ Check prerequisites
- ✅ Install all system dependencies
- ✅ Setup PostgreSQL database
- ✅ Configure Python backend
- ✅ Setup Node.js frontend
- ✅ Generate RSA keys for JWT
- ✅ Create environment files
- ✅ Run database migrations
- ✅ Create admin user
- ✅ Optionally setup systemd services and Nginx

You'll be prompted for:
- Database password
- Admin email and password
- Domain name (optional)
- Production setup preferences

### Manual Installation

If you prefer manual setup, follow these steps:

#### 1. System Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.12 python3.12-venv python3-pip postgresql-16 postgresql-contrib nginx certbot python3-certbot-nginx curl git build-essential

# Install Node.js 20+ and pnpm
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
npm install -g pnpm
```

### 2. Database Setup

```bash
# Create PostgreSQL user and database
sudo -u postgres psql <<EOF
CREATE USER faeflux WITH PASSWORD 'changeme_in_production';
CREATE DATABASE faeflux_one;
GRANT ALL PRIVILEGES ON DATABASE faeflux_one TO faeflux;
\q
EOF
```

### 3. Backend Setup

```bash
cd faeflux-one/apps/api

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your database credentials and secrets

# Generate RSA key pair for JWT
openssl genrsa -out private.pem 2048
openssl rsa -in private.pem -pubout -out public.pem
chmod 600 private.pem
chmod 644 public.pem

# Run migrations
alembic upgrade head

# Create initial admin user
python scripts/create_admin.py
```

### 4. Frontend Setup

```bash
cd faeflux-one/apps/web

# Install dependencies
pnpm install

# Copy environment file
cp .env.example .env.local
# Edit .env.local with your API URL
```

### 5. Development Mode

#### Option A: Quick Start Script (Recommended)
```bash
./dev-start.sh
```

This starts both backend and frontend servers automatically.

#### Option B: Manual Start

**Terminal 1 - Backend:**
```bash
cd apps/api
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd apps/web
pnpm dev
```

**Access Points:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### 6. Production Deployment

#### Systemd Service Setup

```bash
# Copy systemd service files
sudo cp deployment/systemd/faeflux-api.service /etc/systemd/system/
sudo cp deployment/systemd/faeflux-web.service /etc/systemd/system/

# Edit service files with correct paths
sudo nano /etc/systemd/system/faeflux-api.service
sudo nano /etc/systemd/system/faeflux-web.service

# Reload and start services
sudo systemctl daemon-reload
sudo systemctl enable faeflux-api faeflux-web
sudo systemctl start faeflux-api faeflux-web
```

#### Nginx Configuration

```bash
# Copy Nginx configuration
sudo cp deployment/nginx/faeflux-one.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/faeflux-one.conf /etc/nginx/sites-enabled/

# Test and reload Nginx
sudo nginx -t
sudo systemctl reload nginx
```

#### TLS/HTTPS Setup

```bash
# Obtain SSL certificate (replace with your domain)
sudo certbot --nginx -d your-domain.com

# Auto-renewal is set up automatically
sudo certbot renew --dry-run
```

## 🔐 Security Configuration

### Environment Variables

Create `.env` files in both `apps/api` and `apps/web`:

**apps/api/.env:**
```env
DATABASE_URL=postgresql://faeflux:your_password@localhost:5432/faeflux_one
SECRET_KEY=your-very-secret-key-change-in-production
JWT_ALGORITHM=RS256
JWT_PRIVATE_KEY_PATH=./private.pem
JWT_PUBLIC_KEY_PATH=./public.pem
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=14
CORS_ORIGINS=http://localhost:3000,https://your-domain.com
RATE_LIMIT_PER_MINUTE=60
ALLOWED_HOSTS=localhost,your-domain.com
```

**apps/web/.env.local:**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

### File Permissions

```bash
# Secure private keys
chmod 600 apps/api/private.pem
chmod 644 apps/api/public.pem

# Secure environment files
chmod 600 apps/api/.env
chmod 600 apps/web/.env.local
```

### Firewall Configuration

```bash
# Allow HTTP, HTTPS, and SSH only
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

## 📁 Project Structure

```
faeflux-one/
├── apps/
│   ├── api/              # FastAPI backend
│   │   ├── app/
│   │   │   ├── core/     # Security, config, middleware
│   │   │   ├── models/   # SQLModel models
│   │   │   ├── schemas/  # Pydantic schemas
│   │   │   ├── api/      # API routes
│   │   │   ├── services/ # Business logic
│   │   │   └── utils/    # Utilities
│   │   ├── alembic/      # Database migrations
│   │   ├── scripts/      # Utility scripts
│   │   └── main.py       # FastAPI app entry
│   └── web/              # Next.js frontend
│       ├── app/          # Next.js app router
│       ├── components/   # React components
│       ├── locales/      # i18n translations
│       └── lib/          # Utilities
├── deployment/
│   ├── systemd/          # Systemd service files
│   └── nginx/            # Nginx configurations
└── README.md
```

## 🔑 Default Admin Credentials

After running `create_admin.py`, default credentials:
- **Email**: admin@faeflux.local
- **Password**: Admin@123! (change immediately)

## 📊 API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - Logout

### Assets
- `GET /api/v1/assets` - List assets
- `POST /api/v1/assets` - Create asset
- `GET /api/v1/assets/{id}` - Get asset
- `PUT /api/v1/assets/{id}` - Update asset
- `DELETE /api/v1/assets/{id}` - Delete asset

### Tickets
- `GET /api/v1/tickets` - List tickets
- `POST /api/v1/tickets` - Create ticket
- `GET /api/v1/tickets/{id}` - Get ticket
- `PUT /api/v1/tickets/{id}` - Update ticket

### Users
- `GET /api/v1/users` - List users
- `POST /api/v1/users` - Create user
- `GET /api/v1/users/{id}` - Get user
- `PUT /api/v1/users/{id}` - Update user

### Sites
- `GET /api/v1/sites` - List sites
- `POST /api/v1/sites` - Create site
- `GET /api/v1/sites/{id}` - Get site
- `PUT /api/v1/sites/{id}` - Update site

### Agents
- `POST /api/v1/agents/heartbeat` - Agent heartbeat
- `POST /api/v1/agents/inventory` - Submit inventory

### System
- `GET /health` - Health check
- `GET /metrics` - Metrics endpoint

## 🌍 Internationalization

Default language: **Turkish** (tr)
Available languages: Turkish (tr), English (en)

Translation files located in `apps/web/locales/`

## 🛠️ Development Commands

### Backend
```bash
cd apps/api
source venv/bin/activate

# Run migrations
alembic revision --autogenerate -m "description"
alembic upgrade head

# Run tests
pytest

# Format code
black .
isort .
```

### Frontend
```bash
cd apps/web

# Start dev server
pnpm dev

# Build for production
pnpm build

# Start production server
pnpm start

# Lint
pnpm lint

# Format
pnpm format
```

## 📝 License

Proprietary - All rights reserved

## 🔒 Security Notes

1. **Never commit** `.env` files or private keys to version control
2. **Rotate** JWT keys regularly in production
3. **Use strong passwords** for database and admin accounts
4. **Enable** firewall and limit access to necessary ports
5. **Monitor** audit logs regularly
6. **Keep** system and dependencies updated
7. **Use** HTTPS in production (mandatory)
8. **Review** file permissions regularly

## 📞 Support

For issues or questions, please contact the development team.

---

**Version**: 1.0.0  
**Last Updated**: 2024

