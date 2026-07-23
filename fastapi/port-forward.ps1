# Port Forward Script - Localhost'tan Minikube'a Erişim
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  🌐 Port Forward - Localhost:8080  " -ForegroundColor Green
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Port forward başlat
Write-Host "Port forward başlatılıyor..." -ForegroundColor Yellow
Write-Host "   Local:  http://localhost:8080" -ForegroundColor Green
Write-Host "   Target: product-service:80 -> container:8000" -ForegroundColor Gray
Write-Host ""
Write-Host "🌐 Erişim Adresleri:" -ForegroundColor Cyan
Write-Host "   Swagger UI:    http://localhost:8080/api/v1/docs" -ForegroundColor Green
Write-Host "   Health Check:  http://localhost:8080/health" -ForegroundColor Green
Write-Host "   Metrics:       http://localhost:8080/metrics" -ForegroundColor Green
Write-Host ""
Write-Host "⚠️  CTRL+C ile durdurun" -ForegroundColor Yellow
Write-Host ""

# Port forward komutunu çalıştır
kubectl port-forward service/product-service 8080:80
