# Offline Minikube Deployment Script
# Bu script image'ı host makinede build edip Minikube'a transfer eder

Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  📦 Offline Minikube Deployment (Host Build)  " -ForegroundColor Green
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "Bu yöntem host makinenizin Docker Desktop'ını kullanır." -ForegroundColor Yellow
Write-Host "Host makinenizde internet bağlantısı ve Docker Desktop çalışıyor olmalı." -ForegroundColor Yellow
Write-Host ""

$minikubePath = "C:\Program Files\Kubernetes\Minikube\minikube.exe"
$imageName = "product-service"
$imageTag = "latest"
$fullImageName = "${imageName}:${imageTag}"

# Docker Desktop kontrolü
Write-Host "[0/6] Docker Desktop durumu kontrol ediliyor..." -ForegroundColor Yellow
docker info 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker Desktop çalışmıyor!" -ForegroundColor Red
    Write-Host "   Lütfen Docker Desktop'ı başlatın ve tekrar deneyin." -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Docker Desktop çalışıyor" -ForegroundColor Green

# 1. Host makinede Docker build
Write-Host "`n[1/6] Image host makinede build ediliyor..." -ForegroundColor Yellow
Write-Host "   Bu işlem host makinenizin internet bağlantısını kullanacak..." -ForegroundColor Gray
docker build -t $fullImageName . 2>&1 | Write-Host

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n❌ Docker build başarısız!" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Image başarıyla build edildi" -ForegroundColor Green

# 2. Image'ı tar dosyasına export et
Write-Host "`n[2/6] Image tar dosyasına export ediliyor..." -ForegroundColor Yellow
$tarPath = "$env:TEMP\${imageName}.tar"
docker save -o $tarPath $fullImageName 2>&1 | Write-Host
Write-Host "✅ Image export edildi: $tarPath" -ForegroundColor Green

# 3. Tar dosyasını Minikube'a load et
Write-Host "`n[3/6] Image Minikube'a yükleniyor..." -ForegroundColor Yellow
& $minikubePath image load $tarPath
Write-Host "✅ Image Minikube'a yüklendi" -ForegroundColor Green

# 4. Tar dosyasını temizle
Write-Host "`n[4/6] Geçici dosyalar temizleniyor..." -ForegroundColor Yellow
Remove-Item $tarPath -ErrorAction SilentlyContinue
Write-Host "✅ Temizleme tamamlandı" -ForegroundColor Green

# 5. Image'ın yüklendiğini doğrula
Write-Host "`n[5/6] Image doğrulanıyor..." -ForegroundColor Yellow
& $minikubePath image ls | Select-String $imageName
Write-Host "✅ Image Minikube'da mevcut" -ForegroundColor Green

# 6. Dependencies ve app deploy et
Write-Host "`n[6/6] Kubernetes deployment yapılıyor..." -ForegroundColor Yellow

# ConfigMap ve Secret oluştur
Write-Host "   ConfigMap ve Secret oluşturuluyor..." -ForegroundColor Gray
kubectl apply -f k8s/base/configmap.yaml
kubectl apply -f k8s/base/secret.yaml

# Dependencies deploy et
Write-Host "   Dependencies deploy ediliyor (MSSQL, Redis)..." -ForegroundColor Gray
kubectl apply -f k8s/dependencies/

# Dependencies hazır olana kadar bekle
Write-Host "   Dependencies hazır olması bekleniyor..." -ForegroundColor Gray
kubectl wait --for=condition=ready pod -l app=mssql --timeout=120s
kubectl wait --for=condition=ready pod -l app=redis --timeout=60s

# Application deploy et
Write-Host "   Application deploy ediliyor..." -ForegroundColor Gray
kubectl apply -f k8s/base/deployment.yaml
kubectl apply -f k8s/base/service.yaml
kubectl apply -f k8s/base/hpa.yaml

# Application hazır olana kadar bekle
Write-Host "   Application hazır olması bekleniyor..." -ForegroundColor Gray
kubectl wait --for=condition=available deployment/product-service --timeout=180s

Write-Host "✅ Deployment tamamlandı" -ForegroundColor Green

Write-Host "`n════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  ✅ Offline deployment tamamlandı!  " -ForegroundColor Green
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Service URL'ini al ve göster
Write-Host "🌐 Servis bilgileri:" -ForegroundColor Cyan
$serviceUrl = & $minikubePath service product-service-nodeport --url
Write-Host "   API URL: $serviceUrl" -ForegroundColor Green
Write-Host "   Swagger Docs: $serviceUrl/api/v1/docs" -ForegroundColor Green
Write-Host "   Health Check: $serviceUrl/health" -ForegroundColor Green
Write-Host ""

Write-Host "📊 Monitoring komutları:" -ForegroundColor Cyan
Write-Host "   kubectl get pods" -ForegroundColor Gray
Write-Host "   kubectl logs -f deployment/product-service" -ForegroundColor Gray
Write-Host "   kubectl get hpa" -ForegroundColor Gray
Write-Host "   minikube dashboard" -ForegroundColor Gray
Write-Host ""

# Tarayıcıda aç
$openBrowser = Read-Host "Swagger UI'ı tarayıcıda açmak ister misiniz? (E/H)"
if ($openBrowser -eq "E" -or $openBrowser -eq "e") {
    Start-Process "$serviceUrl/api/v1/docs"
}
