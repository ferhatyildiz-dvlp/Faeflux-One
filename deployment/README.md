# Deployment Guide

This directory contains deployment configuration files for Faeflux One.

## Files

- `systemd/` - Systemd service files for API and Web services
- `nginx/` - Nginx configuration for reverse proxy
- `scripts/` - Setup and deployment scripts

## Quick Deploy

1. Run the setup script:
```bash
sudo bash deployment/scripts/setup.sh your-domain.com
```

2. Copy systemd service files:
```bash
sudo cp deployment/systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload
```

3. Configure Nginx:
```bash
sudo cp deployment/nginx/faeflux-one.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/faeflux-one.conf /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

4. Setup SSL:
```bash
sudo certbot --nginx -d your-domain.com
```

## Manual Configuration

Edit the service files and Nginx config to match your environment:
- Update paths in systemd services
- Update domain in Nginx config
- Update database credentials in .env files


