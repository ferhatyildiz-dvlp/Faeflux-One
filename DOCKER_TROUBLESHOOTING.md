# Docker Sorun Giderme Rehberi

## 🔍 Hata Tespiti

### 1. Logları Kontrol Edin

```bash
# Tüm servislerin logları
docker-compose logs

# Sadece web servisi logları
docker-compose logs web

# Canlı log takibi
docker-compose logs -f web
```

### 2. Container Durumlarını Kontrol Edin

```bash
docker-compose ps

# Detaylı bilgi
docker ps -a
```

## 🐛 Yaygın Hatalar ve Çözümleri

### Hata 1: "Cannot install with frozen-lockfile"

**Çözüm:**
```bash
# pnpm-lock.yaml dosyasını oluşturun
cd apps/web
pnpm install
cd ../..

# Docker'ı yeniden build edin
docker-compose build --no-cache web
docker-compose up -d
```

### Hata 2: "Service 'web' failed to build"

**Çözüm:**
```bash
# Önce temizleyin
docker-compose down
docker system prune -f

# Tekrar build edin
docker-compose build web
docker-compose up -d
```

### Hata 3: "Permission denied" veya "EACCES"

**Çözüm:**
```bash
# Docker grubunu kontrol edin
groups | grep docker

# Yoksa ekleyin
sudo usermod -aG docker $USER
newgrp docker

# Dosya izinlerini düzeltin
sudo chown -R $USER:$USER .
```

### Hata 4: Port Zaten Kullanımda

**Çözüm:**
```bash
# Hangi process portu kullanıyor?
sudo lsof -i :3000
sudo lsof -i :8000
sudo lsof -i :5432

# Process'i durdurun
sudo kill -9 <PID>

# Veya docker-compose'u durdurun
docker-compose down
```

### Hata 5: Database Connection Failed

**Çözüm:**
```bash
# PostgreSQL'in hazır olmasını bekleyin
docker-compose up -d postgres
sleep 10

# PostgreSQL loglarını kontrol edin
docker-compose logs postgres

# Database'e bağlanmayı test edin
docker-compose exec postgres psql -U faeflux -d faeflux_one -c "SELECT 1;"
```

### Hata 6: Container Sürekli Restart Oluyor

**Çözüm:**
```bash
# Logları kontrol edin
docker-compose logs web
docker-compose logs api

# Container'ı manuel başlatın (debug için)
docker-compose run --rm web sh
# İçerde komutları test edin
```

## 🔧 Manuel Düzeltme Adımları

### Web Container'ını Manuel Başlatma

```bash
# Container'ı durdurun
docker-compose stop web

# Container içine girin
docker-compose run --rm web sh

# İçerde şunları deneyin:
pnpm install
pnpm dev
```

### API Container'ını Manuel Başlatma

```bash
# Container'ı durdurun
docker-compose stop api

# Container içine girin
docker-compose run --rm api bash

# İçerde şunları deneyin:
python --version
pip list
alembic upgrade head
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 🧹 Temiz Kurulum

Eğer hiçbir şey çalışmıyorsa, temiz kurulum yapın:

```bash
# Tüm container'ları ve volume'ları sil
docker-compose down -v

# Docker cache'i temizle
docker system prune -a -f

# Images'ları temizle
docker rmi $(docker images -q) 2>/dev/null || true

# Yeniden build edin
docker-compose build --no-cache
docker-compose up -d

# Logları izleyin
docker-compose logs -f
```

## 📋 Kontrol Listesi

Kurulum sonrası kontrol:

```bash
# 1. Container'lar çalışıyor mu?
docker-compose ps
# Hepsi "Up" olmalı

# 2. API sağlık kontrolü
curl http://localhost:8000/health
# veya
curl http://localhost:8000/docs

# 3. Web sayfası açılıyor mu?
curl http://localhost:3000

# 4. Database bağlantısı
docker-compose exec postgres psql -U faeflux -d faeflux_one -c "SELECT version();"
```

## 🆘 Hala Çalışmıyorsa

1. **Logları paylaşın:**
```bash
docker-compose logs > docker_logs.txt
cat docker_logs.txt
```

2. **Environment dosyasını kontrol edin:**
```bash
cat .env.docker
```

3. **Docker versiyonunu kontrol edin:**
```bash
docker --version
docker-compose --version
```

4. **Disk alanını kontrol edin:**
```bash
df -h
docker system df
```

## 💡 Hızlı Düzeltme Komutları

```bash
# Her şeyi durdur ve temizle
docker-compose down -v && docker system prune -f

# Yeniden başlat
docker-compose build && docker-compose up -d

# Logları izle
docker-compose logs -f
```

