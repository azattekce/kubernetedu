# MSSQL Port Forward - SSMS Bağlantısı için
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  🗄️  MSSQL Port Forward (SSMS Bağlantısı)  " -ForegroundColor Green
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# MSSQL service kontrolü
Write-Host "MSSQL service kontrol ediliyor..." -ForegroundColor Yellow
$mssqlService = kubectl get svc mssql-service -o jsonpath='{.metadata.name}' 2>$null

if ([string]::IsNullOrEmpty($mssqlService)) {
    Write-Host "❌ MSSQL service bulunamadı!" -ForegroundColor Red
    Write-Host "   kubectl get svc" -ForegroundColor Gray
    exit 1
}

Write-Host "✅ MSSQL service bulundu: $mssqlService" -ForegroundColor Green
Write-Host ""

# Port forward başlat
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  🌐 Port Forward Başlatılıyor  " -ForegroundColor Green
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "📍 Bağlantı Bilgileri (SQL Server Management Studio):" -ForegroundColor Cyan
Write-Host ""
Write-Host "   Server name:     localhost,1433" -ForegroundColor Green
Write-Host "                    (veya 127.0.0.1,1433)" -ForegroundColor Gray
Write-Host ""
Write-Host "   Authentication:  SQL Server Authentication" -ForegroundColor Green
Write-Host "   Login:           sa" -ForegroundColor Green
Write-Host "   Password:        Az.123456+" -ForegroundColor Green
Write-Host ""
Write-Host "   Database:        ProductManagementDB" -ForegroundColor Yellow
Write-Host ""
Write-Host "💡 Encryption Settings:" -ForegroundColor Cyan
Write-Host "   Options > Connection Properties > Encryption:" -ForegroundColor Gray
Write-Host "   - Optional (Önerilen)" -ForegroundColor Gray
Write-Host "   VEYA" -ForegroundColor Gray
Write-Host "   - Mandatory ile 'Trust server certificate' işaretleyin" -ForegroundColor Gray
Write-Host ""
Write-Host "⚠️  Bu terminal açık kalmalı! CTRL+C ile durdurun." -ForegroundColor Yellow
Write-Host ""
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Port forward komutu
kubectl port-forward svc/mssql-service 1433:1433
