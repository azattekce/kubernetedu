# Database Setup Script - MSSQL Database ve Migrations
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  🗄️  Database Setup - MSSQL  " -ForegroundColor Green
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# 1. MSSQL pod'unu kontrol et
Write-Host "[1/4] MSSQL pod durumu kontrol ediliyor..." -ForegroundColor Yellow
$mssqlPod = kubectl get pods -l app=mssql -o jsonpath='{.items[0].metadata.name}' 2>$null

if ([string]::IsNullOrEmpty($mssqlPod)) {
    Write-Host "❌ MSSQL pod bulunamadı!" -ForegroundColor Red
    Write-Host "   Önce dependencies deploy edin:" -ForegroundColor Yellow
    Write-Host "   kubectl apply -f k8s/dependencies/" -ForegroundColor Cyan
    exit 1
}

Write-Host "✅ MSSQL pod bulundu: $mssqlPod" -ForegroundColor Green

# Pod ready olmasını bekle
Write-Host "   MSSQL pod hazır olması bekleniyor..." -ForegroundColor Gray
kubectl wait --for=condition=ready pod/$mssqlPod --timeout=120s
Write-Host "✅ MSSQL pod hazır" -ForegroundColor Green

# 2. Database oluştur
Write-Host "`n[2/4] ProductManagementDB database oluşturuluyor..." -ForegroundColor Yellow
$createDbSql = @"
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'ProductManagementDB')
BEGIN
    CREATE DATABASE ProductManagementDB;
    PRINT 'Database created successfully';
END
ELSE
BEGIN
    PRINT 'Database already exists';
END
GO
"@

# SQL komutunu MSSQL pod'una gönder
$createDbSql | kubectl exec -i $mssqlPod -- /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P 'YourStrongPassword123!' -C

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Database oluşturuldu: ProductManagementDB" -ForegroundColor Green
} else {
    Write-Host "⚠️  Database oluşturma hatası (zaten var olabilir)" -ForegroundColor Yellow
}

# 3. Database'i doğrula
Write-Host "`n[3/4] Database doğrulanıyor..." -ForegroundColor Yellow
$checkDbSql = "SELECT name FROM sys.databases WHERE name = 'ProductManagementDB';"
$checkResult = $checkDbSql | kubectl exec -i $mssqlPod -- /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P 'YourStrongPassword123!' -C -h -1

if ($checkResult -match "ProductManagementDB") {
    Write-Host "✅ Database mevcut ve erişilebilir" -ForegroundColor Green
} else {
    Write-Host "❌ Database doğrulanamadı!" -ForegroundColor Red
    exit 1
}

# 4. Application pod'ları restart et
Write-Host "`n[4/4] Application pod'ları restart ediliyor..." -ForegroundColor Yellow
kubectl rollout restart deployment/product-service
kubectl rollout status deployment/product-service --timeout=120s

Write-Host "`n════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  ✅ Database Setup Tamamlandı!  " -ForegroundColor Green
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Pod durumunu göster
Write-Host "📦 Pod Durumu:" -ForegroundColor Cyan
kubectl get pods

Write-Host "`n📋 Application Logları:" -ForegroundColor Cyan
kubectl logs -l app=product-service --tail=20

Write-Host "`n✅ Database hazır! Alembic migrations çalıştırabilirsiniz." -ForegroundColor Green
Write-Host ""
