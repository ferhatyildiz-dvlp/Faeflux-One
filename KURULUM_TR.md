# Faeflux One - Ubuntu 24 Kurulum Kılavuzu

## 📋 Ön Gereksinimler

Ubuntu 24.04 LTS sisteminizde aşağıdaki paketlerin yüklü olması gerekiyor:

- Python 3.12+
- PostgreSQL 16+
- Node.js 20+
- Nginx
- Git

## 📥 İndirme ve Kurulum

### 1. Projeyi İndirin

**ÖNEMLİ:** Projeyi `/home/ferhat/` veya kullanıcı home dizininize indirin. Root dizinine indirmeyin.

```bash
# Home dizinine git
cd ~

# Projeyi klonla
git clone https://github.com/ferhatyildiz-dvlp/Faeflux-One.git

# Proje dizinine gir
cd Faeflux-One
```

### 2. Kurulum Scriptini Çalıştırın

```bash
# Çalıştırma izni ver
chmod +x install.sh

# Kurulumu başlat (sudo olmadan çalıştırın, script gerekli yerlerde sudo soracak)
./install.sh
```

**NOT:** Script'i `sudo` ile çalıştırmayın! Normal kullanıcı olarak çalıştırın, script gerekli yerlerde sudo şifresi soracak.

### 3. Kurulum Sırasında Sorulacaklar

1. **Domain:** Localhost için boş bırakın veya Enter'a basın
2. **PostgreSQL Şifresi:** Güçlü bir şifre girin
3. **Admin Email:** Varsayılan olarak `admin@faeflux.local`
4. **Admin Şifresi:** En az 8 karakter

## 🔧 Manuel Kurulum (Script Çalışmazsa)

Eğer script çalışmazsa, adım adım manuel kurulum:

### Adım 1: Sistem Güncellemesi

```bash
sudo apt update && sudo apt upgrade -y
```

### Adım 2: Temel Paketleri Yükle

```bash
sudo apt install -y \
    python3.12 python3.12-venv python3-pip \
    postgresql-16 postgresql-contrib \
    nginx certbot python3-certbot-nginx \
    curl git build-essential \
    libpq-dev
```

### Adım 3: Node.js Kurulumu

```bash
# Node.js repository ekle
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -

# Node.js yükle
sudo apt install -y nodejs

# pnpm yükle
sudo npm install -g pnpm
```

### Adım 4: PostgreSQL Kurulumu

```bash
# PostgreSQL kullanıcı ve veritabanı oluştur
sudo -u postgres psql <<EOF
CREATE USER faeflux WITH PASSWORD 'GÜÇLÜ_ŞİFRE_BURAYA';
CREATE DATABASE faeflux_one;
GRANT ALL PRIVILEGES ON DATABASE faeflux_one TO faeflux;
\q
EOF
```

### Adım 5: Backend Kurulumu

```bash
cd ~/Faeflux-One/apps/api

# Virtual environment oluştur
python3.12 -m venv venv

# Virtual environment aktif et
source venv/bin/activate

# Python paketlerini yükle
pip install --upgrade pip
pip install -r requirements.txt

# RSA anahtarları oluştur
openssl genrsa -out private.pem 2048
openssl rsa -in private.pem -pubout -out public.pem
chmod 600 private.pem
chmod 644 public.pem

# .env dosyası oluştur (aşağıdaki içeriği düzenleyin)
nano .env
```

`.env` dosyası içeriği:

```env
# Application
APP_NAME=Faeflux One
DEBUG=false
ENVIRONMENT=production

# Database (GÜÇLÜ_ŞİFRE_BURAYA yerine gerçek şifrenizi yazın)
DATABASE_URL=postgresql://faeflux:GÜÇLÜ_ŞİFRE_BURAYA@localhost:5432/faeflux_one
DATABASE_ECHO=false

# Security
SECRET_KEY=$(openssl rand -hex 32)
JWT_ALGORITHM=RS256
JWT_PRIVATE_KEY_PATH=./private.pem
JWT_PUBLIC_KEY_PATH=./public.pem
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=14

# CORS (JSON formatında)
CORS_ORIGINS=["http://localhost:3000"]

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60

# Allowed Hosts (JSON formatında)
ALLOWED_HOSTS=["localhost"]

# File Upload
MAX_UPLOAD_SIZE=10485760
```

**ÖNEMLİ:** `CORS_ORIGINS` ve `ALLOWED_HOSTS` mutlaka JSON array formatında olmalı!

### Adım 6: Database Migration

```bash
# Migration çalıştır
alembic upgrade head

# İlk migration yoksa oluştur
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### Adım 7: Admin Kullanıcı Oluştur

```bash
python scripts/create_admin.py
```

Veya manuel:

```bash
python <<EOF
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
from sqlmodel import Session, select
from app.core.database import engine
from app.core.auth import get_password_hash
from app.models.user import User, UserRole

with Session(engine) as session:
    statement = select(User).where(User.email == "admin@faeflux.local")
    existing = session.exec(statement).first()
    
    if existing:
        print("Admin user already exists.")
    else:
        admin = User(
            email="admin@faeflux.local",
            hashed_password=get_password_hash("Admin@123!"),
            full_name="System Administrator",
            role=UserRole.ADMIN,
            is_active=True,
        )
        session.add(admin)
        session.commit()
        print("Admin user created: admin@faeflux.local")
EOF
```

### Adım 8: Frontend Kurulumu

```bash
cd ~/Faeflux-One/apps/web

# Node.js paketlerini yükle
pnpm install

# .env.local dosyası oluştur
cat > .env.local <<EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
EOF
```

## 🚀 Çalıştırma

### Geliştirme Modu

```bash
cd ~/Faeflux-One
./dev-start.sh
```

Veya manuel:

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

### Erişim

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## ❌ Yaygın Hatalar ve Çözümleri

### Hata 1: "Permission denied"
```bash
# Dosya izinlerini düzelt
sudo chown -R $USER:$USER ~/Faeflux-One
chmod +x ~/Faeflux-One/install.sh
```

### Hata 2: "CORS_ORIGINS" JSON hatası
`.env` dosyasında `CORS_ORIGINS` ve `ALLOWED_HOSTS` JSON formatında olmalı:
```env
CORS_ORIGINS=["http://localhost:3000"]
ALLOWED_HOSTS=["localhost"]
```

### Hata 3: PostgreSQL bağlantı hatası
```bash
# PostgreSQL servisini kontrol et
sudo systemctl status postgresql

# PostgreSQL'i başlat
sudo systemctl start postgresql

# Bağlantıyı test et
sudo -u postgres psql -c "SELECT version();"
```

### Hata 4: "User is not defined" hatası
Model dosyalarında forward reference kullanılmalı. Bu zaten düzeltildi, projeyi güncelleyin:
```bash
cd ~/Faeflux-One
git pull
```

### Hata 5: pnpm bulunamıyor
```bash
# pnpm'i global yükle
sudo npm install -g pnpm

# Veya corepack kullan
sudo corepack enable
corepack prepare pnpm@latest --activate
```

## 📞 Destek

Sorun yaşarsanız:
1. Kurulum log dosyasını kontrol edin: `~/faeflux_install_*.log`
2. Backend logları: `apps/api/` dizininde
3. Frontend logları: Terminal çıktısında

## ✅ Kurulum Sonrası Kontrol Listesi

- [ ] PostgreSQL çalışıyor mu? (`sudo systemctl status postgresql`)
- [ ] Backend çalışıyor mu? (`curl http://localhost:8000/health`)
- [ ] Frontend çalışıyor mu? (http://localhost:3000 açılıyor mu?)
- [ ] Admin kullanıcı ile giriş yapabiliyor musunuz?
- [ ] Database migration'lar çalıştı mı?

Başarılar! 🎉

