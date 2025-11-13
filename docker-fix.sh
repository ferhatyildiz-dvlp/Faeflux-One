#!/bin/bash

# Docker Fix Script - Sorunları otomatik düzeltir

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔧 Docker Sorun Giderme Scripti${NC}"
echo ""

# 1. Container'ları durdur
echo -e "${YELLOW}1. Container'ları durduruyorum...${NC}"
docker-compose down 2>/dev/null || true

# 2. Web için pnpm-lock.yaml oluştur
echo -e "${YELLOW}2. pnpm-lock.yaml dosyasını kontrol ediyorum...${NC}"
if [ ! -f "apps/web/pnpm-lock.yaml" ]; then
    echo -e "${BLUE}   pnpm-lock.yaml yok, oluşturuyorum...${NC}"
    cd apps/web
    if command -v pnpm &> /dev/null; then
        pnpm install
    else
        echo -e "${YELLOW}   pnpm bulunamadı, npm kullanıyorum...${NC}"
        npm install
    fi
    cd ../..
fi

# 3. RSA keys kontrolü
echo -e "${YELLOW}3. RSA anahtarlarını kontrol ediyorum...${NC}"
if [ ! -f "apps/api/private.pem" ] || [ ! -f "apps/api/public.pem" ]; then
    echo -e "${BLUE}   RSA anahtarları oluşturuluyor...${NC}"
    openssl genrsa -out apps/api/private.pem 2048
    openssl rsa -in apps/api/private.pem -pubout -out apps/api/public.pem
    chmod 600 apps/api/private.pem
    chmod 644 apps/api/public.pem
fi

# 4. Environment dosyası kontrolü
echo -e "${YELLOW}4. Environment dosyasını kontrol ediyorum...${NC}"
if [ ! -f ".env.docker" ]; then
    echo -e "${BLUE}   .env.docker dosyası oluşturuluyor...${NC}"
    cat > .env.docker <<EOF
DB_PASSWORD=changeme_in_production
SECRET_KEY=$(openssl rand -hex 32)
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
CORS_ORIGINS=["http://localhost:3000"]
ALLOWED_HOSTS=["localhost"]
DEBUG=false
ENVIRONMENT=production
EOF
fi

# 5. Docker images'ları temizle ve yeniden build et
echo -e "${YELLOW}5. Docker images'ları temizliyorum...${NC}"
docker-compose build --no-cache

# 6. Container'ları başlat
echo -e "${YELLOW}6. Container'ları başlatıyorum...${NC}"
docker-compose up -d

# 7. Servislerin hazır olmasını bekle
echo -e "${YELLOW}7. Servislerin hazır olmasını bekliyorum...${NC}"
sleep 15

# 8. Durum kontrolü
echo ""
echo -e "${GREEN}📊 Durum Kontrolü:${NC}"
docker-compose ps

echo ""
echo -e "${GREEN}📋 Son Loglar:${NC}"
docker-compose logs --tail=20

echo ""
echo -e "${GREEN}✅ İşlem tamamlandı!${NC}"
echo -e "${BLUE}Logları izlemek için: docker-compose logs -f${NC}"
echo -e "${BLUE}Durum için: docker-compose ps${NC}"

