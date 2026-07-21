# WordPress Kubernetes Deployment

Bu klasör, Kubernetes üzerinde WordPress uygulaması çalıştırmak için gerekli tüm YAML dosyalarını içerir.

## 📁 Dosya Yapısı

```
Demo/
├── mysql-secret.yml           # MySQL parolaları
├── mysql-pvc.yml             # MySQL için PersistentVolumeClaim
├── mysql-deployment.yml      # MySQL Deployment
├── mysql-service.yml         # MySQL Service (ClusterIP)
├── wordpress-pvc.yml         # WordPress için PersistentVolumeClaim
├── wordpress-deployment.yml  # WordPress Deployment
├── wordpress-service.yml     # WordPress Service (NodePort)
└── wordpress-complete.yml    # Tüm bileşenler tek dosyada
```

## 🏗️ Mimari Yapı

```
┌─────────────────────────────────────────┐
│         Internet / Kullanıcı            │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│   WordPress Service (NodePort:30080)    │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│   WordPress Deployment (2 replicas)     │
│   ┌─────────────┐  ┌─────────────┐     │
│   │ WordPress   │  │ WordPress   │     │
│   │   Pod 1     │  │   Pod 2     │     │
│   └─────────────┘  └─────────────┘     │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│    MySQL Service (ClusterIP:3306)       │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│      MySQL Deployment (1 replica)       │
│           ┌─────────────┐               │
│           │   MySQL     │               │
│           │    Pod      │               │
│           └─────────────┘               │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│        PersistentVolumes                │
│  ┌────────────┐    ┌────────────┐      │
│  │ MySQL PV   │    │WordPress PV│      │
│  │   (5Gi)    │    │   (5Gi)    │      │
│  └────────────┘    └────────────┘      │
└─────────────────────────────────────────┘
```

## 🚀 Deployment Seçenekleri

### Seçenek 1: Ayrı Dosyalarla Deployment (Önerilen)

```powershell
# 1. MySQL bileşenlerini deploy et
kubectl apply -f mysql-secret.yml
kubectl apply -f mysql-pvc.yml
kubectl apply -f mysql-service.yml
kubectl apply -f mysql-deployment.yml

# 2. MySQL'in hazır olmasını bekle
kubectl wait --for=condition=ready pod -l tier=mysql --timeout=300s

# 3. WordPress bileşenlerini deploy et
kubectl apply -f wordpress-pvc.yml
kubectl apply -f wordpress-service.yml
kubectl apply -f wordpress-deployment.yml

# 4. WordPress'in hazır olmasını bekle
kubectl wait --for=condition=ready pod -l tier=frontend --timeout=300s
```

### Seçenek 2: Tek Dosyayla Deployment (Hızlı)

```powershell
# Tüm bileşenleri tek seferde deploy et
kubectl apply -f wordpress-complete.yml

# Podların hazır olmasını bekle
kubectl wait --for=condition=ready pod -l app=wordpress --timeout=300s
```

## 📊 Deployment Sonrası Kontroller

### 1. Tüm Kaynakları Kontrol Et

```powershell
# Tüm WordPress kaynaklarını görüntüle
kubectl get all -l app=wordpress

# PersistentVolumeClaim'leri kontrol et
kubectl get pvc

# Secret'ı kontrol et
kubectl get secret mysql-secret
```

### 2. Pod Durumlarını İzle

```powershell
# Podları izle
kubectl get pods -l app=wordpress -w

# Detaylı pod bilgisi
kubectl describe pod -l app=wordpress
```

### 3. Log'ları İncele

```powershell
# MySQL logları
kubectl logs -l tier=mysql

# WordPress logları
kubectl logs -l tier=frontend

# Belirli bir pod'un logları
kubectl logs deployment/wordpress
```

## 🌐 Uygulamaya Erişim

### Minikube Kullanıyorsanız:

```powershell
# Service URL'ini al
minikube service wordpress --url

# Veya tarayıcıda aç
minikube service wordpress
```

### Standard Kubernetes Cluster:

```powershell
# Node IP adresini al
kubectl get nodes -o wide

# Service port'unu kontrol et
kubectl get svc wordpress

# Tarayıcıda aç: http://<NODE-IP>:30080
```

### Port Forward ile Lokal Erişim:

```powershell
# Port forwarding ile erişim
kubectl port-forward svc/wordpress 8080:80

# Tarayıcıda aç: http://localhost:8080
```

## ⚙️ Yapılandırma Detayları

### MySQL Konfigürasyonu

- **Image**: mysql:8.0
- **Replicas**: 1
- **Storage**: 5Gi
- **Port**: 3306 (ClusterIP)
- **Database**: wordpress
- **User**: wordpress
- **Password**: wordpress123 (Secret'ta saklanır)

### WordPress Konfigürasyonu

- **Image**: wordpress:latest
- **Replicas**: 2
- **Storage**: 5Gi
- **Port**: 80 → NodePort 30080
- **Health Checks**: Liveness ve Readiness probe'ları aktif

## 🔒 Güvenlik Notları

### Secret Değiştirme

Varsayılan parolayı değiştirmek için:

```powershell
# Yeni parola oluştur (base64 encoded)
echo -n 'yeni_guclu_parola' | base64

# mysql-secret.yml dosyasını güncelle
# mysql-root-password ve mysql-password değerlerini değiştir

# Secret'ı güncelle
kubectl delete secret mysql-secret
kubectl apply -f mysql-secret.yml

# Podları yeniden başlat
kubectl rollout restart deployment/mysql
kubectl rollout restart deployment/wordpress
```

## 🔄 Güncelleme ve Bakım

### WordPress Güncelleme

```powershell
# Yeni versiyon belirt
kubectl set image deployment/wordpress wordpress=wordpress:6.4

# Rollout durumunu izle
kubectl rollout status deployment/wordpress

# Geri alma (gerekirse)
kubectl rollout undo deployment/wordpress
```

### Ölçeklendirme

```powershell
# WordPress replica sayısını artır
kubectl scale deployment wordpress --replicas=3

# Otomatik ölçeklendirme (HPA)
kubectl autoscale deployment wordpress --cpu-percent=70 --min=2 --max=5
```

## 🧹 Temizlik (Cleanup)

### Tüm Kaynakları Sil

```powershell
# Ayrı dosyalar kullandıysanız
kubectl delete -f wordpress-deployment.yml
kubectl delete -f wordpress-service.yml
kubectl delete -f wordpress-pvc.yml
kubectl delete -f mysql-deployment.yml
kubectl delete -f mysql-service.yml
kubectl delete -f mysql-pvc.yml
kubectl delete -f mysql-secret.yml

# Veya tek dosya kullandıysanız
kubectl delete -f wordpress-complete.yml

# PersistentVolume'ları da sil (dikkat: veri kaybı!)
kubectl delete pvc --all
```

### Sadece Deployment'ları Sil (Veriyi Koru)

```powershell
kubectl delete deployment wordpress mysql
kubectl delete service wordpress mysql
# PVC ve Secret korunur
```

## 🐛 Sorun Giderme

### Problem: TLS Certificate Hatası (Image Pull Error)

**Hata**: `Failed to pull image "mysql:8.0": tls: failed to verify certificate`

**Çözüm 1 - Local Image Yükleme (Önerilen)**:
```powershell
# Image'leri local'e çek
docker pull mysql:8.0
docker pull wordpress:latest

# Minikube'a aktar
minikube image load mysql:8.0
minikube image load wordpress:latest

# Deployment'ı tekrar dene (imagePullPolicy: IfNotPresent eklendi)
kubectl apply -f mysql-deployment.yml -n wordpress-ns
```

**Çözüm 2 - Microsoft Container Registry**:
```powershell
# MCR mirror'ını kullan
kubectl apply -f mysql-deployment-mcr.yml -n wordpress-ns
```

**Çözüm 3 - Minikube İnsecure Registry**:
```powershell
minikube stop
minikube start --insecure-registry="registry-1.docker.io"
```

### Problem: Podlar başlamıyor

```powershell
# Pod durumunu kontrol et
kubectl describe pod <pod-name>

# Events'leri incele
kubectl get events --sort-by='.lastTimestamp'

# Resource kullanımını kontrol et
kubectl top pods
```

### Problem: WordPress MySQL'e bağlanamıyor

```powershell
# MySQL service'in çalıştığını kontrol et
kubectl get svc mysql

# MySQL pod loglarını incele
kubectl logs -l tier=mysql

# DNS çözümlemesini test et
kubectl run -it --rm debug --image=busybox --restart=Never -- nslookup mysql
```

### Problem: PVC pending durumunda

```powershell
# PVC durumunu kontrol et
kubectl describe pvc mysql-pvc
kubectl describe pvc wordpress-pvc

# StorageClass'ları kontrol et
kubectl get storageclass

# Minikube için: storage addon'unu etkinleştir
minikube addons enable storage-provisioner
```

## 📝 En İyi Uygulamalar

1. **Üretim Ortamı İçin**:
   - Secret'ları güçlü parolalarla güncelleyin
   - Resource limits'leri workload'a göre ayarlayın
   - Ingress ekleyerek HTTPS kullanın
   - Backup stratejisi oluşturun

2. **Performans**:
   - WordPress için Redis cache ekleyin
   - CDN kullanın
   - MySQL için tuning yapın

3. **Yüksek Erişilebilirlik**:
   - Multi-zone deployment kullanın
   - Pod Disruption Budget ekleyin
   - Monitoring ve alerting kurun

## 📚 Kaynaklar

- [WordPress Docker Image](https://hub.docker.com/_/wordpress)
- [MySQL Docker Image](https://hub.docker.com/_/mysql)
- [Kubernetes Persistent Volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)
- [Kubernetes Secrets](https://kubernetes.io/docs/concepts/configuration/secret/)
