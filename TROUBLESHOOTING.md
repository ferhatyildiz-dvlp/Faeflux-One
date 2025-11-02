# Troubleshooting Guide

## Installation Issues

### Issue: pnpm Installation Permission Error

**Error:**
```
npm error code EACCES
npm error syscall mkdir
npm error path /usr/lib/node_modules/pnpm
npm error Error: EACCES: permission denied
```

**Solution:**

The install script has been updated to use `sudo npm install -g pnpm`. If you're running an older version, manually install pnpm:

```bash
# Option 1: Using sudo (recommended)
sudo npm install -g pnpm

# Option 2: Using pnpm installer
curl -fsSL https://get.pnpm.io/install.sh | sh -
source ~/.bashrc  # or ~/.zshrc

# Option 3: Using corepack (Node.js 16.10+)
sudo corepack enable
corepack prepare pnpm@latest --activate
```

### Issue: Database Connection Failed

**Error:** `ERROR: Could not open requirements file`

**Solution:**

Make sure you're in the correct directory:
```bash
cd ~/Faeflux-One/apps/api
```

Then check if files exist:
```bash
ls -la requirements.txt
ls -la .env.example
```

### Issue: psycopg2 Build Failed

**Error:**
```
fatal error: pg_config.h: No such file or directory
```

**Solution:**

Install PostgreSQL development headers:
```bash
sudo apt-get install -y postgresql-dev libpq-dev
# or for PostgreSQL 16
sudo apt-get install -y postgresql-server-dev-16
```

Then retry:
```bash
cd apps/api
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: Alembic Command Not Found

**Error:** `Command 'alembic' not found`

**Solution:**

Alembic should be installed via requirements.txt. If not:
```bash
cd apps/api
source venv/bin/activate
pip install alembic
```

Then run migrations:
```bash
alembic upgrade head
```

### Issue: Missing RSA Keys

**Error:** JWT authentication fails, keys not found

**Solution:**

Generate RSA keys:
```bash
cd apps/api
openssl genrsa -out private.pem 2048
openssl rsa -in private.pem -pubout -out public.pem
chmod 600 private.pem
chmod 644 public.pem
```

### Issue: Script Won't Run as Root

**Error:** `Please do NOT run this script as root/sudo`

**Solution:**

Run as regular user. The script will ask for sudo when needed:
```bash
# Don't do this:
sudo ./install.sh

# Do this:
./install.sh
```

## Runtime Issues

### Issue: Backend Won't Start

**Check:**
1. Virtual environment is activated: `source venv/bin/activate`
2. .env file exists and is configured
3. Database is running: `sudo systemctl status postgresql`
4. Port 8000 is available: `sudo lsof -i :8000`

**Debug:**
```bash
cd apps/api
source venv/bin/activate
python -c "from app.core.config import settings; print(settings.DATABASE_URL)"
uvicorn main:app --reload --log-level debug
```

### Issue: Frontend Won't Start

**Check:**
1. Node modules installed: `ls node_modules`
2. .env.local exists
3. Port 3000 is available: `sudo lsof -i :3000`

**Debug:**
```bash
cd apps/web
pnpm install
pnpm dev
```

### Issue: Database Migration Errors

**Solution:**

Reset migrations (WARNING: Only in development, will lose data):
```bash
cd apps/api
source venv/bin/activate
alembic downgrade base
alembic upgrade head
```

Or create fresh migration:
```bash
alembic revision --autogenerate -m "Fix migrations"
alembic upgrade head
```

## Log Files

Installation logs are automatically saved to:
```
~/faeflux_install_YYYYMMDD_HHMMSS.log
```

To view recent logs:
```bash
ls -lt ~/faeflux_install_*.log | head -1 | xargs cat
```

## Getting Help

1. Check installation log file
2. Verify all prerequisites are installed
3. Check service status (production):
   ```bash
   sudo systemctl status faeflux-api
   sudo systemctl status faeflux-web
   sudo journalctl -u faeflux-api -n 50
   ```
4. Review error messages carefully
5. Check GitHub issues: https://github.com/ferhatyildiz-dvlp/Faeflux-One/issues

