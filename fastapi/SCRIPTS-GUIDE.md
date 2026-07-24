# 📜 PowerShell Scripts Kılavuzu

Bu proje için oluşturulan PowerShell (.ps1) automation script'leri ve kullanım detayları.

---

## 🚀 Deployment Scripts

### 1. **deploy-to-minikube.ps1**

**İşlevi:** Tüm uygulamayı Minikube'a otomatik deploy eder (Birincil deployment yöntemi)

**Ne Yapar:**
1. Minikube durumunu kontrol eder (gerekirse başlatır)
2. Minikube addons'ları aktifleştirir (ingress, metrics-server)
3. Minikube Docker environment kullanarak image build eder
4. MSSQL ve Redis dependencies'lerini deploy eder
5. ConfigMap ve Secret'ları oluşturur
6. Product Service deployment'ını yapar
7. HPA (Horizontal Pod Autoscaler) yapılandırır
8. Service URL'ini gösterir ve tarayıcıda açma seçeneği sunar
9. Port-forward başlatma seçeneği sunar

**Kullanım:**
```powershell
cd c:\zattekce\Kubernets\Edu\fastapi
.\deploy-to-minikube.ps1
```

**Gereksinimler:**
- Minikube yüklü ve çalışıyor
- kubectl yapılandırılmış
- Docker (Minikube içinde)

**Çıktılar:**
- Pod'ların durumu
- Service URL'leri
- Swagger UI bağlantısı
- Faydalı komutlar listesi

---

### 2. **deploy-offline.ps1**

**İşlevi:** Image'ı host makinede build edip Minikube'a tar olarak transfer eder

**Ne Yapar:**
1. Host makinedeki Docker Desktop'ı kontrol eder
2. Docker image'ı host makinede build eder (internet bağlantınızı kullanır)
3. Image'ı tar dosyasına export eder
4. Tar dosyasını Minikube içine yükler
5. ConfigMap ve Secret oluşturur
6. Dependencies (MSSQL, Redis) deploy eder
7. Application deployment yapar
8. Service URL'ini gösterir

**Kullanım:**
```powershell
.\deploy-offline.ps1
```

**Ne Zaman Kullanılır:**
- Kurumsal ağlarda TLS/SSL sertifika sorunları olduğunda
- Minikube Docker daemon'ı PyPI veya Docker Hub'a erişemediğinde
- Host makineniniz internet bağlantısı varsa

**Avantajları:**
- %100 çalışır garanti
- Host makinenin kurumsal sertifikalarını kullanır
- Minikube ağ sorunlarından bağımsız

---

### 3. **quick-rebuild.ps1**

**İşlevi:** Image'ı yeniden build edip deployment'ı restart eder (Kod değişikliklerinden sonra)

**Ne Yapar:**
1. Minikube Docker environment hazırlar
2. `--no-cache` ile image'ı tamamen yeniden build eder
3. Mevcut deployment'ı siler
4. Yeni deployment'ı oluşturur
5. Pod'ların hazır olmasını bekler
6. Son logları gösterir

**Kullanım:**
```powershell
.\quick-rebuild.ps1
```

**Ne Zaman Kullanılır:**
- Kod değişikliği yaptıktan sonra
- Yeni dependency ekledikten sonra (requirements.txt)
- Dockerfile güncelledikten sonra
- Environment variable'ları değiştirdikten sonra

**Özellikler:**
- `--no-cache` kullanır (temiz build)
- Deployment'ı siler ve yeniden oluşturur
- Pod ready durumunu bekler

---

## 🗄️ Database Management Scripts

### 4. **setup-database.ps1**

**İşlevi:** MSSQL pod'unda ProductManagementDB database'ini oluşturur

**Ne Yapar:**
1. MSSQL pod'unu bulur ve ready olmasını bekler
2. `ProductManagementDB` database'ini oluşturur (IF NOT EXISTS)
3. Database'in başarıyla oluşturulduğunu doğrular
4. Application pod'larını restart eder

**Kullanım:**
```powershell
.\setup-database.ps1
```

**SQL Komutu:**
```sql
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'ProductManagementDB')
BEGIN
    CREATE DATABASE ProductManagementDB;
END
```

**Ne Zaman Kullanılır:**
- İlk deployment'tan sonra
- Database'i yanlışlıkla sildiyseniz
- MSSQL pod'unu yeniden başlattıktan sonra

---

### 5. **run-migrations.ps1**

**İşlevi:** Alembic database migrations çalıştırır (Schema oluşturma)

**Ne Yapar:**
1. Product Service pod'unu bulur
2. Mevcut migration durumunu gösterir (`alembic current`)
3. Migration geçmişini gösterir (`alembic history`)
4. Migrations çalıştırır (`alembic upgrade head`)
5. Final durumu doğrular

**Kullanım:**
```powershell
.\run-migrations.ps1
```

**Ne Zaman Kullanılır:**
- Database oluşturulduktan sonra (tablolar için)
- Yeni migration eklendikten sonra
- Database schema'sını güncellemek için

**Çalıştırdığı Alembic Komutları:**
```bash
alembic current    # Mevcut revision
alembic history    # Tüm migrations
alembic upgrade head  # Son versiyona upgrade
```

---

### 6. **reset-mssql.ps1**

**İşlevi:** MSSQL'i PVC (Persistent Volume Claim) dahil tamamen sıfırlar

**Ne Yapar:**
1. Kullanıcıdan onay ister (⚠️ Tüm data silinecek!)
2. MSSQL deployment'ını siler
3. MSSQL PVC'yi siler (tüm data kaybolur)
4. Temizlik için bekler
5. MSSQL'i yeniden oluşturur (yeni password ile)
6. SQL bağlantısını test eder
7. ProductManagementDB oluşturur
8. Application restart seçeneği sunar

**Kullanım:**
```powershell
.\reset-mssql.ps1
```

**⚠️ UYARI:** Bu script TÜM MSSQL verilerini siler!

**Ne Zaman Kullanılır:**
- Password değiştirdikten sonra
- MSSQL tamamen bozulduğunda
- Temiz başlangıç yapmak istediğinizde
- PVC'deki eski data sorun yaratıyorsa

---

### 7. **wait-for-mssql.ps1**

**İşlevi:** MSSQL'in tam hazır olmasını bekler ve database oluşturur

**Ne Yapar:**
1. MSSQL pod'unu bulur (yoksa deployment başlatır)
2. Pod'un Running olmasını bekler (max 120 saniye)
3. SQL bağlantısını test eder (30 deneme, her 5 saniyede)
4. ProductManagementDB oluşturur
5. Database'in var olduğunu doğrular
6. Application pod'larını restart eder
7. 30 saniye bekler (yeni pod'lar başlasın)
8. Durumu gösterir

**Kullanım:**
```powershell
.\wait-for-mssql.ps1
```

**Ne Zaman Kullanılır:**
- MSSQL yeni başlatıldıktan sonra
- Application "Login timeout" hatası verdiğinde
- MSSQL pod'u restart olduktan sonra

**Özellikleri:**
- Retry mekanizması (30 deneme)
- SQL bağlantı testi
- Otomatik database oluşturma
- Application pod restart

---

## 🌐 Port Forwarding Scripts

### 8. **port-forward.ps1**

**İşlevi:** localhost:8080'den FastAPI uygulamasına erişim sağlar

**Ne Yapar:**
1. Product Service'i localhost:8080'e forward eder
2. Erişim URL'lerini gösterir (Swagger UI, Health Check, Metrics)
3. Port forward'u aktif tutar (CTRL+C ile durdurulana kadar)

**Kullanım:**
```powershell
.\port-forward.ps1
```

**Erişim Adresleri:**
- **Swagger UI:** http://localhost:8080/api/v1/docs
- **ReDoc:** http://localhost:8080/api/v1/redoc
- **Health Check:** http://localhost:8080/health
- **Liveness:** http://localhost:8080/health/live
- **Readiness:** http://localhost:8080/health/ready
- **Metrics:** http://localhost:8080/metrics

**Not:** Terminal açık kalmalı! Kapatırsanız port-forward durur.

---

### 9. **port-forward-mssql.ps1**

**İşlevi:** localhost:1433'ten MSSQL'e SQL Server Management Studio (SSMS) bağlantısı sağlar

**Ne Yapar:**
1. MSSQL service'in varlığını kontrol eder
2. Port 1433'ü localhost'a forward eder
3. SSMS bağlantı bilgilerini gösterir
4. Port forward'u aktif tutar

**Kullanım:**
```powershell
.\port-forward-mssql.ps1
```

**SSMS Bağlantı Bilgileri:**
- **Server name:** `localhost,1433` (veya `127.0.0.1,1433`)
- **Authentication:** SQL Server Authentication
- **Login:** `sa`
- **Password:** `Az.123456+`
- **Encryption:** Optional (veya Trust server certificate)
- **Database:** ProductManagementDB

**Ne Zaman Kullanılır:**
- SQL Server Management Studio ile bağlanmak için
- Azure Data Studio ile bağlanmak için
- Database'i manuel sorgulamak için
- Tabloları görüntülemek için

---

## 🔄 Utility Scripts

### 10. **rollback-to-minikube-sql.ps1**

**İşlevi:** Host makinedeki SQL Server'dan Minikube içindeki SQL Server'a geri döner

**Ne Yapar:**
1. ConfigMap'i Minikube SQL için günceller (`mssql-service.default.svc.cluster.local`)
2. Secret'ı günceller
3. MSSQL deployment'ını başlatır (scale 1)
4. MSSQL pod'unun hazır olmasını bekler
5. ProductManagementDB oluşturur
6. Application pod'larını restart eder
7. Durumu gösterir

**Kullanım:**
```powershell
.\rollback-to-minikube-sql.ps1
```

**Ne Zaman Kullanılır:**
- Host SQL Server'a bağlanamadığınızda
- Host SQL Server yapılandırması karmaşık olduğunda
- Minikube içindeki SQL tercih edildiğinde
- Development için self-contained ortam istediğinizde

**Değişen Ayarlar:**
```yaml
# Önceden (Host SQL)
database_host: "host.minikube.internal"

# Sonradan (Minikube SQL)
database_host: "mssql-service.default.svc.cluster.local"
```

---

## 🔧 Diğer Utility Scripts

### **connect-host-sqlserver.ps1**

**İşlevi:** Host makinedeki SQL Server'a bağlanmak için yapılandırma yapar

**Ne Yapar:**
1. Minikube içindeki MSSQL pod'unu kapatır (scale 0)
2. ConfigMap'i host SQL için günceller
3. Host SQL Server'da database oluşturmayı dener (sqlcmd varsa)
4. Application pod'larını restart eder
5. Migrations çalıştırır

**Kullanım:**
```powershell
.\connect-host-sqlserver.ps1
```

---

### **diagnose-sqlserver.ps1**

**İşlevi:** Host SQL Server sorunlarını teşhis eder

**Ne Yapar:**
1. SQL Server servislerinin durumunu kontrol eder
2. Port 1433'ün dinlenip dinlenmediğini kontrol eder
3. Windows Firewall kurallarını listeler
4. TCP bağlantısını test eder
5. SQL Server Configuration Manager yolunu gösterir
6. Çözüm önerileri sunar
7. SQL Server servisini otomatik başlatma seçeneği

**Kullanım:**
```powershell
.\diagnose-sqlserver.ps1
```

---

### **fix-docker-certs.ps1**

**İşlevi:** Windows kurumsal sertifikalarını Minikube içine kopyalar

**Ne Yapar:**
1. Windows LocalMachine\Root sertifikalarını export eder
2. PEM formatına çevirir
3. Minikube içine kopyalar
4. System sertifikalarını günceller (`update-ca-certificates`)
5. Docker daemon'ı restart eder

**Kullanım:**
```powershell
.\fix-docker-certs.ps1
```

**Ne Zaman Kullanılır:**
- Kurumsal ağda SSL sertifika hataları alındığında
- Docker Hub veya PyPI bağlantı sorunları olduğunda
- Self-signed certificate hataları için

---

### **fix-docker-proxy.ps1**

**İşlevi:** Minikube Docker daemon için proxy yapılandırması

**Ne Yapar:**
1. Kullanıcıdan proxy bilgilerini alır (HTTP, HTTPS, No Proxy)
2. Docker daemon config dosyasını oluşturur
3. Proxy yoksa TLS bypass config yapar
4. Docker daemon'ı restart eder
5. Durumu kontrol eder

**Kullanım:**
```powershell
.\fix-docker-proxy.ps1
```

**Ne Zaman Kullanılır:**
- Kurumsal proxy arkasındaysanız
- Docker Hub'a proxy üzerinden erişmeniz gerekiyorsa

---

## 📋 Script Kullanım Sırası

### 🆕 İlk Deployment

```powershell
# 1. Ana deployment (TLS sorun yoksa)
.\deploy-to-minikube.ps1

# VEYA TLS sorunu varsa
.\deploy-offline.ps1

# 2. Database hazırlığı
.\wait-for-mssql.ps1

# 3. Migrations
.\run-migrations.ps1

# 4. API erişimi
.\port-forward.ps1
```

### 🔄 Kod Değişikliği Sonrası

```powershell
# Image rebuild ve restart
.\quick-rebuild.ps1

# Migrations (gerekirse)
.\run-migrations.ps1
```

### 🗄️ Database Sorunları

```powershell
# Database hazır değilse
.\wait-for-mssql.ps1

# Tamamen sıfırlamak için
.\reset-mssql.ps1
```

### 🔍 Debug ve Test

```powershell
# API test
.\port-forward.ps1
# http://localhost:8080/api/v1/docs

# Database erişimi
.\port-forward-mssql.ps1
# SSMS ile localhost,1433
```

---

## ⚙️ Script Ortak Özellikleri

### Renkli Çıktılar
- ✅ Yeşil: Başarılı işlemler
- ⚠️ Sarı: Uyarılar ve beklemeler
- ❌ Kırmızı: Hatalar
- 🔵 Mavi: Bilgilendirme
- 🔷 Gri: Detay bilgiler

### Hata Yönetimi
- `$LASTEXITCODE` kontrolü
- Try-catch blokları
- Timeout mekanizmaları
- Retry logic (bazı script'lerde)

### Kullanıcı Etkileşimi
- Onay soruları (tehlikeli işlemler için)
- İlerleme göstergeleri
- Detaylı açıklamalar
- Sonraki adım önerileri

### Kubectl Entegrasyonu
- Pod durumu kontrolleri
- Deployment yönetimi
- Service bilgileri
- Log görüntüleme

---

## 💡 İpuçları

### PowerShell Execution Policy

Eğer script çalıştırma hatası alırsanız:

```powershell
# Geçici bypass (Önerilen)
powershell -ExecutionPolicy Bypass -File .\script-adi.ps1

# Kalıcı olarak değiştir (Admin gerekli)
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Script Loglarını Kaydetme

```powershell
# Çıktıyı dosyaya kaydet
.\deploy-to-minikube.ps1 | Tee-Object -FilePath deployment.log
```

### Parallel Script Çalıştırma

```powershell
# Terminal 1: Port forward
.\port-forward.ps1

# Terminal 2: MSSQL port forward
.\port-forward-mssql.ps1

# Terminal 3: Komutlar
kubectl get pods
```

### Script Durumu Kontrol

```powershell
# Hangi port-forward'lar aktif?
netstat -ano | findstr "8080 1433"

# Hangi kubectl komutları çalışıyor?
Get-Process kubectl
```

---

## 🔗 İlgili Dosyalar

- **DEPLOYMENT-GUIDE.md** - Detaylı deployment kılavuzu
- **README.md** - Proje genel bakış
- **k8s/** - Kubernetes manifest'leri
- **Dockerfile** - Container image tanımı
- **docker-compose.yml** - Local development stack

---

## 📞 Sorun Giderme

### "Access Denied" Hatası
```powershell
# PowerShell'i Admin olarak çalıştırın
# VEYA
powershell -ExecutionPolicy Bypass -File .\script.ps1
```

### "Kubectl not found" Hatası
```powershell
# kubectl PATH'te mi kontrol et
kubectl version

# Minikube kubectl'i kullan
& "C:\Program Files\Kubernetes\Minikube\minikube.exe" kubectl get pods
```

### "Minikube not found" Hatası
```powershell
# Script'teki minikubePath'i kontrol et
$minikubePath = "C:\Program Files\Kubernetes\Minikube\minikube.exe"
```

---

**Son Güncelleme:** 2026-07-24  
**Proje:** FastAPI Product Management Service on Kubernetes  
**Platform:** Minikube (Windows)
