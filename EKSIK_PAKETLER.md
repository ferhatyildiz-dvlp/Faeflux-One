# Eksik Paket Listesi ve Açıklamaları

Bu belge, Faeflux One kurulumu için gereken tüm sistem paketlerini listeler.

## 📦 Sistem Paketleri (Ubuntu 24.04)

### Python Geliştirme Paketleri
```bash
python3.12          # Python 3.12 interpreter
python3.12-venv     # Virtual environment desteği
python3.12-dev      # Python geliştirme başlıkları (C extension derleme için)
python3-pip         # Python paket yöneticisi
python3-setuptools  # Paket kurulum araçları
python3-wheel       # Wheel format desteği
```

### PostgreSQL Paketleri
```bash
postgresql-16              # PostgreSQL veritabanı sunucusu
postgresql-contrib         # PostgreSQL ek modülleri
postgresql-server-dev-16   # PostgreSQL geliştirme başlıkları (psycopg2 için)
libpq-dev                  # PostgreSQL client kütüphanesi (psycopg2 için)
```

### Web Sunucu Paketleri
```bash
nginx                     # Web sunucusu
certbot                   # SSL sertifika yöneticisi
python3-certbot-nginx     # Certbot Nginx eklentisi
```

### Derleme Araçları
```bash
build-essential           # GCC, make ve diğer derleme araçları
pkg-config                # Kütüphane bulma aracı
```

### Kriptografi ve Güvenlik
```bash
libssl-dev                # OpenSSL geliştirme başlıkları (cryptography paketi için)
libffi-dev                # Foreign Function Interface (cffi için)
openssl                   # OpenSSL araçları (RSA key oluşturma için)
```

### Diğer Araçlar
```bash
curl                      # HTTP istemcisi (Node.js repository için)
git                       # Version control
```

## 🐍 Python Paketleri (requirements.txt'den)

Bu paketler `pip install -r requirements.txt` ile yüklenir:

- `fastapi` - Web framework
- `uvicorn[standard]` - ASGI sunucusu
- `sqlmodel` - ORM
- `alembic` - Database migration aracı ⚠️ **ÖNEMLİ: Bu Python paketi, sistem paketi değil!**
- `psycopg2-binary` - PostgreSQL driver
- `pydantic` - Veri validasyonu
- `pydantic-settings` - Settings yönetimi
- `python-jose[cryptography]` - JWT token işlemleri
- `passlib[bcrypt]` - Şifre hashleme
- `python-multipart` - Form data işleme
- `structlog` - Logging
- `slowapi` - Rate limiting
- `httpx` - HTTP client
- `python-dateutil` - Tarih işlemleri

## ⚠️ ÖNEMLİ NOTLAR

### Alembic Hakkında
**Alembic bir sistem paketi DEĞİLDİR!** Alembic Python paketidir ve `pip install` ile yüklenir.

Eğer `alembic: command not found` hatası alırsanız:
1. Virtual environment aktif değildir
2. `requirements.txt` paketleri yüklenmemiştir

Çözüm:
```bash
cd apps/api
source venv/bin/activate
pip install -r requirements.txt
# Alembic artık çalışacak
alembic upgrade head
```

### psycopg2 Derleme Sorunları
`psycopg2-binary` kullanıyoruz (binary versiyon, derleme gerektirmez), ancak yine de bazı sistemlerde `libpq-dev` gerekebilir.

Eğer `psycopg2` kurulumunda hata alırsanız:
```bash
sudo apt install libpq-dev postgresql-server-dev-16
pip install --no-cache-dir psycopg2-binary
```

### Cryptography Paketi
`python-jose[cryptography]` paketi `libssl-dev` gerektirir.

## ✅ Kurulum Kontrol Listesi

Kurulumdan önce kontrol edin:

```bash
# Python kontrolü
python3.12 --version || python3 --version

# PostgreSQL kontrolü
sudo systemctl status postgresql
psql --version

# Gerekli kütüphaneler kontrolü
pkg-config --exists libpq && echo "libpq-dev OK" || echo "libpq-dev EKSIK"
pkg-config --exists openssl && echo "openssl-dev OK" || echo "openssl-dev EKSIK"
pkg-config --exists libffi && echo "libffi-dev OK" || echo "libffi-dev EKSIK"

# Node.js kontrolü
node --version
npm --version
```

## 🔧 Manuel Paket Kurulumu

Eğer script çalışmazsa, tüm paketleri manuel yükleyin:

```bash
sudo apt update

sudo apt install -y \
    python3.12 python3.12-venv python3.12-dev python3-pip \
    postgresql-16 postgresql-contrib postgresql-server-dev-16 \
    nginx certbot python3-certbot-nginx \
    curl git build-essential \
    libpq-dev libssl-dev libffi-dev \
    pkg-config python3-setuptools python3-wheel \
    openssl
```

Sonra Python paketlerini yükleyin:
```bash
cd ~/Faeflux-One/apps/api
python3.12 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

Bu işlem Alembic dahil tüm Python paketlerini yükleyecektir! ✅

