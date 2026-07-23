# Minikube Deployment Script
# Bu script tüm deployment adımlarını otomatikleştirir

Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  🚀 Product Service - Minikube Deployment  " -ForegroundColor Green
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Minikube yolunu tanımla
$minikubePath = "C:\Program Files\Kubernetes\Minikube\minikube.exe"

# Minikube varlığını kontrol et
if (-not (Test-Path $minikubePath)) {
    Write-Host "❌ Minikube bulunamadı: $minikubePath" -ForegroundColor Red
    Write-Host "   Lütfen minikube'un yolunu kontrol edin." -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Minikube bulundu: $minikubePath" -ForegroundColor Green
Write-Host ""

# 1. Minikube durumunu kontrol et
Write-Host "[1/9] Minikube durumu kontrol ediliyor..." -ForegroundColor Yellow
try {
    $minikubeStatus = & $minikubePath status 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Minikube çalışmıyor. Başlatılıyor..." -ForegroundColor Red
        Write-Host "   TLS sertifika sorunları için insecure-registry ile başlatılıyor..." -ForegroundColor Yellow
        & $minikubePath start --cpus=4 --memory=8192 --driver=docker --insecure-registry "docker.io" --insecure-registry "registry-1.docker.io"
        
        # Docker daemon config güncellemesi
        Write-Host "   Docker daemon yapılandırması kontrol ediliyor..." -ForegroundColor Yellow
        & $minikubePath ssh "sudo mkdir -p /etc/docker"
        $dockerConfig = @'
{
  "insecure-registries": ["docker.io", "registry-1.docker.io"],
  "registry-mirrors": []
}
'@
        $dockerConfig | & $minikubePath ssh "sudo tee /etc/docker/daemon.json > /dev/null"
        & $minikubePath ssh "sudo systemctl restart docker"
        Start-Sleep -Seconds 5
    } else {
        Write-Host "✅ Minikube çalışıyor" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Minikube başlatılamadı: $_" -ForegroundColor Red
    exit 1
}

# 2. Kubectl context kontrol et
Write-Host "`n[2/9] Kubectl context kontrol ediliyor..." -ForegroundColor Yellow
$currentContext = kubectl config current-context
Write-Host "   Context: $currentContext" -ForegroundColor Gray
if ($currentContext -ne "minikube") {
    Write-Host "⚠️  Context minikube değil, değiştiriliyor..." -ForegroundColor Yellow
    kubectl config use-context minikube
}

# 3. Gerekli addon'ları aktifleştir
Write-Host "`n[3/9] Minikube addon'ları aktifleştiriliyor..." -ForegroundColor Yellow
& $minikubePath addons enable ingress
& $minikubePath addons enable metrics-server
Write-Host "✅ Addon'lar aktifleştirildi" -ForegroundColor Green

# 4. Docker image build et (Minikube Docker daemon kullanarak)
Write-Host "`n[4/9] Docker image build ediliyor..." -ForegroundColor Yellow
Write-Host "   Minikube Docker environment kullanılıyor..." -ForegroundColor Gray

# Minikube Docker environment'ını ayarla
& $minikubePath -p minikube docker-env --shell powershell | Invoke-Expression

# Build yap
docker build -t product-service:latest -f Dockerfile .

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Docker image başarıyla build edildi" -ForegroundColor Green
} else {
    Write-Host "❌ Docker build hatası!" -ForegroundColor Red
    exit 1
}

# 5. Dependencies (MSSQL ve Redis) deploy et
Write-Host "`n[5/9] MSSQL ve Redis deploy ediliyor..." -ForegroundColor Yellow

# MSSQL deployment
$mssqlExists = kubectl get deployment mssql-deployment 2>&1
if ($LASTEXITCODE -ne 0) {
    kubectl apply -f k8s/dependencies/mssql-deployment.yaml 2>&1 | Out-Null
    Write-Host "   ✓ MSSQL deployed" -ForegroundColor Gray
} else {
    Write-Host "   ✓ MSSQL zaten mevcut" -ForegroundColor Gray
}

# Redis deployment
$redisExists = kubectl get deployment redis-deployment 2>&1
if ($LASTEXITCODE -ne 0) {
    kubectl apply -f k8s/dependencies/redis-deployment.yaml 2>&1 | Out-Null
    Write-Host "   ✓ Redis deployed" -ForegroundColor Gray
} else {
    Write-Host "   ✓ Redis zaten mevcut" -ForegroundColor Gray
}

Write-Host "✅ Dependencies hazır" -ForegroundColor Green

# 6. ConfigMap ve Secret oluştur
Write-Host "`n[6/9] ConfigMap ve Secret oluşturuluyor..." -ForegroundColor Yellow
kubectl apply -f k8s/base/configmap.yaml | Out-Null
kubectl apply -f k8s/base/secret.yaml | Out-Null
Write-Host "✅ ConfigMap ve Secret oluşturuldu" -ForegroundColor Green

# 7. Product Service deploy et
Write-Host "`n[7/9] Product Service deploy ediliyor..." -ForegroundColor Yellow
kubectl apply -f k8s/base/deployment.yaml | Out-Null
kubectl apply -f k8s/base/service.yaml | Out-Null
Write-Host "✅ Product Service deploy edildi" -ForegroundColor Green

# 8. HPA oluştur
Write-Host "`n[8/9] Horizontal Pod Autoscaler yapılandırılıyor..." -ForegroundColor Yellow
kubectl apply -f k8s/hpa.yaml | Out-Null
Write-Host "✅ HPA yapılandırıldı" -ForegroundColor Green

# 9. Deployment'ın hazır olmasını bekle
Write-Host "`n[9/9] Deployment tamamlanması bekleniyor..." -ForegroundColor Yellow
Write-Host "   (Bu birkaç dakika sürebilir...)" -ForegroundColor Gray

kubectl wait --for=condition=available --timeout=300s deployment/product-service 2>&1 | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Deployment başarıyla tamamlandı!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Deployment timeout oldu, lütfen manuel kontrol edin" -ForegroundColor Yellow
}

# Sonuçları göster
Write-Host ""
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  ✅ DEPLOYMENT TAMAMLANDI!  " -ForegroundColor Green
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Service URL'ini al
Write-Host "📍 Service Erişim Bilgileri:" -ForegroundColor Cyan
Write-Host ""

try {
    $serviceUrl = & $minikubePath service product-service-nodeport --url 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   API Base URL:" -ForegroundColor White
        Write-Host "   $serviceUrl" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "   API Documentation (Swagger):" -ForegroundColor White
        Write-Host "   $serviceUrl/api/v1/docs" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "   Health Check:" -ForegroundColor White
        Write-Host "   $serviceUrl/health" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   Service URL alınamadı" -ForegroundColor Red
}

# Pod bilgilerini göster
Write-Host ""
Write-Host "📦 Pod Durumu:" -ForegroundColor Cyan
kubectl get pods -l app=product-service

# Service bilgilerini göster
Write-Host ""
Write-Host "🌐 Service Durumu:" -ForegroundColor Cyan
kubectl get services

# HPA durumu
Write-Host ""
Write-Host "📊 HPA Durumu:" -ForegroundColor Cyan
kubectl get hpa

# Faydalı komutlar
Write-Host ""
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  📖 Faydalı Komutlar  " -ForegroundColor Magenta
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Pod Logları:" -ForegroundColor White
Write-Host "  kubectl logs -f deployment/product-service" -ForegroundColor Gray
Write-Host ""
Write-Host "  Dashboard Aç:" -ForegroundColor White
Write-Host "  minikube dashboard" -ForegroundColor Gray
Write-Host ""
Write-Host "  Service Browser'da Aç:" -ForegroundColor White
Write-Host "  minikube service product-service-nodeport" -ForegroundColor Gray
Write-Host ""
Write-Host "  Port Forward:" -ForegroundColor White
Write-Host "  kubectl port-forward service/product-service 8080:80" -ForegroundColor Gray
Write-Host ""
Write-Host "  Tüm Kaynakları Sil:" -ForegroundColor White
Write-Host "  kubectl delete -f k8s/base/" -ForegroundColor Gray
Write-Host ""
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan

# Browser'da aç mı?
Write-Host ""
$openBrowser = Read-Host "API Documentation'ı browser'da açmak ister misiniz? (E/H)"
if ($openBrowser -eq "E" -or $openBrowser -eq "e") {
    try {
        $serviceUrl = & $minikubePath service product-service-nodeport --url
        Start-Process "$serviceUrl/api/v1/docs"
        Write-Host "✅ Browser açıldı!" -ForegroundColor Green
    } catch {
        Write-Host "❌ Browser açılamadı" -ForegroundColor Red
    }
}

# Port forward başlat mı?
Write-Host ""
$startPortForward = Read-Host "Localhost:8080 üzerinden port-forward başlatmak ister misiniz? (E/H)"
if ($startPortForward -eq "E" -or $startPortForward -eq "e") {
    Write-Host ""
    Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "  🌐 Port Forward Başlatılıyor  " -ForegroundColor Green
    Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "🌐 Localhost Adresleri:" -ForegroundColor Cyan
    Write-Host "   Swagger UI:    http://localhost:8080/api/v1/docs" -ForegroundColor Green
    Write-Host "   Health Check:  http://localhost:8080/health" -ForegroundColor Green
    Write-Host "   Metrics:       http://localhost:8080/metrics" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠️  CTRL+C ile durdurun" -ForegroundColor Yellow
    Write-Host ""
    
    # 3 saniye bekle
    Start-Sleep -Seconds 3
    
    # Port forward başlat
    kubectl port-forward service/product-service 8080:80
}

Write-Host ""
Write-Host "🎉 İyi çalışmalar!" -ForegroundColor Green
Write-Host ""
