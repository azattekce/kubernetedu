# Kubernetes Eğitim Projesi

Bu proje, Kubernetes'in temel kavramlarını ve uygulama dağıtım senaryolarını öğrenmek için hazırlanmış kapsamlı bir eğitim materyalidir.

## 📋 İçindekiler

- [Proje Yapısı](#proje-yapısı)
- [Önkoşullar](#önkoşullar)
- [Demo Uygulamaları](#demo-uygulamaları)
  - [WordPress ve MySQL](#wordpress-ve-mysql)
  - [NGINX Development](#nginx-development)
- [Kubernetes Kavramları](#kubernetes-kavramları)
- [Kullanım](#kullanım)
- [Faydalı Komutlar](#faydalı-komutlar)

## 📁 Proje Yapısı

```
Edu/
├── Demo/                    # WordPress ve MySQL demo uygulamaları
│   ├── mysql-*.yml         # MySQL deployment ve servis tanımları
│   ├── wordpress-*.yml     # WordPress deployment ve servis tanımları
│   └── README-WordPress.md # WordPress kurulum kılavuzu
├── nginx/                   # NGINX development ortamı
│   ├── nginx-dev-deployment.yml
│   ├── nginx-dev-service.yml
│   ├── nginx-dev-pv-claim.yml
│   └── nginx-dev-ns.yml
└── wp/                      # Detaylı WordPress çözümü
    ├── frontend/           # WordPress frontend tanımları
    └── mysql/              # MySQL backend tanımları
```

## 🔧 Önkoşullar

Projeyi çalıştırmadan önce aşağıdaki araçların sisteminizde kurulu olması gerekmektedir:

- **kubectl**: Kubernetes komut satırı aracı
- **Kubernetes Cluster**: 
  - Minikube (yerel geliştirme için)
  - Docker Desktop Kubernetes
  - veya herhangi bir Kubernetes cluster
- **Docker**: Container runtime
- **Git**: Versiyon kontrolü (opsiyonel)

### Kurulum Kontrolü

```bash
# kubectl versiyonunu kontrol et
kubectl version --client

# Cluster bağlantısını kontrol et
kubectl cluster-info

# Node'ları listele
kubectl get nodes
```

## 🚀 Demo Uygulamaları

### WordPress ve MySQL

WordPress blog platformu ve MySQL veritabanı kullanarak tam bir web uygulaması deployment örneği.

#### Özellikler:
- ✅ Persistent Volume (PV) ve Persistent Volume Claim (PVC) kullanımı
- ✅ Secret yönetimi (MySQL şifreleri)
- ✅ Service discovery (WordPress'ten MySQL'e bağlantı)
- ✅ NodePort ile dış erişim
- ✅ Namespace izolasyonu

#### Hızlı Başlangıç:

```bash
# Namespace oluştur
kubectl apply -f Demo/wordpress-namespace.yml

# MySQL'i dağıt
kubectl apply -f Demo/mysql-secret.yml
kubectl apply -f Demo/mysql-pvc.yml
kubectl apply -f Demo/mysql-deployment.yml
kubectl apply -f Demo/mysql-service.yml

# WordPress'i dağıt
kubectl apply -f Demo/wordpress-pvc.yml
kubectl apply -f Demo/wordpress-deployment.yml
kubectl apply -f Demo/wordpress-service.yml

# Veya tümünü tek seferde:
kubectl apply -f Demo/wordpress-complete.yml
```

#### Erişim:

```bash
# Service'in NodePort'unu öğren
kubectl get service wordpress -n wordpress

# Minikube kullanıyorsanız:
minikube service wordpress -n wordpress
```

### NGINX Development

Development ortamı için NGINX web sunucusu kurulumu.

#### Özellikler:
- ✅ Custom namespace (azdevops)
- ✅ Persistent Volume kullanımı
- ✅ NodePort service
- ✅ Development ortamı için optimize edilmiş

#### Kurulum:

```bash
# Namespace oluştur
kubectl apply -f nginx/nginx-dev-ns.yml

# PVC oluştur
kubectl apply -f nginx/nginx-dev-pv-claim.yml

# NGINX deployment
kubectl apply -f nginx/nginx-dev-deployment.yml

# Service oluştur
kubectl apply -f nginx/nginx-dev-service.yml

# Kontrol et
kubectl get all -n azdevops
```

## 📚 Kubernetes Kavramları

Bu projede kullanılan temel Kubernetes kavramları:

### Pod
- En küçük deployment birimi
- Bir veya daha fazla container barındırır
- Geçici (ephemeral) yapıdadır

### Deployment
- Pod'ların yaşam döngüsünü yönetir
- Replica sayısını kontrol eder
- Rolling update ve rollback özellikleri
- Self-healing (otomatik yeniden başlatma)

### Service
- Pod'lara network erişimi sağlar
- Service discovery
- Load balancing
- **ClusterIP**: Cluster içi erişim
- **NodePort**: Cluster dışından erişim
- **LoadBalancer**: Cloud provider load balancer

### Persistent Volume (PV) & Persistent Volume Claim (PVC)
- Kalıcı veri saklama
- Pod'lardan bağımsız yaşam döngüsü
- Stateful uygulamalar için kritik

### Namespace
- Kaynak izolasyonu
- Çoklu ortam desteği (dev, test, prod)
- RBAC (Role-Based Access Control) için temel

### Secret
- Hassas bilgilerin güvenli saklanması
- Şifreler, API anahtarları, sertifikalar
- Base64 encoded

### ConfigMap
- Uygulama yapılandırma verileri
- Environment variables
- Configuration files

## 💻 Kullanım

### Tüm Kaynakları Görüntüleme

```bash
# Tüm namespace'lerdeki pod'ları listele
kubectl get pods --all-namespaces

# Belirli bir namespace'teki tüm kaynakları listele
kubectl get all -n wordpress
kubectl get all -n azdevops

# Persistent volume'ları listele
kubectl get pv
kubectl get pvc --all-namespaces
```

### Log Kontrolü

```bash
# Pod loglarını görüntüle
kubectl logs <pod-name> -n <namespace>

# Canlı log takibi
kubectl logs -f <pod-name> -n <namespace>

# Önceki container'ın logları (crash durumunda)
kubectl logs <pod-name> -n <namespace> --previous
```

### Hata Ayıklama

```bash
# Pod detaylarını görüntüle
kubectl describe pod <pod-name> -n <namespace>

# Service detaylarını görüntüle
kubectl describe service <service-name> -n <namespace>

# Pod'a shell erişimi
kubectl exec -it <pod-name> -n <namespace> -- /bin/bash

# Port forwarding (local testing)
kubectl port-forward <pod-name> 8080:80 -n <namespace>
```

### Kaynak Silme

```bash
# Belirli bir kaynağı sil
kubectl delete -f <dosya.yml>

# Namespace ve içindeki tüm kaynakları sil
kubectl delete namespace <namespace-name>

# Tüm pod'ları sil (namespace içinde)
kubectl delete pods --all -n <namespace>
```

## 🔍 Faydalı Komutlar

### Cluster Durumu

```bash
# Cluster bilgisi
kubectl cluster-info

# Node durumu
kubectl get nodes -o wide

# Namespace'leri listele
kubectl get namespaces

# Tüm API kaynaklarını listele
kubectl api-resources
```

### YAML Doğrulama

```bash
# YAML syntax kontrolü
kubectl apply --dry-run=client -f <dosya.yml>

# Server-side doğrulama
kubectl apply --dry-run=server -f <dosya.yml>

# YAML'ı görüntüle
kubectl get <resource> <name> -n <namespace> -o yaml
```

### Performans İzleme

```bash
# Node kaynak kullanımı
kubectl top nodes

# Pod kaynak kullanımı
kubectl top pods -n <namespace>

# Tüm namespace'lerdeki pod kaynak kullanımı
kubectl top pods --all-namespaces
```

## 🎓 Öğrenme Yolu

1. **Başlangıç**: NGINX deployment ile başlayın
   - Temel pod, deployment, service kavramlarını öğrenin
   
2. **Orta Seviye**: WordPress + MySQL
   - Çoklu container deployment
   - Service discovery
   - Secret ve PVC kullanımı
   
3. **İleri Seviye**: 
   - ConfigMap kullanımı
   - Health checks (liveness, readiness probes)
   - Resource limits ve requests
   - Horizontal Pod Autoscaling

## 📖 Ek Kaynaklar

- [Kubernetes Resmi Dokümantasyonu](https://kubernetes.io/docs/)
- [Kubernetes Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)

## 🤝 Katkıda Bulunma

Bu bir eğitim projesidir. İyileştirme önerileriniz için:
1. Yeni örnekler ekleyin
2. Dokümantasyonu geliştirin
3. Hataları düzeltin

## 📝 Notlar

- **Güvenlik**: Production ortamında Secret'ları kesinlikle external secret management (Azure Key Vault, AWS Secrets Manager, HashiCorp Vault) kullanarak yönetin
- **Monitoring**: Production için Prometheus + Grafana gibi monitoring çözümleri kullanın
- **Backup**: Persistent Volume'ların düzenli yedeklerini alın
- **Resource Limits**: Her zaman CPU ve memory limits tanımlayın

## 📄 Lisans

Bu proje eğitim amaçlıdır ve özgürce kullanılabilir.

---

**Not**: Bu proje Kubernetes öğrenmek için hazırlanmıştır. Production kullanımı için ek güvenlik ve performans optimizasyonları gereklidir.
