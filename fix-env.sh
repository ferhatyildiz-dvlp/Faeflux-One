#!/bin/bash
# Quick script to fix .env file format for CORS_ORIGINS and ALLOWED_HOSTS

ENV_FILE="apps/api/.env"

if [ ! -f "$ENV_FILE" ]; then
    echo "Error: $ENV_FILE not found"
    exit 1
fi

# Read current DOMAIN from .env if it exists, or use localhost
DOMAIN=$(grep -E "^DOMAIN=" "$ENV_FILE" 2>/dev/null | cut -d'=' -f2 || echo "")
if [ -z "$DOMAIN" ] || [ "$DOMAIN" = "localhost" ]; then
    CORS_ORIGINS='["http://localhost:3000"]'
    ALLOWED_HOSTS='["localhost"]'
else
    CORS_ORIGINS="[\"http://localhost:3000\",\"https://$DOMAIN\"]"
    ALLOWED_HOSTS="[\"localhost\",\"$DOMAIN\"]"
fi

# Create a backup
cp "$ENV_FILE" "${ENV_FILE}.backup"

# Fix CORS_ORIGINS
if grep -q '^CORS_ORIGINS=' "$ENV_FILE"; then
    sed -i "s|^CORS_ORIGINS=.*|CORS_ORIGINS=$CORS_ORIGINS|" "$ENV_FILE"
fi

# Fix ALLOWED_HOSTS
if grep -q '^ALLOWED_HOSTS=' "$ENV_FILE"; then
    sed -i "s|^ALLOWED_HOSTS=.*|ALLOWED_HOSTS=$ALLOWED_HOSTS|" "$ENV_FILE"
fi

echo "✓ Fixed .env file format"
echo "  CORS_ORIGINS=$CORS_ORIGINS"
echo "  ALLOWED_HOSTS=$ALLOWED_HOSTS"
echo "  Backup saved to: ${ENV_FILE}.backup"

