# 🚀 Minikube Deployment Guide

## Minikube Hazırlık Adımları

### 1. Minikube Başlatma

```powershell
# Minikube'u başlat (8GB RAM, 4 CPU önerilir)
minikube start --cpus=4 --memory=8192 --driver=docker

# Minikube durumunu kontrol et
minikube status

# Kubectl context'i kontrol et
kubectl config current-context  # minikube olmalı
```

### 2. Gerekli Addon'ları Aktifleştir

```powershell
# Ingress controller aktifleştir
minikube addons enable ingress

# Metrics server aktifleştir (HPA için gerekli)
minikube addons enable metrics-server

# Dashboard (opsiyonel)
minikube addons enable dashboard

# Addon'ları kontrol et
minikube addons list
```

### 3. Docker Image'ı Minikube'a Yükleme

**Önemli:** Minikube kendi Docker daemon'ını kullanır. İki seçenek var:

#### Seçenek A: Minikube Docker Daemon'ını Kullan (Önerilen)

```powershell
# Minikube Docker environment'ını kullan
minikube docker-env | Invoke-Expression

# Şimdi Docker build yapınca direkt minikube'a gider
docker build -t product-service:latest .

# Image'ların minikube'da olduğunu kontrol et
minikube ssh
docker images | grep product-service
exit
```

#### Seçenek B: Image'ı Minikube'a Yükle

```powershell
# Önce normal build yap
docker build -t product-service:latest .

# Image'ı minikube'a yükle
minikube image load product-service:latest

# Kontrol et
minikube image ls | grep product-service
```

### 4. MSSQL ve Redis için Local Deployment

Minikube'da MSSQL ve Redis'i de deploy etmemiz gerekiyor:

```powershell
# MSSQL Server deployment
kubectl apply -f k8s/dependencies/mssql-deployment.yaml

# Redis deployment
kubectl apply -f k8s/dependencies/redis-deployment.yaml

# Kontrol et
kubectl get pods
```

### 5. ConfigMap ve Secret Oluştur

```powershell
# ConfigMap'i minikube için güncellenmiş versiyonla apply et
kubectl apply -f k8s/base/configmap.yaml

# Secret'ı apply et (production'da external secret manager kullan!)
kubectl apply -f k8s/base/secret.yaml

# Kontrol et
kubectl get configmap
kubectl get secret
```

### 6. Product Service Deploy Et

```powershell
# Deployment
kubectl apply -f k8s/base/deployment.yaml

# Service
kubectl apply -f k8s/base/service.yaml

# HPA (Horizontal Pod Autoscaler)
kubectl apply -f k8s/hpa.yaml

# Deployment durumunu izle
kubectl get pods -w
```

### 7. Service'e Erişim

Minikube'da 3 farklı erişim yöntemi var:

#### A. NodePort ile Erişim

```powershell
# Service URL'ini al
minikube service product-service-nodeport --url

# Örnek çıktı: http://192.168.49.2:30800
# Bu URL'den API'ye erişebilirsiniz
```

#### B. Port Forwarding

```powershell
# Port forward başlat
kubectl port-forward service/product-service 8000:80

# Şimdi http://localhost:8000 üzerinden erişebilirsiniz
```

#### C. Ingress ile Erişim (Önerilen)

```powershell
# Ingress apply et
kubectl apply -f k8s/base/ingress.yaml

# Minikube IP'sini al
minikube ip

# Hosts dosyasına ekle (Admin PowerShell gerekli)
# Windows: C:\Windows\System32\drivers\etc\hosts
# Örnek: 192.168.49.2 api.yourdomain.com
Add-Content -Path C:\Windows\System32\drivers\etc\hosts -Value "`n$(minikube ip) api.yourdomain.com"

# Şimdi http://api.yourdomain.com üzerinden erişebilirsiniz
```

### 8. API Test Et

```powershell
# Health check
curl http://$(minikube service product-service-nodeport --url)/health

# Veya browser'dan:
# http://$(minikube service product-service-nodeport --url)/api/v1/docs
```

### 9. Monitoring

```powershell
# Dashboard aç
minikube dashboard

# Pod logları
kubectl logs -f deployment/product-service

# Pod'a bağlan
kubectl exec -it deployment/product-service -- /bin/bash

# Metrics kontrol et
kubectl top pods
kubectl top nodes
```

## Minikube'a Özel Notlar

### 1. Image Pull Policy

Minikube'da local image kullanırken `imagePullPolicy: Never` veya `IfNotPresent` kullanın:

```yaml
# k8s/base/deployment.yaml içinde
spec:
  containers:
    - name: product-service
      image: product-service:latest
      imagePullPolicy: IfNotPresent  # Veya Never
```

### 2. Resource Limits

Minikube local olduğu için daha düşük resource limitleri kullanabilirsiniz:

```yaml
resources:
  requests:
    cpu: "100m"
    memory: "128Mi"
  limits:
    cpu: "500m"
    memory: "256Mi"
```

### 3. External Services

LoadBalancer yerine NodePort kullanın (zaten service.yaml'da var).

### 4. Persistent Volumes

Minikube otomatik olarak local storage sağlar, ekstra yapılandırma gerekmez.

## Tam Deployment Script

Tüm adımları otomatikleştirmek için:

```powershell
# deploy-to-minikube.ps1

Write-Host "🚀 Minikube'a Deployment Başlıyor..." -ForegroundColor Green

# 1. Minikube durumunu kontrol et
Write-Host "`n1. Minikube durumu kontrol ediliyor..." -ForegroundColor Yellow
minikube status

# 2. Addon'ları aktifleştir
Write-Host "`n2. Gerekli addon'lar aktifleştiriliyor..." -ForegroundColor Yellow
minikube addons enable ingress
minikube addons enable metrics-server

# 3. Docker image build et
Write-Host "`n3. Docker image build ediliyor..." -ForegroundColor Yellow
minikube docker-env | Invoke-Expression
docker build -t product-service:latest .

# 4. Dependencies deploy et
Write-Host "`n4. MSSQL ve Redis deploy ediliyor..." -ForegroundColor Yellow
kubectl apply -f k8s/dependencies/

# 5. ConfigMap ve Secret
Write-Host "`n5. ConfigMap ve Secret oluşturuluyor..." -ForegroundColor Yellow
kubectl apply -f k8s/base/configmap.yaml
kubectl apply -f k8s/base/secret.yaml

# 6. Product Service
Write-Host "`n6. Product Service deploy ediliyor..." -ForegroundColor Yellow
kubectl apply -f k8s/base/deployment.yaml
kubectl apply -f k8s/base/service.yaml
kubectl apply -f k8s/hpa.yaml

# 7. Deployment tamamlanmasını bekle
Write-Host "`n7. Deployment tamamlanması bekleniyor..." -ForegroundColor Yellow
kubectl wait --for=condition=available --timeout=300s deployment/product-service

# 8. Service URL'ini göster
Write-Host "`n✅ Deployment tamamlandı!" -ForegroundColor Green
Write-Host "`nService URL:" -ForegroundColor Cyan
minikube service product-service-nodeport --url

Write-Host "`nAPI Docs:" -ForegroundColor Cyan
Write-Host "$(minikube service product-service-nodeport --url)/api/v1/docs"

Write-Host "`nPod durumu:" -ForegroundColor Cyan
kubectl get pods

Write-Host "`n📊 Dashboard'u açmak için: minikube dashboard" -ForegroundColor Magenta
```

## Temizlik (Cleanup)

```powershell
# Tüm kaynakları sil
kubectl delete -f k8s/base/
kubectl delete -f k8s/dependencies/
kubectl delete -f k8s/hpa.yaml

# Veya namespace bazlı temizlik
kubectl delete namespace default

# Minikube'u durdur
minikube stop

# Minikube'u tamamen sil
minikube delete
```

## Troubleshooting

### Image Pull Hatası

```powershell
# Image'ın minikube'da olduğunu kontrol et
minikube ssh
docker images
exit

# Image tekrar yükle
minikube image load product-service:latest
```

### Pod CrashLoopBackOff

```powershell
# Pod loglarını kontrol et
kubectl logs deployment/product-service

# Pod detaylarını kontrol et
kubectl describe pod <pod-name>

# Database connection kontrol et
kubectl get pods | grep mssql
kubectl logs <mssql-pod-name>
```

### HPA Çalışmıyor

```powershell
# Metrics server kontrol et
kubectl top nodes
kubectl top pods

# Metrics server yoksa:
minikube addons enable metrics-server
```

## Performans Optimizasyonu

```powershell
# Minikube'a daha fazla kaynak ver
minikube stop
minikube start --cpus=6 --memory=16384 --disk-size=50g

# Docker cache temizle
minikube ssh
docker system prune -a
exit
```

---

**Sonraki Adım**: `deploy-to-minikube.ps1` scriptini çalıştırın! 🚀
