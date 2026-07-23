# Run Alembic Migrations - Database Schema Setup
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  📊 Alembic Migrations  " -ForegroundColor Green
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# 1. Application pod'unu bul
Write-Host "[1/3] Application pod bulunuyor..." -ForegroundColor Yellow
$podName = kubectl get pods -l app=product-service -o jsonpath='{.items[0].metadata.name}' 2>$null

if ([string]::IsNullOrEmpty($podName)) {
    Write-Host "❌ Application pod bulunamadı!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Pod bulundu: $podName" -ForegroundColor Green

# 2. Migration durumunu kontrol et
Write-Host "`n[2/3] Mevcut migration durumu kontrol ediliyor..." -ForegroundColor Yellow
Write-Host "   Current revision:" -ForegroundColor Gray
kubectl exec $podName -- alembic current

Write-Host "`n   Migration history:" -ForegroundColor Gray
kubectl exec $podName -- alembic history

# 3. Migrations çalıştır
Write-Host "`n[3/3] Migrations çalıştırılıyor (upgrade head)..." -ForegroundColor Yellow
kubectl exec $podName -- alembic upgrade head

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Migrations başarıyla uygulandı!" -ForegroundColor Green
} else {
    Write-Host "❌ Migration hatası!" -ForegroundColor Red
    Write-Host "`n📋 Pod logları:" -ForegroundColor Yellow
    kubectl logs $podName --tail=30
    exit 1
}

Write-Host "`n════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  ✅ Database Schema Hazır!  " -ForegroundColor Green
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# 4. Son durumu göster
Write-Host "📊 Final migration durumu:" -ForegroundColor Cyan
kubectl exec $podName -- alembic current

Write-Host "`n🌐 API erişim:" -ForegroundColor Cyan
Write-Host "   Port Forward: .\port-forward.ps1" -ForegroundColor Yellow
Write-Host "   Swagger UI: http://localhost:8080/api/v1/docs" -ForegroundColor Green
Write-Host ""
