# WordPress YAML Dosyaları - Hızlı Referans

## 📋 Dosya Listesi ve Kullanım Alanları

| Dosya | Kaynak Türü | Kullanım | Öncelik |
|-------|-------------|----------|---------|
| `wordpress-pvc.yaml` | PersistentVolumeClaim | Kalıcı depolama | 1️⃣ İlk |
| `wordpress-service.yaml` | Service | Dış erişim (NodePort) | 2️⃣ İkinci |
| `wordpress-deployment.yaml` | Deployment | Uygulama pod'ları | 3️⃣ Üçüncü |
| `wordpress-complete.yaml` | Hepsi | Tek dosyada tümü | ⚡ Hızlı |

---

## 1️⃣ wordpress-pvc.yaml

### Ne İşe Yarar?
WordPress'in dosyalarını (temalar, eklentiler, yüklemeler) saklamak için kalıcı depolama alanı ister.

### İçerik
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: wp-pv-claim       # PVC adı
  namespace: wp           # Namespace
  labels:
    app: wordpress
    tier: frontend
spec:
  accessModes:
    - ReadWriteOnce       # Tek node'da okuma-yazma
  resources:
    requests:
      storage: 10Gi       # İstenen depolama: 10 GB
```

### Önemli Parametreler

| Parametre | Değer | Açıklama |
|-----------|-------|----------|
| `accessModes` | ReadWriteOnce | Aynı anda tek bir node mount edebilir |
| `storage` | 10Gi | WordPress için 10 GB alan |
| `name` | wp-pv-claim | Deployment'ta bu isimle referans verilir |

### Access Modes

- **ReadWriteOnce (RWO)**: Tek node okuma-yazma ✅ Kullanılan
- **ReadOnlyMany (ROX)**: Çoklu node sadece okuma
- **ReadWriteMany (RWX)**: Çoklu node okuma-yazma

### Komutlar

```powershell
# Oluştur
kubectl apply -f wordpress-pvc.yaml

# Kontrol et
kubectl get pvc -n wp
kubectl describe pvc wp-pv-claim -n wp

# Durumu
# STATUS sütununda "Bound" olmalı

# Sil
kubectl delete -f wordpress-pvc.yaml
# ⚠️ Dikkat: Veri kalıcı olarak silinir!
```

### Sorun Giderme

**Problem**: PVC "Pending" durumunda
```powershell
# Nedeni kontrol et
kubectl describe pvc wp-pv-claim -n wp

# Çözümler:
# 1. Cluster'da PV (PersistentVolume) var mı?
kubectl get pv

# 2. StorageClass var mı?
kubectl get storageclass

# 3. Minikube'de addon gerekebilir
minikube addons enable storage-provisioner
```

---

## 2️⃣ wordpress-service.yaml

### Ne İşe Yarar?
WordPress pod'larına dışarıdan erişim sağlar. Trafiği pod'lara yönlendirir.

### İçerik
```yaml
apiVersion: v1
kind: Service
metadata:
  name: wordpress         # Service adı
  namespace: wp
  labels:
    app: wordpress
    tier: frontend
spec:
  type: NodePort          # Dış erişim tipi
  ports:
  - port: 80              # Service port
    targetPort: 80        # Container port
    protocol: TCP
    nodePort: 30080       # Node üzerindeki port
  selector:               # Hangi pod'lara yönlendirsin?
    app: wordpress
    tier: frontend
```

### Önemli Parametreler

| Parametre | Değer | Açıklama |
|-----------|-------|----------|
| `type` | NodePort | Node IP üzerinden dış erişim |
| `port` | 80 | Service içindeki port |
| `targetPort` | 80 | Container'ın dinlediği port |
| `nodePort` | 30080 | Node'da açılan port (30000-32767) |
| `selector` | app:wordpress | Bu label'lı pod'lara yönlendir |

### Service Türleri

1. **ClusterIP** (Default)
   - Sadece cluster içinden erişim
   - Dış erişim yok
   ```yaml
   type: ClusterIP
   ```

2. **NodePort** ✅ Kullanılan
   - Node IP:Port ile dış erişim
   - Port range: 30000-32767
   ```yaml
   type: NodePort
   nodePort: 30080
   ```

3. **LoadBalancer**
   - Cloud provider'ın LB'si
   - AWS/Azure/GCP'de otomatik external IP
   ```yaml
   type: LoadBalancer
   ```

4. **ExternalName**
   - DNS CNAME mapping
   - Dış servislere alias

### Komutlar

```powershell
# Oluştur
kubectl apply -f wordpress-service.yaml

# Kontrol et
kubectl get service wordpress -n wp
kubectl get svc wordpress -n wp  # Kısa hali

# Detaylı bilgi
kubectl describe service wordpress -n wp

# Endpoint'leri gör (hangi pod'lara yönlendiriyor)
kubectl get endpoints wordpress -n wp

# Minikube'de URL al
minikube service wordpress -n wp --url

# Port-forward (test için)
kubectl port-forward -n wp service/wordpress 8080:80
# Tarayıcı: http://localhost:8080

# Sil
kubectl delete -f wordpress-service.yaml
```

### Erişim Örnekleri

```powershell
# 1. NodePort ile
# Cluster node IP'sini al
kubectl get nodes -o wide
# Tarayıcı: http://<NODE-IP>:30080

# 2. Minikube
minikube service wordpress -n wp

# 3. Port Forward
kubectl port-forward -n wp svc/wordpress 8080:80
# Tarayıcı: http://localhost:8080

# 4. Cluster içinden (başka pod'dan)
kubectl run -it --rm test --image=busybox -n wp -- wget -qO- http://wordpress
```

### Sorun Giderme

**Problem**: Endpoint'ler boş
```powershell
kubectl get endpoints wordpress -n wp
# ENDPOINTS sütunu boşsa:

# 1. Pod'lar çalışıyor mu?
kubectl get pods -n wp -l app=wordpress

# 2. Pod'ların label'ları doğru mu?
kubectl get pods -n wp --show-labels

# 3. Pod'lar Ready durumunda mı?
kubectl get pods -n wp
```

**Problem**: Service'e erişilemiyor
```powershell
# 1. Service var mı?
kubectl get svc wordpress -n wp

# 2. Port forward ile test
kubectl port-forward -n wp svc/wordpress 8080:80
curl http://localhost:8080

# 3. DNS çözümü (cluster içinden)
kubectl run -it --rm debug --image=busybox -n wp -- nslookup wordpress
```

---

## 3️⃣ wordpress-deployment.yaml

### Ne İşe Yarar?
WordPress uygulamasını çalıştıran pod'ları oluşturur ve yönetir. Replica, güncelleme stratejisi, sağlık kontrolleri içerir.

### İçerik Yapısı

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: wordpress
  namespace: wp
spec:
  replicas: 2                    # Çalışacak pod sayısı
  selector:                      # Hangi pod'ları yönetsin
    matchLabels:
      app: wordpress
      tier: frontend
  strategy:                      # Güncelleme stratejisi
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:                      # Pod şablonu
    metadata:
      labels:                    # Pod label'ları
        app: wordpress
        tier: frontend
    spec:
      containers:
      - name: wordpress
        image: wordpress:latest
        # ... (detaylar aşağıda)
```

### 📦 Container Konfigürasyonu

#### Image ve Pull Policy

```yaml
image: wordpress:latest
imagePullPolicy: IfNotPresent
```

| Policy | Davranış |
|--------|----------|
| `IfNotPresent` ✅ | Yoksa çek, varsa kullan |
| `Always` | Her zaman en son sürümü çek |
| `Never` | Hiç çekme, local'de olmalı |

#### Environment Variables (MySQL Bağlantısı)

```yaml
env:
- name: WORDPRESS_DB_HOST
  value: wordpress-mysql:3306    # MySQL service:port

- name: WORDPRESS_DB_NAME
  value: wp_db                   # Database adı

- name: WORDPRESS_DB_USER
  value: burak                   # DB kullanıcısı

- name: WORDPRESS_DB_PASSWORD
  valueFrom:                     # Secret'tan al
    secretKeyRef:
      name: mysql-pass           # Secret adı
      key: password              # Secret key
```

**Secret Kontrolü:**
```powershell
# Secret var mı?
kubectl get secret mysql-pass -n wp

# Secret yoksa oluştur:
kubectl create secret generic mysql-pass -n wp --from-literal=password=admin
```

#### Ports

```yaml
ports:
- containerPort: 80              # Container'ın dinlediği port
  name: wordpress                # Port adı (opsiyonel)
```

#### Volume Mounts

```yaml
volumeMounts:
- name: wordpress-persistent-storage
  mountPath: /var/www/html       # WordPress dosyaları

volumes:
- name: wordpress-persistent-storage
  persistentVolumeClaim:
    claimName: wp-pv-claim       # PVC referansı
```

**Kontrol:**
```powershell
# Volume mount edilmiş mi?
kubectl exec -it -n wp <pod-name> -- df -h | grep /var/www/html

# Dosyalar var mı?
kubectl exec -it -n wp <pod-name> -- ls -la /var/www/html
```

### ⚙️ Resource Management

```yaml
resources:
  requests:                      # Minimum garanti
    memory: "256Mi"
    cpu: "250m"                  # 0.25 core
  limits:                        # Maximum limit
    memory: "512Mi"
    cpu: "500m"                  # 0.5 core
```

**CPU Birimleri:**
- `1000m` = 1 CPU core
- `500m` = 0.5 CPU core
- `250m` = 0.25 CPU core

**Memory Birimleri:**
- `256Mi` = 256 Mebibyte
- `512Mi` = 512 Mebibyte
- `1Gi` = 1 Gibibyte

**Kaynak İzleme:**
```powershell
# Pod kaynak kullanımı
kubectl top pods -n wp

# Node kaynak kullanımı
kubectl top nodes

# Detaylı kaynak bilgisi
kubectl describe pod <pod-name> -n wp | grep -A 10 "Requests\|Limits"
```

### 🏥 Health Checks (Probes)

#### Liveness Probe (Canlılık)

```yaml
livenessProbe:
  httpGet:
    path: /                      # Kontrol URL'i
    port: 80
  initialDelaySeconds: 60        # İlk kontrol: 60 saniye sonra
  periodSeconds: 10              # Her 10 saniyede kontrol
  timeoutSeconds: 5              # 5 saniye timeout
  failureThreshold: 3            # 3 başarısız denemeden sonra restart
```

**Ne Yapar?**
- Uygulama canlı mı kontrol eder
- Başarısız olursa pod'u yeniden başlatır
- Donmuş uygulamaları yakalar

#### Readiness Probe (Hazırlık)

```yaml
readinessProbe:
  httpGet:
    path: /
    port: 80
  initialDelaySeconds: 30        # İlk kontrol: 30 saniye sonra
  periodSeconds: 5               # Her 5 saniyede kontrol
  timeoutSeconds: 3              # 3 saniye timeout
  failureThreshold: 3            # 3 başarısız denemeden sonra NotReady
```

**Ne Yapar?**
- Uygulama trafiği kabul edebilir mi kontrol eder
- Başarısız olursa pod'a trafik gönderilmez (restart edilmez)
- Service'den çıkarılır

#### Probe Türleri

| Tip | Kullanım |
|-----|----------|
| `httpGet` ✅ | HTTP GET request (200-399 başarılı) |
| `tcpSocket` | TCP port kontrolü |
| `exec` | Container içinde komut çalıştır |

**Örnek TCP Probe:**
```yaml
livenessProbe:
  tcpSocket:
    port: 80
  initialDelaySeconds: 30
```

**Örnek Exec Probe:**
```yaml
livenessProbe:
  exec:
    command:
    - cat
    - /var/www/html/index.php
  initialDelaySeconds: 30
```

**Kontrol:**
```powershell
# Pod'un Ready durumu
kubectl get pods -n wp

# Probe sonuçları
kubectl describe pod <pod-name> -n wp | grep -A 5 "Liveness\|Readiness"

# Events'lerde probe hatalarını ara
kubectl get events -n wp | grep -i probe
```

### 🔄 Deployment Strategy (Güncelleme Stratejisi)

#### Rolling Update (Kullanılan)

```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1                  # Aynı anda 1 fazla pod olabilir
    maxUnavailable: 0            # Hiç pod down olmaz
```

**Nasıl Çalışır?**
1. Yeni pod başlatılır (maxSurge: 1)
2. Yeni pod Ready olur
3. Eski pod kapatılır
4. Süreç tekrarlanır
5. ✅ Sıfır kesinti!

**Örnek Senaryolar:**

| replicas | maxSurge | maxUnavailable | Maksimum Pod | Minimum Pod |
|----------|----------|----------------|--------------|-------------|
| 2 | 1 | 0 | 3 | 2 |
| 2 | 0 | 1 | 2 | 1 |
| 3 | 1 | 1 | 4 | 2 |

**Güncelleme Komutları:**
```powershell
# Image güncelle
kubectl set image deployment/wordpress -n wp wordpress=wordpress:6.4

# YAML'dan güncelle
kubectl apply -f wordpress-deployment.yaml

# Rollout durumunu izle
kubectl rollout status deployment/wordpress -n wp

# Güncelleme duraklatma
kubectl rollout pause deployment/wordpress -n wp

# Güncelleme devam ettirme
kubectl rollout resume deployment/wordpress -n wp

# Geri alma (rollback)
kubectl rollout undo deployment/wordpress -n wp

# Belirli revision'a geri dön
kubectl rollout undo deployment/wordpress -n wp --to-revision=2

# Güncelleme geçmişi
kubectl rollout history deployment/wordpress -n wp

# Belirli revision detayı
kubectl rollout history deployment/wordpress -n wp --revision=2
```

#### Recreate Strategy

```yaml
strategy:
  type: Recreate
```

**Nasıl Çalışır?**
1. Tüm eski pod'lar kapatılır
2. Yeni pod'lar başlatılır
3. ⚠️ Kesinti olur!

**Ne Zaman Kullanılır?**
- Veritabanı migration gerekiyorsa
- Aynı anda birden fazla versiyon çalışmamalıysa

### 🎯 Replica Management

```yaml
replicas: 2                      # 2 pod çalıştır
```

**Replica Sayısını Değiştirme:**
```powershell
# Scale komutu ile
kubectl scale deployment wordpress -n wp --replicas=3

# YAML'ı düzenleyip apply
kubectl apply -f wordpress-deployment.yaml

# Auto-scaling (HPA)
kubectl autoscale deployment wordpress -n wp --min=2 --max=5 --cpu-percent=80
```

**Replica Kontrolü:**
```powershell
# Deployment bilgisi
kubectl get deployment wordpress -n wp
# READY: 2/2 olmalı (2/3 gibi değerler sorun işareti)

# Pod'ları listele
kubectl get pods -n wp -l app=wordpress

# ReplicaSet'leri gör
kubectl get replicaset -n wp
```

### 🚀 Komutlar

#### Oluşturma ve Silme

```powershell
# Deployment oluştur
kubectl apply -f wordpress-deployment.yaml

# Deployment'ı sil
kubectl delete -f wordpress-deployment.yaml

# Sadece pod'ları sil (yeniden oluşturulur)
kubectl delete pods -n wp -l app=wordpress
```

#### İzleme ve Debug

```powershell
# Deployment durumu
kubectl get deployment wordpress -n wp
kubectl describe deployment wordpress -n wp

# Pod'ları izle
kubectl get pods -n wp -l app=wordpress -w

# Log görüntüle
kubectl logs -n wp deployment/wordpress
kubectl logs -n wp deployment/wordpress -f          # Follow
kubectl logs -n wp deployment/wordpress --tail=100  # Son 100 satır

# Pod'a giriş
kubectl exec -it -n wp <pod-name> -- bash

# Çoklu pod'dan log
kubectl logs -n wp -l app=wordpress --all-containers=true
```

#### Güncelleme ve Rollback

```powershell
# Image değiştir
kubectl set image deployment/wordpress -n wp wordpress=wordpress:6.4

# Env variable değiştir
kubectl set env deployment/wordpress -n wp WORDPRESS_DEBUG=true

# Replica değiştir
kubectl scale deployment wordpress -n wp --replicas=3

# Rollback
kubectl rollout undo deployment/wordpress -n wp
```

### 🐛 Sorun Giderme

**Problem: Pod başlamıyor (CrashLoopBackOff)**

```powershell
# 1. Log kontrol
kubectl logs -n wp <pod-name>
kubectl logs -n wp <pod-name> --previous  # Önceki çalışma

# 2. Describe ile detay
kubectl describe pod <pod-name> -n wp

# 3. Events kontrol
kubectl get events -n wp --sort-by='.lastTimestamp' | grep <pod-name>

# Yaygın nedenler:
# - MySQL bağlantı hatası
# - Secret bulunamadı
# - PVC mount edilemedi
# - Resource limitleri çok düşük
```

**Problem: ImagePullBackOff**

```powershell
kubectl describe pod <pod-name> -n wp

# Çözümler:
# 1. Image adı doğru mu?
# 2. Registry erişimi var mı?
# 3. Image tag mevcut mu?

# Image pull secret gerekiyorsa:
kubectl create secret docker-registry regcred \
  --docker-server=<registry> \
  --docker-username=<user> \
  --docker-password=<pass>
```

**Problem: MySQL bağlantı hatası**

```powershell
# 1. MySQL service çalışıyor mu?
kubectl get svc -n wp | grep mysql

# 2. Environment variables doğru mu?
kubectl exec -it -n wp <pod-name> -- env | grep WORDPRESS_DB

# 3. Secret var mı?
kubectl get secret mysql-pass -n wp

# 4. MySQL'e manuel bağlan
kubectl exec -it -n wp <pod-name> -- bash
apt-get update && apt-get install -y default-mysql-client
mysql -h wordpress-mysql -u burak -padmin wp_db
```

**Problem: PVC mount edilemiyor**

```powershell
# 1. PVC durumu
kubectl get pvc wp-pv-claim -n wp
# STATUS: Bound olmalı

# 2. PVC events
kubectl describe pvc wp-pv-claim -n wp

# 3. Pod events
kubectl describe pod <pod-name> -n wp | grep -i volume
```

---

## 4️⃣ wordpress-complete.yaml

### Ne İşe Yarar?
PVC, Service ve Deployment'ı tek bir dosyada toplar. Tek komutla tüm WordPress altyapısını oluşturur.

### İçerik Yapısı

```yaml
# --- ile 3 bölüm:

# Bölüm 1: PersistentVolumeClaim
apiVersion: v1
kind: PersistentVolumeClaim
...
---
# Bölüm 2: Service
apiVersion: v1
kind: Service
...
---
# Bölüm 3: Deployment
apiVersion: apps/v1
kind: Deployment
...
```

### Avantajları

✅ **Tek Komut Deployment**
```powershell
kubectl apply -f wordpress-complete.yaml
```

✅ **Versiyon Kontrolü Kolaylığı**
- Tek dosya = Kolay git tracking
- Tüm konfigürasyon bir arada

✅ **Bağımlılıkları Görme**
- PVC → Service → Deployment ilişkisi açık

✅ **Kolay Silme**
```powershell
kubectl delete -f wordpress-complete.yaml
```

### Dezavantajları

❌ **Modülerlik Eksikliği**
- Bir şeyi değiştirmek için tüm dosya apply edilir

❌ **Karmaşık Büyük Projelerde**
- Çok kaynak olunca dosya şişer

### Kullanım Senaryoları

**✅ Kullan:**
- Hızlı demo/test ortamları
- Küçük uygulamalar
- Tutorial/eğitim amaçlı
- Tek komutla tüm stack oluşturmak istiyorsan

**❌ Kullanma:**
- Production ortamları (ayrı dosyalar daha iyi)
- Büyük, karmaşık uygulamalar
- Sık güncelleme yapılan ortamlar
- CI/CD pipeline'larında (ayrı dosyalar esneklik sağlar)

### Komutlar

```powershell
# Tüm kaynakları oluştur
kubectl apply -f wordpress-complete.yaml

# Durumu kontrol et
kubectl get all -n wp

# Tek tek kontrol
kubectl get pvc -n wp
kubectl get service wordpress -n wp
kubectl get deployment wordpress -n wp
kubectl get pods -n wp

# Tüm kaynakları sil
kubectl delete -f wordpress-complete.yaml

# Dry-run (test)
kubectl apply -f wordpress-complete.yaml --dry-run=client

# Diff (ne değişecek)
kubectl diff -f wordpress-complete.yaml
```

---

## 📊 Karşılaştırma Tablosu

| Özellik | Ayrı Dosyalar | Complete.yaml |
|---------|---------------|---------------|
| **Dosya Sayısı** | 3 ayrı dosya | 1 dosya |
| **Komut Sayısı** | 3 apply komutu | 1 apply komutu |
| **Modülerlik** | ✅ Yüksek | ❌ Düşük |
| **Versiyon Kontrolü** | Her dosya ayrı | Tümü bir arada |
| **Güncelleme** | Sadece değişen dosya | Tüm dosya |
| **Production** | ✅ İdeal | ⚠️ Uygun değil |
| **Demo/Test** | ⚠️ Fazla komut | ✅ Hızlı |
| **CI/CD** | ✅ Esnek | ❌ Katı |

---

## 🚀 Deployment Sırası

### Önkoşullar

```powershell
# 1. Namespace oluştur
kubectl create namespace wp

# 2. MySQL Secret oluştur
kubectl create secret generic mysql-pass -n wp --from-literal=password=admin
```

### Yöntem 1: Ayrı Dosyalarla (Önerilen - Production)

```powershell
# Sıra önemli!

# 1. PVC (en önce storage)
kubectl apply -f wordpress-pvc.yaml

# 2. Service (network)
kubectl apply -f wordpress-service.yaml

# 3. Deployment (son olarak uygulama)
kubectl apply -f wordpress-deployment.yaml

# Kontrol
kubectl get all -n wp
```

### Yöntem 2: Complete Dosya (Hızlı - Test/Demo)

```powershell
# Tek komut!
kubectl apply -f wordpress-complete.yaml

# Kontrol
kubectl get all -n wp
```

### Yöntem 3: Kustomize (Advanced)

```powershell
# kustomization.yaml oluştur
cat <<EOF > kustomization.yaml
namespace: wp
resources:
  - wordpress-pvc.yaml
  - wordpress-service.yaml
  - wordpress-deployment.yaml
secretGenerator:
  - name: mysql-pass
    literals:
      - password=admin
EOF

# Deploy
kubectl apply -k .
```

---

## 🧪 Test Senaryoları

### 1. Temel Erişim Testi

```powershell
# Pod'lar çalışıyor mu?
kubectl get pods -n wp -l app=wordpress

# Service çalışıyor mu?
kubectl get svc wordpress -n wp

# Endpoint'ler var mı?
kubectl get endpoints wordpress -n wp

# HTTP testi
curl http://$(minikube ip):30080
```

### 2. MySQL Bağlantı Testi

```powershell
# WordPress pod'una giriş
kubectl exec -it -n wp <wordpress-pod> -- bash

# MySQL client kur
apt-get update && apt-get install -y default-mysql-client

# Bağlan
mysql -h wordpress-mysql -u burak -padmin wp_db

# SQL test
SHOW TABLES;
EXIT;
```

### 3. Storage Testi

```powershell
# Volume mount edilmiş mi?
kubectl exec -it -n wp <pod-name> -- df -h | grep /var/www/html

# Dosya yazabilir miyiz?
kubectl exec -it -n wp <pod-name> -- touch /var/www/html/test.txt

# Dosya okunabilir mi?
kubectl exec -it -n wp <pod-name> -- ls -la /var/www/html/test.txt

# Temizle
kubectl exec -it -n wp <pod-name> -- rm /var/www/html/test.txt
```

### 4. High Availability Testi

```powershell
# Bir pod'u sil
kubectl delete pod <pod-name> -n wp

# Otomatik yeniden oluşturulmalı
kubectl get pods -n wp -w

# Service hala çalışıyor mu?
curl http://$(minikube ip):30080
```

### 5. Rolling Update Testi

```powershell
# Image güncelle
kubectl set image deployment/wordpress -n wp wordpress=wordpress:6.4

# Rollout izle
kubectl rollout status deployment/wordpress -n wp

# Pod'lar tek tek güncellendiğini gör
kubectl get pods -n wp -w

# Servis kesintiye uğramadı mı?
while true; do curl -s http://$(minikube ip):30080 > /dev/null && echo "UP" || echo "DOWN"; sleep 1; done
```

---

## 📝 Özet Cheat Sheet

```powershell
# === OLUŞTURMA ===
kubectl apply -f wordpress-complete.yaml
# VEYA
kubectl apply -f wordpress-pvc.yaml
kubectl apply -f wordpress-service.yaml
kubectl apply -f wordpress-deployment.yaml

# === KONTROL ===
kubectl get all -n wp
kubectl get pods -n wp -l app=wordpress
kubectl get svc wordpress -n wp
kubectl get pvc -n wp

# === ERİŞİM ===
minikube service wordpress -n wp
# VEYA
kubectl port-forward -n wp svc/wordpress 8080:80

# === LOG ===
kubectl logs -n wp deployment/wordpress -f

# === DEBUG ===
kubectl describe pod <pod-name> -n wp
kubectl exec -it -n wp <pod-name> -- bash

# === GÜNCELLEME ===
kubectl apply -f wordpress-deployment.yaml
kubectl rollout status deployment/wordpress -n wp

# === ÖLÇEKLEME ===
kubectl scale deployment wordpress -n wp --replicas=3

# === GERİ ALMA ===
kubectl rollout undo deployment/wordpress -n wp

# === SİLME ===
kubectl delete -f wordpress-complete.yaml
# VEYA
kubectl delete namespace wp
```

---

## 🎓 Best Practices

### 1. Image Versiyonları
❌ Yapma:
```yaml
image: wordpress:latest
```

✅ Yap:
```yaml
image: wordpress:6.4.2
```

### 2. Resource Limits
❌ Yapma:
```yaml
# Limit yok - pod tüm kaynakları tüketebilir
```

✅ Yap:
```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

### 3. Health Checks
❌ Yapma:
```yaml
# Health check yok - arızalı pod'lar çalışmaya devam eder
```

✅ Yap:
```yaml
livenessProbe:
  httpGet:
    path: /
    port: 80
  initialDelaySeconds: 60
readinessProbe:
  httpGet:
    path: /
    port: 80
  initialDelaySeconds: 30
```

### 4. Secrets
❌ Yapma:
```yaml
env:
- name: WORDPRESS_DB_PASSWORD
  value: "plain-text-password"
```

✅ Yap:
```yaml
env:
- name: WORDPRESS_DB_PASSWORD
  valueFrom:
    secretKeyRef:
      name: mysql-pass
      key: password
```

### 5. Namespace Kullanımı
❌ Yapma:
```yaml
# namespace yok - default namespace'e gider
```

✅ Yap:
```yaml
metadata:
  namespace: wp
```

### 6. Labels
❌ Yapma:
```yaml
# label yok - selector çalışmaz
```

✅ Yap:
```yaml
metadata:
  labels:
    app: wordpress
    tier: frontend
    version: "1.0"
    environment: production
```

### 7. Rolling Update Strategy
❌ Yapma:
```yaml
strategy:
  type: Recreate  # Kesinti olur
```

✅ Yap:
```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1
    maxUnavailable: 0  # Sıfır kesinti
```

### 8. Persistent Data
❌ Yapma:
```yaml
# Volume yok - pod silince veri gider
```

✅ Yap:
```yaml
volumeMounts:
- name: wordpress-persistent-storage
  mountPath: /var/www/html
volumes:
- name: wordpress-persistent-storage
  persistentVolumeClaim:
    claimName: wp-pv-claim
```

---

## 🔗 İlgili Dosyalar

- **MySQL Backend**: `../mysql/` klasörü
  - `mysql-deployment.yaml`
  - `mysql-service.yaml`
  - `mysql-pvc.yaml`
  - `secret.yaml`
  - `MYSQL-BAGLANTI.md`

- **Ana Dokümantasyon**:
  - `WORDPRESS-FRONTEND.md` - Detaylı kılavuz

---

## 📚 Kaynaklar

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [WordPress Docker Image](https://hub.docker.com/_/wordpress)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)

---

**📅 Güncellenme:** 2026-07-05  
**✍️ Doküman:** WordPress YAML Hızlı Referans
