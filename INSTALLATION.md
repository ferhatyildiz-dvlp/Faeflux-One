# Faeflux One - Installation Guide

## Automated Installation

The easiest way to install Faeflux One is using the provided installation script.

### Prerequisites

- Ubuntu 22.04 or later (or compatible Linux distribution)
- Internet connection
- Sudo/root access for system package installation

### Running the Installation Script

1. **Navigate to the project directory:**
   ```bash
   cd faeflux-one
   ```

2. **Make the script executable:**
   ```bash
   chmod +x install.sh
   ```

3. **Run the installation script:**
   ```bash
   ./install.sh
   ```

### What the Script Does

The installation script is interactive and will guide you through:

1. **Prerequisites Check** - Verifies Python, Node.js, and other dependencies
2. **Configuration** - Asks for:
   - Database password
   - Admin email
   - Admin password
   - Domain name (optional, for production)
3. **System Dependencies** - Installs:
   - Python 3.12 (or 3.x)
   - PostgreSQL 16
   - Node.js 20+
   - pnpm
   - Nginx
   - Certbot
   - Build tools
4. **Database Setup** - Creates PostgreSQL database and user
5. **Backend Setup** - Sets up Python virtual environment and installs dependencies
6. **RSA Key Generation** - Creates JWT signing keys
7. **Environment Configuration** - Creates `.env` and `.env.local` files
8. **Database Migrations** - Runs Alembic migrations
9. **Admin User Creation** - Creates initial admin user
10. **Production Setup** (Optional) - Configures systemd services and Nginx

### Installation Prompts

During installation, you'll be asked for:

#### Database Password
- Required: Yes
- Used for: PostgreSQL database user authentication
- Security: Choose a strong password

#### Admin Email
- Required: Yes
- Default: `admin@faeflux.local`
- Used for: Initial admin account login

#### Admin Password
- Required: Yes
- Minimum: 8 characters
- Default: `Admin@123!` (if not provided)
- Security: **Change immediately after first login!**

#### Domain Name
- Required: No
- Default: `localhost`
- Used for: Production deployment and CORS configuration

### Post-Installation

After installation completes:

1. **Change Admin Password**
   - Log in with the credentials you provided
   - Navigate to user settings
   - Change password immediately

2. **Review Configuration**
   - Check `.env` files in both `apps/api` and `apps/web`
   - Verify database connection
   - Review security settings

3. **Start Development**
   ```bash
   ./dev-start.sh
   ```

   Or manually:
   ```bash
   # Terminal 1 - Backend
   cd apps/api
   source venv/bin/activate
   uvicorn main:app --reload

   # Terminal 2 - Frontend
   cd apps/web
   pnpm dev
   ```

## Manual Installation

If you prefer manual installation or need custom configuration, see the main [README.md](./README.md) for step-by-step instructions.

## Troubleshooting

### Installation Fails at Database Step

**Problem:** Cannot create database or user.

**Solution:**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Manually create database
sudo -u postgres psql
CREATE USER faeflux WITH PASSWORD 'your_password';
CREATE DATABASE faeflux_one;
GRANT ALL PRIVILEGES ON DATABASE faeflux_one TO faeflux;
\q
```

### Python Virtual Environment Issues

**Problem:** venv creation fails or packages won't install.

**Solution:**
```bash
cd apps/api
rm -rf venv
python3.12 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Node.js Dependencies Issues

**Problem:** pnpm install fails.

**Solution:**
```bash
cd apps/web
rm -rf node_modules
npm install -g pnpm
pnpm install
```

### RSA Keys Missing

**Problem:** JWT authentication fails with key errors.

**Solution:**
```bash
cd apps/api
openssl genrsa -out private.pem 2048
openssl rsa -in private.pem -pubout -out public.pem
chmod 600 private.pem
chmod 644 public.pem
```

### Database Migration Errors

**Problem:** Alembic migrations fail.

**Solution:**
```bash
cd apps/api
source venv/bin/activate

# Check database connection
python -c "from app.core.config import settings; print(settings.DATABASE_URL)"

# Reset migrations (WARNING: Only in development!)
# rm -rf alembic/versions/*
# alembic revision --autogenerate -m "Initial migration"
# alembic upgrade head
```

## Production Deployment

For production deployment, the script offers to setup:

- **Systemd Services** - For automatic startup
- **Nginx Configuration** - For reverse proxy
- **SSL/TLS Certificates** - Via Certbot

After installation, if you selected production setup:

1. **Edit systemd service files** (if paths differ):
   ```bash
   sudo nano /etc/systemd/system/faeflux-api.service
   sudo nano /etc/systemd/system/faeflux-web.service
   ```

2. **Enable and start services:**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable faeflux-api faeflux-web
   sudo systemctl start faeflux-api faeflux-web
   ```

3. **Setup SSL Certificate:**
   ```bash
   sudo certbot --nginx -d your-domain.com
   ```

## Security Checklist

After installation:

- [ ] Changed default admin password
- [ ] Reviewed `.env` files (remove from version control)
- [ ] Secured `private.pem` file (chmod 600)
- [ ] Configured firewall (ufw)
- [ ] Updated CORS_ORIGINS in production
- [ ] Changed SECRET_KEY in production
- [ ] Setup SSL/TLS in production
- [ ] Reviewed file permissions
- [ ] Enabled audit logging monitoring

## Support

For issues or questions:
1. Check the main [README.md](./README.md)
2. Review logs: `journalctl -u faeflux-api -u faeflux-web`
3. Check GitHub issues: [https://github.com/ferhatyildiz-dvlp/Faeflux-One](https://github.com/ferhatyildiz-dvlp/Faeflux-One)

