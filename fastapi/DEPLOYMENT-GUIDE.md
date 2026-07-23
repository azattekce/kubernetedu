# 🚀 Deployment Kılavuzu - Kurumsal Ağlar İçin

Bu proje kurumsal ağlarda (proxy, self-signed sertifikalar) çalışacak şekilde optimize edilmiştir.

## 🔍 Sorun: TLS/SSL Sertifika Hataları

Kurumsal ağlarda yaygın hatalar:
- `certificate verify failed: self-signed certificate in certificate chain`
- `x509: certificate signed by unknown authority`
- `failed to verify certificate`

## ✅ Çözümler

### 🎯 Yöntem 1: Normal Deployment (Önerilen İlk Deneme)

Dockerfile'da pip SSL bypass kullanılıyor:

```powershell
cd c:\zattekce\Kubernets\Edu\fastapi
.\deploy-to-minikube.ps1
```

**Avantajlar:**
- ✅ En hızlı yöntem
- ✅ MCR (Microsoft Container Registry) kullanıyor
- ✅ Pip paketleri için SSL bypass var

**Ne zaman kullanılır:**
- İlk deneme olarak
- MCR'ye erişiminiz varsa

---

### 🔄 Yöntem 2: Offline/Host Build (Garanti Çözüm)

Host makinenizde (Docker Desktop ile) build edip Minikube'a transfer eder:

```powershell
cd c:\zattekce\Kubernets\Edu\fastapi
.\deploy-offline.ps1
```

**Nasıl Çalışır:**
1. ✅ Host makinenizde Docker build (sizin internet bağlantınızı kullanır)
2. ✅ Image'ı tar dosyasına export eder
3. ✅ Tar'ı Minikube içine yükler
4. ✅ Kubernetes deployment'ını yapar

**Avantajlar:**
- ✅ %100 çalışır garanti
- ✅ Minikube'un ağ sorunlarından bağımsız
- ✅ Host makinenizin kurumsal sertifikalarını kullanır

**Gereksinimler:**
- Docker Desktop çalışıyor olmalı
- Host makinenizde internet bağlantısı

---

### 🔧 Yöntem 3: Manuel Kurumsal Sertifika Ekleme

Eğer kalıcı çözüm istiyorsanız:

```powershell
cd c:\zattekce\Kubernets\Edu\fastapi
.\fix-docker-certs.ps1
```

Bu script Windows'taki tüm kurumsal sertifikaları Minikube içine kopyalar.

---

## 📋 Deployment Sonrası

Deployment başarılı olduktan sonra:

### Servis Bilgileri

```powershell
# Servis URL'ini al
minikube service product-service-nodeport --url

# Çıktı örneği:
# http://192.168.49.2:30800
```

### API Endpoints

- **Swagger UI**: `http://<minikube-ip>:30800/api/v1/docs`
- **Health Check**: `http://<minikube-ip>:30800/health`
- **Metrics**: `http://<minikube-ip>:30800/metrics`

### 🌐 Localhost'tan Erişim (Port Forward)

Eğer Minikube IP'sine direkt erişemiyorsanız, port-forward kullanın:

```powershell
# Otomatik script ile
.\port-forward.ps1

# Veya manuel olarak
kubectl port-forward service/product-service 8080:80
```

Artık localhost'tan erişebilirsiniz:
- **Swagger UI**: `http://localhost:8080/api/v1/docs`
- **Health Check**: `http://localhost:8080/health`
- **Metrics**: `http://localhost:8080/metrics`

**Not**: Port forward çalışırken terminal açık kalmalı. CTRL+C ile durdurun.

### Monitoring Komutları

```powershell
# Pod'ları görüntüle
kubectl get pods

# Logları izle
kubectl logs -f deployment/product-service

# HPA durumunu kontrol et
kubectl get hpa

# Dashboard aç
minikube dashboard
```

---

## 🐛 Sorun Giderme

### Build Hataları

#### 1. PyPI SSL Hatası
```
ERROR: Could not fetch URL https://pypi.org/simple/...
```

**Çözüm**: Offline deployment kullanın (`.\deploy-offline.ps1`)

#### 2. Docker Hub SSL Hatası
```
failed to verify certificate: x509: certificate signed by unknown authority
```

**Çözüm**: Dockerfile zaten MCR kullanıyor, offline deployment deneyin

#### 3. MSSQL ODBC Kurulum Hatası
```
apt-key: not found
```

**Çözüm**: Dockerfile güncel GPG yöntemini kullanıyor, script'i tekrar çalıştırın

---

### Runtime Hataları

#### Pod CrashLoopBackOff
```powershell
# Logları kontrol et
kubectl logs -f deployment/product-service

# Yaygın nedenler:
# - Database bağlantı hatası
# - Secret/ConfigMap eksik
# - Health check timeout
```

#### Database Bağlantı Hatası
```powershell
# MSSQL pod'unun çalıştığını kontrol et
kubectl get pods -l app=mssql

# MSSQL loglarını kontrol et
kubectl logs -l app=mssql

# Secret'ın doğru olduğunu kontrol et
kubectl get secret product-service-secret -o yaml
```

---

## 🎓 Deployment Akışı

### Normal Deployment Akışı
```
1. Minikube durumu kontrol
2. Addons aktifleştir (ingress, metrics-server)
3. Minikube Docker env kullan
4. Docker image build (MCR + SSL bypass)
5. Dependencies deploy (MSSQL, Redis)
6. App deploy (ConfigMap, Secret, Deployment, Service, HPA)
7. Health check bekle
8. Service URL göster
```

### Offline Deployment Akışı
```
1. Docker Desktop kontrol
2. Host makinede image build
3. Image'ı tar'a export
4. Tar'ı Minikube'a load
5. Dependencies deploy (MSSQL, Redis)
6. App deploy
7. Health check bekle
8. Service URL göster
```

---

## 📊 Yapılandırma Dosyaları

### Ortam Değişkenleri

`.env` dosyası kullanılmaz, ConfigMap ve Secret kullanılır:

**ConfigMap** (`k8s/base/configmap.yaml`):
- `DATABASE_HOST`: MSSQL service FQDN
- `REDIS_HOST`: Redis service FQDN
- Non-sensitive ayarlar

**Secret** (`k8s/base/secret.yaml`):
- `DATABASE_PASSWORD`: MSSQL şifresi (base64)
- `JWT_SECRET_KEY`: JWT signing key (base64)
- Sensitive ayarlar

---

## 🔐 Güvenlik

### Secret Değerlerini Değiştirme

```powershell
# Base64 encode
$password = "YourStrongPassword123!"
$bytes = [System.Text.Encoding]::UTF8.GetBytes($password)
$encoded = [Convert]::ToBase64String($bytes)
Write-Host $encoded

# Secret YAML'ı güncelle
# kubectl apply -f k8s/base/secret.yaml
```

### Production Notları

⚠️ **Bu deployment local/dev içindir!** Production için:

1. ✅ Secret'ları Azure Key Vault'a taşıyın
2. ✅ External database kullanın (Azure SQL)
3. ✅ Redis için Azure Cache kullanın
4. ✅ Ingress TLS sertifikası ekleyin
5. ✅ Resource limits artırın
6. ✅ Replica sayısını artırın (min 3)
7. ✅ Network policies ekleyin

---

## 📞 Yardım

Deployment sırasında sorun yaşarsanız:

1. ✅ Bu dosyayı okuyun
2. ✅ Logları kontrol edin (`kubectl logs`)
3. ✅ Offline deployment deneyin
4. ✅ Minikube'u yeniden başlatın (`minikube delete && minikube start`)

Happy deploying! 🚀
