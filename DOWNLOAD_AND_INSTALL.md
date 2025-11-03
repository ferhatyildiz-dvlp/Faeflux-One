# Faeflux One - Download and Install Guide for Ubuntu

This guide will walk you through downloading and installing Faeflux One on Ubuntu 22.04 or later.

## 📋 Prerequisites

Before starting, ensure you have:
- Ubuntu 22.04 or later
- Internet connection
- User account with sudo privileges
- At least 2GB free disk space

## 🚀 Step-by-Step Installation

### Step 1: Open Terminal

Press `Ctrl + Alt + T` or search for "Terminal" in the Applications menu.

### Step 2: Update System Packages

```bash
sudo apt update && sudo apt upgrade -y
```

### Step 3: Install Git (if not already installed)

```bash
sudo apt install -y git
```

Verify installation:
```bash
git --version
```

### Step 4: Download Faeflux One

You have two options:

#### Option A: Clone from GitHub (Recommended)

```bash
# Navigate to your desired directory (e.g., home directory)
cd ~

# Clone the repository
git clone https://github.com/ferhatyildiz-dvlp/Faeflux-One.git

# Navigate into the project directory
cd Faeflux-One
```

#### Option B: Download ZIP File

1. Visit: https://github.com/ferhatyildiz-dvlp/Faeflux-One
2. Click the green "Code" button
3. Select "Download ZIP"
4. Extract the ZIP file to your desired location
5. Open terminal in the extracted folder

```bash
# Navigate to the extracted folder
cd ~/Downloads/Faeflux-One-main  # Adjust path based on your download location
```

### Step 5: Make Installation Script Executable

```bash
chmod +x install.sh
```

### Step 6: Run the Installation Script

```bash
./install.sh
```

### Step 7: Follow the Interactive Prompts

The script will ask you for the following information:

#### 1. Domain Name
```
Enter your domain (leave empty for local development) [localhost]: 
```
- **For local development:** Press Enter (uses `localhost`)
- **For production:** Enter your domain name (e.g., `faeflux.example.com`)

#### 2. Database Password
```
Enter PostgreSQL password for database user 'faeflux': 
```
- Enter a **strong password** for the database
- The password will be hidden as you type
- **Save this password** - you'll need it for database access

#### 3. Admin Email
```
Enter admin email [admin@faeflux.local]: 
```
- Press Enter to use default, or enter a custom email
- This will be your admin login email

#### 4. Admin Password
```
Enter admin password (min 8 chars): 
```
- Enter a **strong password** (minimum 8 characters)
- The password will be hidden as you type
- **Save this password** - you'll need it to log in

#### 5. Production Setup (Optional)
```
Would you like to setup systemd services and Nginx for production? (y/N): 
```
- Type `y` for production deployment
- Type `N` or press Enter for development only

### Step 8: Wait for Installation

The script will automatically:
- ✅ Install system dependencies (Python, PostgreSQL, Node.js, etc.)
- ✅ Set up the database
- ✅ Install Python packages
- ✅ Generate security keys
- ✅ Configure environment files
- ✅ Run database migrations
- ✅ Create admin user

**This may take 5-15 minutes** depending on your internet speed.

### Step 9: Installation Complete!

You'll see a success message with:
- Database information
- Admin credentials
- Instructions to start the application

## 🎯 Starting the Application

### For Development (Quick Start)

```bash
# From the project root directory
./dev-start.sh
```

This starts both backend and frontend servers.

### For Development (Manual)

Open **two terminal windows**:

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

### Access the Application

Once started, open your web browser:

- **Frontend (Web Interface):** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

## 🔐 First Login

1. Go to http://localhost:3000
2. Use the admin credentials you provided during installation:
   - **Email:** The email you entered (default: `admin@faeflux.local`)
   - **Password:** The password you entered
3. **⚠️ IMPORTANT:** Change the password immediately after first login!

## 📝 Quick Reference Commands

```bash
# Navigate to project
cd ~/Faeflux-One

# Start development servers (easiest)
./dev-start.sh

# Check if services are running (production)
sudo systemctl status faeflux-api
sudo systemctl status faeflux-web

# View logs (production)
sudo journalctl -u faeflux-api -f
sudo journalctl -u faeflux-web -f
```

## 🛠️ Troubleshooting

### Installation Fails

**Problem:** Script exits with errors

**Solution:**
```bash
# Check error messages in terminal
# Common issues:
# - Need to run: sudo apt update
# - PostgreSQL not installed: sudo apt install postgresql
# - Python version issue: Check with python3 --version
```

### Can't Connect to Database

**Problem:** Database connection errors

**Solution:**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Start PostgreSQL if stopped
sudo systemctl start postgresql

# Test connection
sudo -u postgres psql -c "SELECT version();"
```

### Port Already in Use

**Problem:** Port 3000 or 8000 already in use

**Solution:**
```bash
# Find what's using the port
sudo lsof -i :8000
sudo lsof -i :3000

# Stop the conflicting service or change ports in:
# - Backend: apps/api/.env (if using production)
# - Frontend: apps/web/package.json scripts
```

### Permission Errors

**Problem:** Permission denied errors

**Solution:**
```bash
# Ensure scripts are executable
chmod +x install.sh
chmod +x dev-start.sh

# Check file ownership
ls -la

# Fix ownership if needed (replace 'username' with your username)
sudo chown -R username:username ~/Faeflux-One
```

### Frontend Won't Start

**Problem:** `pnpm: command not found`

**Solution:**
```bash
# Install pnpm
npm install -g pnpm

# Or reinstall Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
npm install -g pnpm
```

### Backend Won't Start

**Problem:** Module not found errors

**Solution:**
```bash
cd ~/Faeflux-One/apps/api
source venv/bin/activate
pip install -r requirements.txt
```

## 📚 Additional Resources

- **Main README:** [README.md](./README.md)
- **Detailed Installation Guide:** [INSTALLATION.md](./INSTALLATION.md)
- **API Documentation:** http://localhost:8000/docs (after starting)

## 🆘 Getting Help

If you encounter issues:

1. **Check the logs:**
   ```bash
   # Development: Check terminal output
   # Production: 
   sudo journalctl -u faeflux-api -n 50
   ```

2. **Verify installation:**
   ```bash
   # Check Python version
   python3 --version
   
   # Check Node.js version
   node --version
   
   # Check PostgreSQL
   sudo systemctl status postgresql
   ```

3. **GitHub Issues:** 
   Visit: https://github.com/ferhatyildiz-dvlp/Faeflux-One/issues

## ✅ Post-Installation Checklist

After successful installation:

- [ ] Successfully logged in with admin account
- [ ] Changed admin password
- [ ] Tested API at http://localhost:8000/docs
- [ ] Reviewed `.env` files (keep them secure!)
- [ ] Backed up database password
- [ ] Bookmarked the application URL

## 🎉 You're All Set!

Enjoy using Faeflux One! For production deployment, refer to the [README.md](./README.md) for systemd and Nginx setup instructions.


