# Kubernetes Eğitim Notları
**Tarih:** 12 Mayıs 2026  
**Konu:** Kubernetes Deployment, Service, Ingress ve Load Balancing

---

## 📚 İçindekiler
1. [Kubernetes Temel Kavramlar](#kubernetes-temel-kavramlar)
2. [Namespace Yönetimi](#namespace-yönetimi)
3. [Pod ve Deployment](#pod-ve-deployment)
4. [Service Tipleri ve Kullanımı](#service-tipleri-ve-kullanımı)
5. [Load Balancing](#load-balancing)
6. [Ingress Controller](#ingress-controller)
7. [Multi-Service Mimarisi](#multi-service-mimarisi)
8. [Pratik Komutlar](#pratik-komutlar)

---

## 1. Kubernetes Temel Kavramlar

### 1.1 Kubernetes Nedir?
Kubernetes, container'ları otomatik olarak deploy eden, ölçeklendiren ve yöneten açık kaynaklı bir platformdur.

### 1.2 Temel Bileşenler

| Bileşen | Açıklama | Kullanım Amacı |
|---------|----------|----------------|
| **Pod** | En küçük deployable birim | Container'ları çalıştırmak |
| **Deployment** | Pod'ları yöneten üst seviye nesne | Ölçeklendirme, güncelleme, rollback |
| **Service** | Pod'lara erişim sağlayan network abstraction | Load balancing, service discovery |
| **Ingress** | Cluster dışından HTTP/HTTPS erişimi | Domain routing, SSL/TLS, path routing |
| **Namespace** | Kaynakları gruplandırma | Ortam ayırma (dev, test, prod) |

---

## 2. Namespace Yönetimi

### 2.1 Namespace Nedir?
Namespace, Kubernetes cluster'ındaki kaynakları mantıksal olarak ayırmak için kullanılır.

### 2.2 Namespace Oluşturma

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: azatdevops
  labels:
    name: azatdevops
    environment: development
```

**Kullanım:**
```bash
# Namespace oluştur
kubectl apply -f namespace.yml

# Namespace'leri listele
kubectl get namespaces

# Belirli namespace'deki kaynakları listele
kubectl get all -n azatdevops
```

### 2.3 Namespace Avantajları
- ✅ **İzolasyon:** Farklı projeler/ekipler ayrı çalışır
- ✅ **Kaynak Kontrolü:** Namespace bazında quota ve limit
- ✅ **Organizasyon:** Dev, test, prod ortamlarını ayırma
- ✅ **Güvenlik:** RBAC ile namespace bazlı yetkilendirme

---

## 3. Pod ve Deployment

### 3.1 Pod Nedir?
Pod, bir veya daha fazla container içeren en küçük Kubernetes nesnesidir.

#### Pod Örneği
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
  namespace: azatdevops
  labels:
    app: nginx
spec:
  containers:
  - name: nginx
    image: nginx:latest
    imagePullPolicy: IfNotPresent
    ports:
    - containerPort: 80
      protocol: TCP
```

**Özellikler:**
- Tek bir IP adresi
- Aynı pod içindeki container'lar `localhost` ile haberleşir
- Geçici (ephemeral) - pod ölürse kaybolur

### 3.2 Deployment Nedir?
Deployment, pod'ların istenen durumunu tanımlar ve yönetir.

#### Deployment Örneği
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  namespace: azatdevops
spec:
  replicas: 2  # 2 kopya pod çalıştır
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.16.1
        ports:
        - containerPort: 80
```

**Avantajları:**
- ✅ **Ölçeklendirme:** `replicas` değerini değiştirerek pod sayısını artır/azalt
- ✅ **Self-healing:** Pod çökerse otomatik yeniden oluşturur
- ✅ **Rolling Update:** Sıfır downtime ile güncelleme
- ✅ **Rollback:** Önceki versiyona geri dönme

### 3.3 Pod vs Deployment

| Özellik | Pod | Deployment |
|---------|-----|------------|
| **Ölçeklendirme** | Manuel | Otomatik (replicas) |
| **Self-healing** | ❌ Yok | ✅ Var |
| **Güncelleme** | Manuel silip oluştur | Rolling update |
| **Kullanım** | Test, debug | Production |

---

## 4. Service Tipleri ve Kullanımı

### 4.1 Service Nedir?
Service, pod'lara erişim sağlayan **sabit bir endpoint**'tir. Pod'lar geçici olsa da, Service kalıcıdır.

### 4.2 Service Tipleri

#### 4.2.1 ClusterIP (Varsayılan)
**Açıklama:** Sadece cluster içinden erişilebilir

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
  namespace: azatdevops
spec:
  type: ClusterIP
  selector:
    app: nginx
  ports:
  - port: 80
    targetPort: 80
```

**Kullanım:**
- Microservice'ler arası iletişim
- Backend servisleri
- Cluster içi erişim

#### 4.2.2 NodePort
**Açıklama:** Her node'un belirli bir portunu dışarıya açar (30000-32767)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
  namespace: azatdevops
spec:
  type: NodePort
  selector:
    app: nginx
  ports:
  - port: 80        # Service portu
    targetPort: 80  # Container portu
    nodePort: 30080 # Node portu (isteğe bağlı)
```

**Erişim:**
```
http://<NODE-IP>:30080
```

**Kullanım:**
- Development/test ortamları
- Cloud olmayan kurulumlar
- Basit dış erişim

#### 4.2.3 LoadBalancer
**Açıklama:** Cloud provider'ın load balancer'ını oluşturur

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
  namespace: azatdevops
spec:
  type: LoadBalancer
  selector:
    app: nginx
  ports:
  - port: 80
    targetPort: 80
```

**Kullanım:**
- Production ortamlar
- Cloud platformları (AWS, Azure, GCP)
- Otomatik external IP

### 4.3 Service Seçici (Selector)
Service, pod'ları **label** ile seçer:

```yaml
# Service
selector:
  app: nginx

# Pod/Deployment
labels:
  app: nginx
```

**ÖNEMLİ:** Label'lar eşleşmezse Service pod'ları bulamaz!

---

## 5. Load Balancing

### 5.1 Kubernetes Load Balancing Nasıl Çalışır?

```
Client İsteği
    ↓
Service (ClusterIP/NodePort/LoadBalancer)
    ↓
[Endpoint List: 10.244.0.43, 10.244.0.44, 10.244.0.45]
    ↓
Round-Robin / Random Distribution
    ↓
Pod 1    Pod 2    Pod 3
```

### 5.2 Bugün Yaptığımız Load Balancing Testi

**Deployment:**
```yaml
replicas: 2  # 2 pod oluşturduk
```

**Test Sonucu (Cluster İçinden):**
```bash
kubectl exec -n azatdevops nginx-pod -- sh -c \
  'for i in 1 2 3 4 5 6 7 8 9 10; do 
     curl -s http://nginx-service | grep POD
   done'
```

**Çıktı:**
```
İstek 1: POD 1
İstek 2: POD 2
İstek 3: POD 2
İstek 4: POD 1
İstek 5: POD 3
... (istekler dağıtılıyor)
```

### 5.3 Port-Forward ile Neden Load Balancing Yok?

**Port-Forward:**
```bash
kubectl port-forward service/nginx-service 8080:80
```

**Sorun:**
- Port-forward, **tek bir endpoint**'e bağlanır
- Bağlantı kurulduktan sonra sabit kalır
- Load balancing yapmaz

**Çözüm:**
- ✅ Cluster içinden test et
- ✅ Ingress kullan
- ✅ NodePort ile direkt erişim

### 5.4 Session Affinity (İsteğe Bağlı)

Aynı client'tan gelen istekleri aynı pod'a yönlendir:

```yaml
spec:
  sessionAffinity: ClientIP
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 10800  # 3 saat
```

---

## 6. Ingress Controller

### 6.1 Ingress Nedir?

**Ingress**, HTTP/HTTPS trafiğini yönlendiren bir API nesnesidir.

**Service ile Karşılaştırma:**

| Özellik | Service (NodePort) | Ingress |
|---------|-------------------|---------|
| **Erişim** | `IP:30080` | `http://myapp.local` |
| **Domain** | ❌ Yok | ✅ Domain routing |
| **Path Routing** | ❌ Yok | ✅ `/api`, `/admin` |
| **SSL/TLS** | ❌ Manuel | ✅ Otomatik |
| **Tek Giriş** | Her servis ayrı port | ✅ Tek IP |

### 6.2 Ingress Mimarisi

```
┌─────────────────────────────────────────────┐
│            Client (Browser)                  │
└─────────────────┬───────────────────────────┘
                  │
                  │ HTTP Request
                  │ Host: nginx.local
                  │
┌─────────────────▼───────────────────────────┐
│         Ingress Controller (NGINX)          │
│  - Host-based routing                       │
│  - Path-based routing                       │
│  - SSL/TLS termination                      │
│  - Load balancing                           │
└─────────────────┬───────────────────────────┘
                  │
        ┌─────────┼─────────┐
        │         │         │
┌───────▼──┐ ┌───▼────┐ ┌──▼──────┐
│ Service1 │ │Service2│ │Service3 │
│ (ClusterIP)│(ClusterIP)│(ClusterIP)
└─────┬────┘ └───┬────┘ └────┬────┘
      │          │           │
  ┌───┴───┐  ┌──┴──┐    ┌───┴───┐
  │Pod1 Pod2│Pod3 Pod4│  │Pod5   │
  └────────┘ └──────┘   └───────┘
```

### 6.3 Ingress Kurulumu (Minikube)

```bash
# 1. Ingress Controller'ı etkinleştir
minikube addons enable ingress

# 2. Controller'ın çalıştığını doğrula
kubectl get pods -n ingress-nginx

# Beklenen çıktı:
# NAME                                        READY   STATUS    RESTARTS   AGE
# ingress-nginx-controller-xxx                1/1     Running   0          1m
```

### 6.4 Basit Ingress Örneği

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: nginx-ingress
  namespace: azatdevops
  annotations:
    kubernetes.io/ingress.class: "nginx"
    nginx.ingress.kubernetes.io/ssl-redirect: "false"
spec:
  ingressClassName: nginx
  rules:
  - host: nginx.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: nginx-service
            port:
              number: 80
```

**Deploy:**
```bash
kubectl apply -f Ingress.yml
```

**Hosts Dosyası (Windows):**
```
C:\Windows\System32\drivers\etc\hosts

192.168.49.2  nginx.local
```

**Erişim:**
```
http://nginx.local
```

### 6.5 Path-Based Routing

Aynı domain, farklı path'ler:

```yaml
spec:
  rules:
  - host: myapp.local
    http:
      paths:
      - path: /           # Frontend
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 80
      
      - path: /api        # Backend API
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 80
      
      - path: /admin      # Admin Panel
        pathType: Prefix
        backend:
          service:
            name: admin-service
            port:
              number: 80
```

**Erişim:**
```
http://myapp.local/       → Frontend
http://myapp.local/api    → Backend
http://myapp.local/admin  → Admin
```

### 6.6 Host-Based Routing

Farklı domain'ler, farklı servisler:

```yaml
spec:
  rules:
  - host: frontend.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 80
  
  - host: api.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 80
```

**Erişim:**
```
http://frontend.local/  → Frontend
http://api.local/       → Backend
```

### 6.7 Ingress Annotations

Ingress davranışını kontrol eden özel ayarlar:

```yaml
annotations:
  # Ingress sınıfı
  kubernetes.io/ingress.class: "nginx"
  
  # URL rewrite
  nginx.ingress.kubernetes.io/rewrite-target: /
  
  # SSL redirect
  nginx.ingress.kubernetes.io/ssl-redirect: "false"
  
  # CORS
  nginx.ingress.kubernetes.io/enable-cors: "true"
  
  # Rate limiting
  nginx.ingress.kubernetes.io/limit-rps: "100"
  
  # Upload size
  nginx.ingress.kubernetes.io/proxy-body-size: "8m"
  
  # Timeout
  nginx.ingress.kubernetes.io/proxy-read-timeout: "600"
```

---

## 7. Multi-Service Mimarisi

### 7.1 Gerçek Dünya Senaryosu

**E-Ticaret Uygulaması:**

```
┌──────────────────────────────────────────────┐
│        Ingress Controller (myshop.com)       │
└────┬─────────┬──────────┬──────────┬─────────┘
     │         │          │          │
     │ /       │ /api     │ /admin   │ /payment
     │         │          │          │
┌────▼───┐ ┌──▼────┐ ┌───▼────┐ ┌──▼──────┐
│Frontend│ │Backend│ │Admin   │ │Payment  │
│Service │ │Service│ │Service │ │Service  │
│(2 pods)│ │(3 pods)│(1 pod) │ │(2 pods) │
└────────┘ └───────┘ └────────┘ └─────────┘
```

### 7.2 Bugün Oluşturduğumuz Multi-Service

**Dosya:** `multi-service-ingress.yml`

**Yapı:**
```
3 Deployment:
  - frontend-deployment  (2 replicas)
  - backend-deployment   (3 replicas)
  - admin-deployment     (1 replica)

3 Service:
  - frontend-service (ClusterIP)
  - backend-service  (ClusterIP)
  - admin-service    (ClusterIP)

2 Ingress:
  - multi-service-ingress  (Path-based)
  - host-based-ingress     (Host-based)
```

### 7.3 Deployment ve Test

```bash
# 1. Deploy
kubectl apply -f multi-service-ingress.yml

# 2. Pod durumu
kubectl get pods -n azatdevops

# Beklenen çıktı:
# frontend-deployment-xxx   1/1  Running
# frontend-deployment-yyy   1/1  Running
# backend-deployment-xxx    1/1  Running
# backend-deployment-yyy    1/1  Running
# backend-deployment-zzz    1/1  Running
# admin-deployment-xxx      1/1  Running

# 3. Service durumu
kubectl get svc -n azatdevops

# 4. Ingress durumu
kubectl get ingress -n azatdevops
```

**Hosts dosyasına ekle:**
```
192.168.49.2  myapp.local
192.168.49.2  frontend.local
192.168.49.2  api.local
192.168.49.2  admin.local
```

**Test:**
```bash
# Path-based
curl http://myapp.local/
curl http://myapp.local/api
curl http://myapp.local/admin

# Host-based
curl http://frontend.local/
curl http://api.local/
curl http://admin.local/
```

---

## 8. Pratik Komutlar

### 8.1 Pod Yönetimi

```bash
# Pod'ları listele
kubectl get pods -n azatdevops
kubectl get pods -n azatdevops -o wide  # IP adresleriyle

# Pod detayları
kubectl describe pod <pod-name> -n azatdevops

# Pod logları
kubectl logs <pod-name> -n azatdevops
kubectl logs <pod-name> -n azatdevops -f  # Canlı takip

# Pod içine gir (exec)
kubectl exec -it <pod-name> -n azatdevops -- bash
kubectl exec -it <pod-name> -n azatdevops -- sh

# Pod silme
kubectl delete pod <pod-name> -n azatdevops
```

### 8.2 Deployment Yönetimi

```bash
# Deployment listele
kubectl get deployments -n azatdevops

# Deployment detayları
kubectl describe deployment <deployment-name> -n azatdevops

# Ölçeklendirme
kubectl scale deployment <deployment-name> --replicas=5 -n azatdevops

# Deployment güncelleme
kubectl set image deployment/<deployment-name> nginx=nginx:1.19 -n azatdevops

# Rollout durumu
kubectl rollout status deployment/<deployment-name> -n azatdevops

# Rollout history
kubectl rollout history deployment/<deployment-name> -n azatdevops

# Rollback (önceki versiyona dön)
kubectl rollout undo deployment/<deployment-name> -n azatdevops
```

### 8.3 Service Yönetimi

```bash
# Service listele
kubectl get services -n azatdevops
kubectl get svc -n azatdevops  # Kısa hali

# Service detayları
kubectl describe service <service-name> -n azatdevops

# Endpoint'leri görüntüle
kubectl get endpoints <service-name> -n azatdevops

# Service silme
kubectl delete service <service-name> -n azatdevops
```

### 8.4 Ingress Yönetimi

```bash
# Ingress listele
kubectl get ingress -n azatdevops

# Ingress detayları
kubectl describe ingress <ingress-name> -n azatdevops

# Ingress Controller logları
kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx

# Ingress silme
kubectl delete ingress <ingress-name> -n azatdevops
```

### 8.5 Port Forwarding

```bash
# Service'e port forward
kubectl port-forward service/<service-name> 8080:80 -n azatdevops

# Pod'a port forward
kubectl port-forward <pod-name> 8080:80 -n azatdevops

# Deployment'a port forward
kubectl port-forward deployment/<deployment-name> 8080:80 -n azatdevops
```

### 8.6 Tüm Kaynaklar

```bash
# Namespace'deki tüm kaynakları listele
kubectl get all -n azatdevops

# YAML çıktısı al
kubectl get deployment <name> -n azatdevops -o yaml

# JSON çıktısı al
kubectl get deployment <name> -n azatdevops -o json

# Belirli alanları göster
kubectl get pods -n azatdevops -o custom-columns=NAME:.metadata.name,STATUS:.status.phase,IP:.status.podIP
```

### 8.7 Namespace Yönetimi

```bash
# Namespace listele
kubectl get namespaces

# Namespace oluştur
kubectl create namespace <namespace-name>

# Namespace sil (dikkat: içindeki her şeyi siler!)
kubectl delete namespace <namespace-name>

# Varsayılan namespace değiştir
kubectl config set-context --current --namespace=azatdevops
```

### 8.8 YAML Dosyalarıyla Çalışma

```bash
# Apply (oluştur veya güncelle)
kubectl apply -f deployment.yml
kubectl apply -f .  # Klasördeki tüm YAML'lar

# Create (sadece oluştur, varsa hata verir)
kubectl create -f deployment.yml

# Delete (sil)
kubectl delete -f deployment.yml

# Dry run (gerçekten uygulamadan kontrol et)
kubectl apply -f deployment.yml --dry-run=client

# YAML doğrulama
kubectl apply -f deployment.yml --validate=true --dry-run=client
```

### 8.9 Debugging

```bash
# Event'leri görüntüle
kubectl get events -n azatdevops --sort-by='.lastTimestamp'

# Resource kullanımı
kubectl top nodes
kubectl top pods -n azatdevops

# Cluster bilgisi
kubectl cluster-info
kubectl get nodes
kubectl describe node <node-name>

# API kaynakları
kubectl api-resources

# Hata ayıklama pod'u çalıştır
kubectl run debug --image=busybox -it --rm --restart=Never -- sh
```

---

## 9. Bugün Öğrendiklerimiz - Özet

### 9.1 Ana Konular

1. ✅ **Namespace Oluşturma ve Yönetimi**
   - Kaynakları izole etme
   - Ortam ayırma (dev, test, prod)

2. ✅ **Pod ve Deployment Farkı**
   - Pod: Tek kullanımlık
   - Deployment: Production için ideal

3. ✅ **Service Tipleri**
   - ClusterIP: Cluster içi
   - NodePort: Basit dış erişim
   - LoadBalancer: Cloud load balancer

4. ✅ **Load Balancing**
   - Service otomatik load balance yapar
   - Port-forward load balance yapmaz
   - Cluster içi test önemli

5. ✅ **Ingress Controller**
   - Domain-based routing
   - Path-based routing
   - SSL/TLS desteği

6. ✅ **Multi-Service Mimarisi**
   - Tek Ingress ile birden fazla servis
   - Microservice mimarisi
   - Gerçek dünya senaryoları

### 9.2 Oluşturulan Dosyalar

| Dosya | İçerik | Amaç |
|-------|--------|------|
| `dev-deployment.yml` | Namespace + Pod + Deployment + Service | Temel Kubernetes kaynakları |
| `Ingress.yml` | Ingress kaynağı | Domain-based routing |
| `multi-service-ingress.yml` | 3 Deployment + 3 Service + 2 Ingress | Multi-service mimarisi |

### 9.3 Pratik Deneyimler

```bash
# 1. Basit deployment
kubectl apply -f dev-deployment.yml
kubectl get all -n azatdevops

# 2. Load balancing testi
kubectl exec -n azatdevops nginx-pod -- sh -c \
  'for i in 1 2 3 4 5; do curl -s http://nginx-service | grep POD; done'

# 3. Ingress ile erişim
kubectl apply -f Ingress.yml
# Tarayıcı: http://nginx.local

# 4. Multi-service
kubectl apply -f multi-service-ingress.yml
# Tarayıcı: http://myapp.local/api
```

---

## 10. İleri Seviye Konular (Sonraki Adımlar)

### 10.1 ConfigMap ve Secret
```yaml
# ConfigMap: Uygulama ayarları
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  database_url: "postgres://db:5432"
  log_level: "info"

# Secret: Hassas veriler
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
data:
  username: YWRtaW4=  # base64
  password: cGFzc3dvcmQ=
```

### 10.2 Persistent Volume
```yaml
# Kalıcı veri depolama
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mysql-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
```

### 10.3 Horizontal Pod Autoscaler
```yaml
# Otomatik ölçeklendirme
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: nginx-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: nginx-deployment
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 80
```

### 10.4 StatefulSet
```yaml
# Stateful uygulamalar (database, kafka)
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql
spec:
  serviceName: mysql
  replicas: 3
  selector:
    matchLabels:
      app: mysql
  template:
    metadata:
      labels:
        app: mysql
    spec:
      containers:
      - name: mysql
        image: mysql:8.0
        ports:
        - containerPort: 3306
```

### 10.5 DaemonSet
```yaml
# Her node'da çalışan pod'lar (monitoring, logging)
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluentd
spec:
  selector:
    matchLabels:
      name: fluentd
  template:
    metadata:
      labels:
        name: fluentd
    spec:
      containers:
      - name: fluentd
        image: fluent/fluentd:latest
```

---

## 11. Best Practices

### 11.1 Deployment Best Practices

✅ **DO (Yapılması Gerekenler):**
- Resource limits tanımla (CPU, memory)
- Liveness ve Readiness probe kullan
- Labels ve selectors tutarlı kullan
- Rolling update stratejisi kullan
- Namespace kullan (production için)

❌ **DON'T (Yapılmaması Gerekenler):**
- `latest` tag kullanma (belirli version kullan)
- Root user ile çalıştırma
- Hardcoded password/secret kullanma
- Tek replica ile production'a çıkma

### 11.2 Service Best Practices

✅ **DO:**
- İsimler DNS-compatible olsun (küçük harf, tire)
- ClusterIP varsayılan olarak kullan
- Health check endpoint'leri ekle
- Monitoring ve metrics ekle

❌ **DON'T:**
- Her service için LoadBalancer kullanma (maliyetli)
- Session affinity gereksiz kullanma
- Port충돌 yaratma

### 11.3 Ingress Best Practices

✅ **DO:**
- SSL/TLS kullan (Let's Encrypt)
- Rate limiting ekle
- CORS doğru yapılandır
- Path routing dikkatli kullan
- Monitoring ekle

❌ **DON'T:**
- Wildcard domain gereksiz kullanma
- Default backend unutma
- SSL redirect kapatma (production'da)

---

## 12. Troubleshooting

### 12.1 Pod Sorunları

**Pod başlamıyor:**
```bash
# 1. Pod durumunu kontrol et
kubectl get pods -n azatdevops

# 2. Detaylı bilgi
kubectl describe pod <pod-name> -n azatdevops

# 3. Event'lere bak
kubectl get events -n azatdevops --sort-by='.lastTimestamp'

# Yaygın sorunlar:
# - ImagePullBackOff: Image bulunamıyor
# - CrashLoopBackOff: Container sürekli çöküyor
# - Pending: Resource yetersiz veya scheduling sorunu
```

**Pod logları:**
```bash
# Normal log
kubectl logs <pod-name> -n azatdevops

# Önceki container'ın logu
kubectl logs <pod-name> -n azatdevops --previous

# Canlı takip
kubectl logs <pod-name> -n azatdevops -f
```

### 12.2 Service Sorunları

**Service pod'lara erişemiyor:**
```bash
# 1. Endpoint kontrolü
kubectl get endpoints <service-name> -n azatdevops

# Eğer ENDPOINTS boşsa:
# - Selector label'ları kontrol et
# - Pod'ların READY olduğundan emin ol

# 2. Label eşleşmesi
kubectl get pods -n azatdevops --show-labels
kubectl describe service <service-name> -n azatdevops

# 3. Port kontrolü
# Service port ve targetPort eşleşmeli
```

### 12.3 Ingress Sorunları

**Ingress çalışmıyor:**
```bash
# 1. Ingress Controller var mı?
kubectl get pods -n ingress-nginx

# 2. Ingress durumu
kubectl describe ingress <ingress-name> -n azatdevops

# 3. Controller logları
kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx

# 4. Backend service çalışıyor mu?
kubectl get svc -n azatdevops

# 5. Hosts dosyası doğru mu?
ping myapp.local
```

---

## 13. Kaynaklar ve Referanslar

### 13.1 Resmi Dökümanlar
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
- [Ingress Controllers](https://kubernetes.io/docs/concepts/services-networking/ingress-controllers/)

### 13.2 Minikube
- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
- [Minikube Addons](https://minikube.sigs.k8s.io/docs/commands/addons/)

### 13.3 Pratik Eğitim
- [Kubernetes By Example](https://kubernetesbyexample.com/)
- [Play with Kubernetes](https://labs.play-with-k8s.com/)

---

## 14. Sıkça Sorulan Sorular (FAQ)

**S: Pod ve Deployment arasındaki fark nedir?**
C: Pod tek kullanımlıktır, Deployment ise pod'ları yöneten ve ölçeklendiren üst seviye bir nesnedir. Production'da her zaman Deployment kullanın.

**S: Service olmadan pod'lara erişebilir miyim?**
C: Cluster içinden IP ile erişebilirsiniz ama pod IP'leri geçicidir. Service sabit bir endpoint sağlar.

**S: Ingress ne zaman kullanmalıyım?**
C: HTTP/HTTPS trafiği için domain-based veya path-based routing yapmak istediğinizde. Tek bir IP'den birden fazla servise erişim için idealdir.

**S: LoadBalancer her zaman gerekli mi?**
C: Hayır. Development'ta NodePort, production cloud ortamlarında LoadBalancer, on-premise'de Ingress + NodePort kombinasyonu kullanılabilir.

**S: Replica sayısını nasıl belirlemeliyim?**
C: Trafik, resource kullanımı ve high availability ihtiyacınıza göre. Başlangıç için 2-3, sonra otoscaling ekleyin.

---

## 15. Özet Çizelge

| Kavram | Ne Zaman Kullan | Alternatif |
|--------|-----------------|------------|
| **Pod** | Debug, test | Deployment |
| **Deployment** | Stateless uygulamalar | StatefulSet (stateful için) |
| **Service** | Her zaman (pod erişimi için) | - |
| **ClusterIP** | Cluster içi servisler | - |
| **NodePort** | Dev/test dış erişim | Ingress |
| **LoadBalancer** | Production (cloud) | Ingress |
| **Ingress** | HTTP/HTTPS routing | LoadBalancer (basit dış erişim) |
| **Namespace** | Ortam/proje ayırma | - |

---

## 16. Sonraki Adımlar

1. ✅ **Tamamladıklarınız:**
   - Kubernetes temelleri
   - Deployment ve Service
   - Ingress ve routing
   - Multi-service mimarisi

2. 📚 **Öğrenilecekler:**
   - ConfigMap ve Secret yönetimi
   - Persistent Volume kullanımı
   - Monitoring (Prometheus + Grafana)
   - CI/CD pipeline (GitLab CI, Jenkins)
   - Helm Charts
   - Security best practices
   - Production deployment stratejileri

3. 🎯 **Proje Önerileri:**
   - Microservice uygulaması deploy et
   - Database + Backend + Frontend stack kur
   - CI/CD pipeline oluştur
   - Monitoring ekle

---

**Eğitim Tamamlandı! 🎉**

Bu dokümanda bugün öğrendiğiniz tüm konular, pratik örnekler ve komutlar bulunmaktadır. 
Herhangi bir sorunuz olursa bu notu referans olarak kullanabilirsiniz.

**İyi Çalışmalar!** 🚀
