# Quick Rebuild Script - Image'ı yeniden build et ve deployment'ı restart et
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  🔄 Quick Rebuild & Restart  " -ForegroundColor Green
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$minikubePath = "C:\Program Files\Kubernetes\Minikube\minikube.exe"

# 1. Minikube Docker env kullan
Write-Host "[1/4] Minikube Docker environment hazırlanıyor..." -ForegroundColor Yellow
& $minikubePath docker-env | Invoke-Expression
Write-Host "✅ Docker environment hazır" -ForegroundColor Green

# 2. Image'ı yeniden build et
Write-Host "`n[2/4] Docker image yeniden build ediliyor..." -ForegroundColor Yellow
Write-Host "   (email-validator paketi ekleniyor...)" -ForegroundColor Gray
docker build --no-cache -t product-service:latest .

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n❌ Docker build başarısız!" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Image başarıyla build edildi" -ForegroundColor Green

# 3. Mevcut deployment'ı sil
Write-Host "`n[3/4] Mevcut deployment siliniyor..." -ForegroundColor Yellow
kubectl delete deployment product-service
Start-Sleep -Seconds 3
Write-Host "✅ Deployment silindi" -ForegroundColor Green

# 4. Yeni deployment oluştur
Write-Host "`n[4/4] Yeni deployment oluşturuluyor..." -ForegroundColor Yellow
kubectl apply -f k8s/base/deployment.yaml

# Deployment'ın hazır olmasını bekle
Write-Host "   Deployment hazır olması bekleniyor..." -ForegroundColor Gray
kubectl wait --for=condition=available deployment/product-service --timeout=180s

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Deployment başarılı!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Deployment timeout, logları kontrol edin" -ForegroundColor Yellow
}

Write-Host "`n════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  ✅ Rebuild ve Restart Tamamlandı!  " -ForegroundColor Green
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Pod durumunu göster
Write-Host "📦 Pod Durumu:" -ForegroundColor Cyan
kubectl get pods -l app=product-service

Write-Host "`n📋 Son 20 satır log:" -ForegroundColor Cyan
kubectl logs -l app=product-service --tail=20

Write-Host "`n🌐 Port Forward Başlatmak İçin:" -ForegroundColor Cyan
Write-Host "   .\port-forward.ps1" -ForegroundColor Yellow
Write-Host ""
