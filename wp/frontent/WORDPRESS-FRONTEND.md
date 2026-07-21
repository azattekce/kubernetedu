# WordPress Frontend Kılavuzu

## 📊 Mevcut Durum

- **Namespace**: wp
- **Deployment**: wordpress
- **Service**: wordpress
- **Service Type**: NodePort
- **Port**: 80 (Container) → 30080 (NodePort)
- **Replicas**: 2
- **Image**: wordpress:latest
- **Storage**: 10Gi (PVC: wp-pv-claim)

## 🌐 Erişim Yöntemleri

### 1. NodePort Üzerinden Erişim

```powershell
# Cluster IP'sini öğren
kubectl get nodes -o wide

# Tarayıcıda aç
# http://<NODE-IP>:30080

# Minikube kullanıyorsanız
minikube service wordpress -n wp
```

### 2. Port Forward ile Yerel Erişim

```powershell
# Port forward başlat
kubectl port-forward -n wp service/wordpress 8080:80

# Tarayıcıda aç
# http://localhost:8080
```

### 3. Servis Bilgilerini Görüntüleme

```powershell
# Service detayları
kubectl get service wordpress -n wp
kubectl describe service wordpress -n wp

# Endpoint'leri kontrol et
kubectl get endpoints wordpress -n wp
```

## 📁 YAML Dosyaları Detayları

### 1. wordpress-pvc.yaml - Persistent Volume Claim

**Amaç**: WordPress dosyaları için kalıcı depolama alanı talep eder.

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: wp-pv-claim
  namespace: wp
  labels:
    app: wordpress
    tier: frontend
spec:
  accessModes:
    - ReadWriteOnce  # Tek bir node tarafından okunup yazılabilir
  resources:
    requests:
      storage: 10Gi  # 10GB depolama alanı
```

**Önemli Noktalar**:
- `ReadWriteOnce`: Aynı anda sadece bir node tarafından mount edilebilir
- WordPress tema, plugin ve upload dosyaları burada saklanır
- `/var/www/html` dizinine mount edilir

**Kontrol Komutları**:
```powershell
# PVC durumunu kontrol et
kubectl get pvc -n wp
kubectl describe pvc wp-pv-claim -n wp

# Hangi pod kullanıyor
kubectl get pods -n wp -o wide
```

---

### 2. wordpress-service.yaml - Service Tanımı

**Amaç**: WordPress pod'larına dışarıdan erişim sağlar.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: wordpress
  namespace: wp
  labels:
    app: wordpress
    tier: frontend
spec:
  type: NodePort      # Dış erişim için NodePort
  ports:
  - port: 80          # Service portu
    targetPort: 80    # Container portu
    protocol: TCP
    nodePort: 30080   # Node üzerindeki port (30000-32767 arası)
  selector:
    app: wordpress    # Bu labelları taşıyan pod'lara yönlendir
    tier: frontend
```

**Service Türleri**:
- `ClusterIP`: Sadece cluster içinden erişim (default)
- `NodePort`: Node IP:Port ile dış erişim (30000-32767)
- `LoadBalancer`: Cloud provider'ın load balancer'ı ile erişim

**Test Komutları**:
```powershell
# Service endpoint'lerini görüntüle
kubectl get endpoints wordpress -n wp

# Service detaylarını göster
kubectl describe service wordpress -n wp

# Service URL'ini al (minikube)
minikube service wordpress -n wp --url
```

---

### 3. wordpress-deployment.yaml - Deployment Tanımı

**Amaç**: WordPress uygulamasını çalıştıran pod'ları yönetir.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: wordpress
  namespace: wp
  labels:
    app: wordpress
    tier: frontend
spec:
  replicas: 2  # 2 pod çalıştır (High Availability)
  selector:
    matchLabels:
      app: wordpress
      tier: frontend
  strategy:
    type: RollingUpdate  # Sıfır kesinti ile güncelleme
    rollingUpdate:
      maxSurge: 1        # Aynı anda 1 fazla pod oluşturulabilir
      maxUnavailable: 0  # Güncelleme sırasında hiç pod down olmaz
```

**Deployment Stratejileri**:

1. **RollingUpdate** (Kullanılan): Sıfır kesinti ile güncelleme
   - Önce yeni pod başlatılır
   - Hazır olunca eski pod kapatılır
   - `maxSurge`: Aynı anda kaç fazla pod olabilir
   - `maxUnavailable`: Aynı anda kaç pod down olabilir

2. **Recreate**: Tüm pod'ları durdur, yenilerini başlat (Kesinti olur)

**Container Konfigürasyonu**:

```yaml
containers:
- name: wordpress
  image: wordpress:latest
  imagePullPolicy: IfNotPresent  # Image yoksa çek, varsa kullan
```

**Environment Variables (MySQL Bağlantısı)**:

```yaml
env:
- name: WORDPRESS_DB_HOST
  value: wordpress-mysql:3306  # MySQL service adı ve portu

- name: WORDPRESS_DB_NAME
  value: wp_db  # Veritabanı adı

- name: WORDPRESS_DB_USER
  value: burak  # Veritabanı kullanıcısı

- name: WORDPRESS_DB_PASSWORD
  valueFrom:
    secretKeyRef:
      name: mysql-pass  # Secret'tan şifre al
      key: password
```

**Resource Limits (Kaynak Yönetimi)**:

```yaml
resources:
  requests:  # Minimum garanti edilen kaynaklar
    memory: "256Mi"
    cpu: "250m"  # 0.25 CPU core
  limits:    # Maximum kullanılabilecek kaynaklar
    memory: "512Mi"
    cpu: "500m"  # 0.5 CPU core
```

**Health Checks (Sağlık Kontrolleri)**:

```yaml
livenessProbe:  # Pod canlı mı? Değilse yeniden başlat
  httpGet:
    path: /
    port: 80
  initialDelaySeconds: 60  # İlk kontrol 60 saniye sonra
  periodSeconds: 10        # Her 10 saniyede bir kontrol
  timeoutSeconds: 5        # 5 saniye içinde yanıt yoksa fail

readinessProbe:  # Pod trafiği kabul edebilir mi?
  httpGet:
    path: /
    port: 80
  initialDelaySeconds: 30  # İlk kontrol 30 saniye sonra
  periodSeconds: 5         # Her 5 saniyede bir kontrol
  timeoutSeconds: 3        # 3 saniye timeout
```

**Fark**:
- **LivenessProbe**: Uygulama dondu mu? → Yeniden başlat
- **ReadinessProbe**: Uygulama hazır mı? → Trafiği yönlendir/yönlendirme

**Volume Mounting**:

```yaml
volumeMounts:
- name: wordpress-persistent-storage
  mountPath: /var/www/html  # WordPress dosyaları

volumes:
- name: wordpress-persistent-storage
  persistentVolumeClaim:
    claimName: wp-pv-claim  # PVC referansı
```

---

### 4. wordpress-complete.yaml - Tek Dosyada Tüm Kaynaklar

**Amaç**: PVC, Service ve Deployment'ı tek bir dosyada toplar.

**Avantajları**:
- Tek komutla tüm kaynakları oluştur
- Kolay yönetim ve versiyon kontrolü
- Bağımlılıkları bir arada görme

**Kullanım**:
```powershell
# Tüm kaynakları oluştur
kubectl apply -f wordpress-complete.yaml

# Tüm kaynakları sil
kubectl delete -f wordpress-complete.yaml
```

**Yapısı**:
```yaml
# --- ile ayrılmış 3 bölüm:
1. PersistentVolumeClaim
---
2. Service
---
3. Deployment
```

## 🔧 Yönetim Komutları

### Pod Yönetimi

```powershell
# WordPress pod'larını listele
kubectl get pods -n wp -l app=wordpress

# Pod detaylarını görüntüle
kubectl describe pod <pod-name> -n wp

# Pod loglarını görüntüle
kubectl logs -n wp deployment/wordpress

# Canlı log takibi
kubectl logs -n wp deployment/wordpress -f

# Belirli pod'un logu
kubectl logs -n wp <pod-name>

# Pod'a giriş yap
kubectl exec -it -n wp <pod-name> -- bash
```

### Deployment Yönetimi

```powershell
# Deployment durumunu kontrol et
kubectl get deployment wordpress -n wp
kubectl describe deployment wordpress -n wp

# Replica sayısını değiştir
kubectl scale deployment wordpress -n wp --replicas=3

# Deployment'ı güncelle (yeni image)
kubectl set image deployment/wordpress -n wp wordpress=wordpress:6.4

# Güncelleme durumunu izle
kubectl rollout status deployment/wordpress -n wp

# Güncelleme geçmişini görüntüle
kubectl rollout history deployment/wordpress -n wp

# Önceki versiyona geri dön
kubectl rollout undo deployment/wordpress -n wp

# Belirli bir versiyona geri dön
kubectl rollout undo deployment/wordpress -n wp --to-revision=2
```

### Service ve Network

```powershell
# Service bilgilerini görüntüle
kubectl get service wordpress -n wp -o wide

# Endpoint'leri kontrol et
kubectl get endpoints wordpress -n wp

# Service üzerinden test
kubectl run -it --rm debug --image=busybox --restart=Never -n wp -- wget -qO- http://wordpress
```

### Storage Yönetimi

```powershell
# PVC durumunu kontrol et
kubectl get pvc -n wp

# PV (Persistent Volume) detayları
kubectl get pv

# PVC detayları
kubectl describe pvc wp-pv-claim -n wp

# Hangi pod kullanıyor
kubectl get pods -n wp -o json | grep -A 5 volumeMounts
```

## 🐛 Troubleshooting (Sorun Giderme)

### 1. Pod Başlamıyor

```powershell
# Pod durumunu kontrol et
kubectl get pods -n wp

# Olası durumlar ve çözümleri:
```

**Pending**: Kaynak yetersiz veya PVC mount edilemiyor
```powershell
kubectl describe pod <pod-name> -n wp
# Events kısmına bak
```

**CrashLoopBackOff**: Pod başladıktan hemen sonra kapanıyor
```powershell
# Logları kontrol et
kubectl logs -n wp <pod-name>
kubectl logs -n wp <pod-name> --previous  # Önceki çalışmanın logu

# MySQL bağlantısını kontrol et
kubectl exec -it -n wp <pod-name> -- env | grep WORDPRESS_DB
```

**ImagePullBackOff**: Image çekilemiyor
```powershell
kubectl describe pod <pod-name> -n wp
# Image adını ve registry erişimini kontrol et
```

### 2. MySQL Bağlantı Hatası

```powershell
# MySQL service çalışıyor mu?
kubectl get service -n wp | grep mysql

# MySQL pod çalışıyor mu?
kubectl get pods -n wp | grep mysql

# Environment variable'lar doğru mu?
kubectl exec -it -n wp <wordpress-pod> -- env | grep DB

# MySQL'e manuel bağlantı testi
kubectl exec -it -n wp <wordpress-pod> -- bash
apt-get update && apt-get install -y default-mysql-client
mysql -h wordpress-mysql -u burak -padmin wp_db
```

### 3. Websitesine Erişilemiyor

```powershell
# Service var mı?
kubectl get service wordpress -n wp

# Endpoint'ler var mı?
kubectl get endpoints wordpress -n wp

# Pod'lar Ready durumunda mı?
kubectl get pods -n wp -l app=wordpress

# Port-forward ile direkt teste
kubectl port-forward -n wp service/wordpress 8080:80
# Tarayıcıda: http://localhost:8080

# NodePort ile test (minikube)
minikube service wordpress -n wp
```

### 4. Dosya Upload Edilemiyor

```powershell
# PVC mount edilmiş mi?
kubectl exec -it -n wp <pod-name> -- df -h | grep /var/www/html

# Dizin izinleri
kubectl exec -it -n wp <pod-name> -- ls -la /var/www/html

# wp-content yazılabilir mi?
kubectl exec -it -n wp <pod-name> -- ls -la /var/www/html/wp-content/uploads

# İzin düzeltme (gerekirse)
kubectl exec -it -n wp <pod-name> -- chown -R www-data:www-data /var/www/html
```

### 5. Yüksek Kaynak Kullanımı

```powershell
# Pod kaynak kullanımını görüntüle
kubectl top pods -n wp

# Resource limits kontrolü
kubectl describe pod <pod-name> -n wp | grep -A 5 Limits

# Logları kontrol et (hata var mı?)
kubectl logs -n wp <pod-name> | tail -100
```

## 📈 Monitoring ve Logs

### Pod Durumu İzleme

```powershell
# Tüm pod'ların durumu
kubectl get pods -n wp -w  # Watch mode (-w)

# Detaylı durum
kubectl get pods -n wp -o wide

# JSON formatında tam bilgi
kubectl get pods -n wp -o json

# Specific field'leri seç
kubectl get pods -n wp -o custom-columns=NAME:.metadata.name,STATUS:.status.phase,NODE:.spec.nodeName
```

### Log Yönetimi

```powershell
# Son 100 satır
kubectl logs -n wp <pod-name> --tail=100

# Son 1 saatteki loglar
kubectl logs -n wp <pod-name> --since=1h

# Canlı log takibi
kubectl logs -n wp <pod-name> -f

# Önceki container'ın logu (crash durumunda)
kubectl logs -n wp <pod-name> --previous

# Tüm replica'ların logu
kubectl logs -n wp -l app=wordpress --all-containers=true
```

### Events İzleme

```powershell
# Namespace'deki tüm events
kubectl get events -n wp --sort-by='.lastTimestamp'

# Son 10 event
kubectl get events -n wp --sort-by='.lastTimestamp' | tail -10

# Belirli bir pod'un eventleri
kubectl describe pod <pod-name> -n wp | grep -A 10 Events
```

## 🔐 Güvenlik

### Secret Yönetimi

```powershell
# MySQL password secret'ı kontrol et
kubectl get secret mysql-pass -n wp

# Secret içeriğini görüntüle (base64 encoded)
kubectl get secret mysql-pass -n wp -o yaml

# Secret'ı decode et
kubectl get secret mysql-pass -n wp -o jsonpath='{.data.password}' | base64 -d
```

### Pod Security

```powershell
# Container'ın root olarak çalışıp çalışmadığını kontrol et
kubectl exec -it -n wp <pod-name> -- whoami

# Security context kontrol
kubectl get pod <pod-name> -n wp -o yaml | grep -A 10 securityContext
```

## 📦 Backup ve Restore

### WordPress Dosyaları Backup

```powershell
# Pod'dan local'e dosya kopyala
kubectl cp -n wp <pod-name>:/var/www/html ./wordpress-backup

# Local'den pod'a dosya kopyala
kubectl cp ./wordpress-backup -n wp <pod-name>:/var/www/html
```

### Database Backup (MySQL)

```powershell
# Database dump al
kubectl exec -n wp deployment/wordpress-mysql -- mysqldump -u root -pwproot wp_db > wp_backup.sql

# Database restore et
cat wp_backup.sql | kubectl exec -i -n wp deployment/wordpress-mysql -- mysql -u root -pwproot wp_db
```

## ⚡ Performance İyileştirme

### 1. Resource Limits Artırma

```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "500m"
  limits:
    memory: "1Gi"
    cpu: "1000m"
```

### 2. Replica Sayısını Artırma

```powershell
kubectl scale deployment wordpress -n wp --replicas=3
```

### 3. Caching Ekleme

WordPress'e Redis veya Memcached cache ekleyerek performansı artırabilirsiniz.

### 4. PHP Optimizasyonu

Custom image oluşturup PHP ayarlarını optimize edin:
- `memory_limit`
- `max_execution_time`
- `upload_max_filesize`

## 🚀 Dağıtım Adımları

### İlk Kurulum

```powershell
# 1. Namespace oluştur (yoksa)
kubectl create namespace wp

# 2. MySQL Secret oluştur
kubectl create secret generic mysql-pass -n wp --from-literal=password=admin

# 3. MySQL'i deploy et (mysql klasöründeki yaml'larla)
kubectl apply -f ../mysql/

# 4. WordPress'i deploy et
kubectl apply -f wordpress-complete.yaml

# 5. Durumu kontrol et
kubectl get all -n wp

# 6. Erişim
minikube service wordpress -n wp
```

### Güncelleme

```powershell
# YAML dosyasını düzenle
# Sonra apply et
kubectl apply -f wordpress-deployment.yaml

# Rollout durumunu izle
kubectl rollout status deployment/wordpress -n wp
```

### Silme

```powershell
# Sadece WordPress
kubectl delete -f wordpress-complete.yaml

# Tüm namespace'i sil (dikkatli!)
kubectl delete namespace wp
```

## 📚 Faydalı Kaynaklar

- [WordPress Docker Image](https://hub.docker.com/_/wordpress)
- [Kubernetes Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [Kubernetes Services](https://kubernetes.io/docs/concepts/services-networking/service/)
- [Persistent Volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)
- [WordPress Codex](https://codex.wordpress.org/)

## 💡 İpuçları

1. **Health Check Süreleri**: WordPress başlatması uzun sürebilir, `initialDelaySeconds` değerlerini uygun ayarlayın.

2. **Persistent Storage**: PVC silmeden önce yedeğinizi alın, veriler kalıcı olarak silinir.

3. **Resource Limits**: Çok düşük ayarlanırsa pod crash olabilir, izleyip ayarlayın.

4. **Rolling Update**: `maxUnavailable: 0` ile sıfır kesinti güncellemesi yapabilirsiniz.

5. **Secrets**: Production'da asla plain text şifre kullanmayın, mutlaka Secret kullanın.

6. **Image Tag**: `latest` yerine belirli version kullanın (ör: `wordpress:6.4`)

7. **Backup**: Düzenli backup alın, hem dosyalar hem veritabanı için.

8. **Monitoring**: Log ve metric'leri düzenli takip edin.
