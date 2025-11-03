# 🐳 Docker ile Faeflux One Kurulumu

Docker ile kurulum çok daha kolay! Tüm bağımlılıklar container içinde kalır, sisteminizi kirletmez.

## 📋 Gereksinimler

- Docker 20.10+
- Docker Compose 2.0+

Ubuntu'da kurulum:
```bash
sudo apt update
sudo apt install -y docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
# Yeni grubun aktif olması için oturumu kapatıp açın veya:
newgrp docker
```

## 🚀 Hızlı Başlangıç

### 1. Projeyi İndirin

```bash
cd ~
git clone https://github.com/ferhatyildiz-dvlp/Faeflux-One.git
cd Faeflux-One
```

### 2. Environment Dosyasını Oluşturun

```bash
cp .env.docker.example .env.docker
nano .env.docker
```

Önemli değerleri düzenleyin:
- `DB_PASSWORD` - Güçlü bir veritabanı şifresi
- `SECRET_KEY` - `openssl rand -hex 32` ile oluşturun

### 3. RSA Anahtarları Oluşturun (İlk Kurulum)

```bash
cd apps/api
openssl genrsa -out private.pem 2048
openssl rsa -in private.pem -pubout -out public.pem
chmod 600 private.pem
chmod 644 public.pem
cd ../..
```

### 4. Container'ları Başlatın

```bash
docker-compose up -d
```

Bu komut:
- ✅ PostgreSQL container'ı oluşturur ve başlatır
- ✅ Backend API container'ı oluşturur ve başlatır
- ✅ Frontend Web container'ı oluşturur ve başlatır
- ✅ Database migration'ları çalıştırır
- ✅ Admin kullanıcı oluşturur

### 5. Logları İzleyin

```bash
# Tüm servislerin logları
docker-compose logs -f

# Sadece API logları
docker-compose logs -f api

# Sadece Web logları
docker-compose logs -f web

# PostgreSQL logları
docker-compose logs -f postgres
```

## 🌐 Erişim

Kurulum tamamlandıktan sonra:

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Dokümantasyonu:** http://localhost:8000/docs

**Varsayılan Admin Girişi:**
- Email: `admin@faeflux.local`
- Şifre: Script tarafından oluşturulan şifre (loglarda görünecek)

## 🛠️ Yönetim Komutları

### Container'ları Durdurma
```bash
docker-compose stop
```

### Container'ları Başlatma
```bash
docker-compose start
```

### Container'ları Tamamen Kaldırma (Veriler korunur)
```bash
docker-compose down
```

### Container'ları ve Verileri Tamamen Kaldırma
```bash
docker-compose down -v
```

### Container'ları Yeniden Oluşturma
```bash
docker-compose up -d --build
```

### Tek Bir Servisi Yeniden Başlatma
```bash
docker-compose restart api
docker-compose restart web
docker-compose restart postgres
```

### Container İçine Girme
```bash
# API container'ına gir
docker-compose exec api bash

# Web container'ına gir
docker-compose exec web sh

# PostgreSQL container'ına gir
docker-compose exec postgres psql -U faeflux -d faeflux_one
```

## 🔧 Geliştirme Modu

Geliştirme için volume'lar aktif. Kod değişiklikleriniz otomatik olarak container içine yansır:

```bash
# Development modunda başlat
docker-compose up

# Veya arka planda
docker-compose up -d
```

## 🏭 Production Modu

Production için:

1. **Web Dockerfile'ını güncelleyin:**
```dockerfile
# apps/web/Dockerfile içinde production build kısmını açın
RUN pnpm build
CMD ["pnpm", "start"]
```

2. **docker-compose.prod.yml oluşturun:**
```yaml
# docker-compose.yml'in production versiyonu
# Volume'ları kaldırın, sadece build'leri kullanın
```

3. **Production'da çalıştırın:**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 📊 Durum Kontrolü

```bash
# Container durumları
docker-compose ps

# Container kaynak kullanımı
docker stats

# Database bağlantısını test et
docker-compose exec api python -c "from app.core.database import engine; print('DB OK' if engine else 'DB FAIL')"
```

## 🔄 Migration Çalıştırma

Yeni migration oluşturma:
```bash
docker-compose exec api alembic revision --autogenerate -m "migration name"
docker-compose exec api alembic upgrade head
```

## 👤 Admin Kullanıcı Oluşturma

```bash
docker-compose exec api python scripts/create_admin.py
```

## 🗄️ Veritabanı Yedekleme

```bash
# Yedek al
docker-compose exec postgres pg_dump -U faeflux faeflux_one > backup.sql

# Yedekten geri yükle
docker-compose exec -T postgres psql -U faeflux faeflux_one < backup.sql
```

## ❌ Sorun Giderme

### Port Kullanımda Hatası
```bash
# Hangi process portu kullanıyor?
sudo lsof -i :8000
sudo lsof -i :3000
sudo lsof -i :5432

# Process'i durdur
sudo kill -9 <PID>
```

### Container Başlamıyor
```bash
# Logları kontrol et
docker-compose logs

# Container'ı yeniden oluştur
docker-compose up -d --force-recreate

# Image'ları temizle ve yeniden oluştur
docker-compose build --no-cache
docker-compose up -d
```

### Database Bağlantı Hatası
```bash
# PostgreSQL'in çalıştığını kontrol et
docker-compose ps postgres

# PostgreSQL loglarını kontrol et
docker-compose logs postgres

# Database'i yeniden oluştur
docker-compose down -v
docker-compose up -d postgres
# Biraz bekleyin, sonra diğer servisleri başlatın
docker-compose up -d
```

### Permission Hatası
```bash
# RSA key izinlerini düzelt
chmod 600 apps/api/private.pem
chmod 644 apps/api/public.pem
```

## 📝 Environment Değişkenleri

`.env.docker` dosyasında tüm ayarları yapabilirsiniz:

```bash
# Yeni bir secret key oluştur
openssl rand -hex 32

# .env.docker dosyasına ekle
SECRET_KEY=<oluşturulan_key>
```

## 🎯 Docker vs Native Kurulum

| Özellik | Docker | Native |
|---------|--------|--------|
| Kurulum | ✅ Çok kolay | ⚠️ Daha karmaşık |
| Sistem Paketleri | ❌ Gereksiz | ✅ Gerekli |
| İzolasyon | ✅ Mükemmel | ❌ Sistemde çalışır |
| Taşınabilirlik | ✅ Çok iyi | ⚠️ Sistem bağımlı |
| Performans | ✅ İyi | ✅ Biraz daha iyi |
| Geliştirme | ✅ Kolay | ✅ Kolay |

## 🚀 Hızlı Komutlar

```bash
# Her şeyi başlat
docker-compose up -d

# Her şeyi durdur
docker-compose stop

# Logları izle
docker-compose logs -f

# Yeniden başlat
docker-compose restart

# Temiz kurulum (dikkatli! veriler silinir)
docker-compose down -v
docker-compose up -d --build
```

## ✅ Kurulum Sonrası Kontrol

```bash
# Tüm servisler çalışıyor mu?
docker-compose ps

# API sağlık kontrolü
curl http://localhost:8000/health

# Frontend açılıyor mu?
curl http://localhost:3000

# Database bağlantısı
docker-compose exec postgres psql -U faeflux -d faeflux_one -c "SELECT version();"
```

**Başarılar! 🎉**

Docker ile kurulum çok daha temiz ve kolay. Sorun yaşarsanız logları kontrol edin!

