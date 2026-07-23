# MSSQL Readiness Check - MSSQL tam hazır olana kadar bekle
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  ⏳ MSSQL Hazırlık Kontrolü  " -ForegroundColor Green
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# 1. MSSQL pod durumunu kontrol et
Write-Host "[1/5] MSSQL pod durumu kontrol ediliyor..." -ForegroundColor Yellow
$mssqlPod = kubectl get pods -l app=mssql -o jsonpath='{.items[0].metadata.name}' 2>$null

if ([string]::IsNullOrEmpty($mssqlPod)) {
    Write-Host "❌ MSSQL pod bulunamadı!" -ForegroundColor Red
    Write-Host "   MSSQL deployment başlatılıyor..." -ForegroundColor Yellow
    kubectl scale deployment mssql-deployment --replicas=1
    Start-Sleep -Seconds 10
    $mssqlPod = kubectl get pods -l app=mssql -o jsonpath='{.items[0].metadata.name}' 2>$null
}

Write-Host "✅ MSSQL pod: $mssqlPod" -ForegroundColor Green

# 2. Pod'un Running olmasını bekle
Write-Host "`n[2/5] MSSQL pod Running olması bekleniyor..." -ForegroundColor Yellow
$maxWait = 120
$waited = 0
$interval = 5

while ($waited -lt $maxWait) {
    $podStatus = kubectl get pod $mssqlPod -o jsonpath='{.status.phase}' 2>$null
    
    if ($podStatus -eq "Running") {
        Write-Host "✅ Pod Running durumda" -ForegroundColor Green
        break
    }
    
    Write-Host "   Pod status: $podStatus - Bekleniyor... ($waited/$maxWait saniye)" -ForegroundColor Gray
    Start-Sleep -Seconds $interval
    $waited += $interval
}

# 3. MSSQL'in hazır olmasını bekle (SQL bağlantısı)
Write-Host "`n[3/5] MSSQL servisi hazır olması bekleniyor (SQL bağlantısı)..." -ForegroundColor Yellow
$maxAttempts = 30
$attempt = 0

while ($attempt -lt $maxAttempts) {
    $attempt++
    Write-Host "   Deneme $attempt/$maxAttempts - SQL bağlantısı test ediliyor..." -ForegroundColor Gray
    
    $testSql = "SELECT @@VERSION;"
    $result = $testSql | kubectl exec -i $mssqlPod -- /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P 'Az.123456+' -C -h -1 2>$null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ MSSQL hazır ve bağlantı kabul ediyor!" -ForegroundColor Green
        break
    }
    
    Start-Sleep -Seconds 5
}

if ($attempt -ge $maxAttempts) {
    Write-Host "❌ MSSQL bağlantısı kurulamadı!" -ForegroundColor Red
    Write-Host "`n📋 MSSQL Logları:" -ForegroundColor Yellow
    kubectl logs $mssqlPod --tail=30
    exit 1
}

# 4. Database oluştur veya kontrol et
Write-Host "`n[4/5] ProductManagementDB database kontrol ediliyor..." -ForegroundColor Yellow
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

$createDbSql | kubectl exec -i $mssqlPod -- /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P 'Az.123456+' -C

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Database hazır: ProductManagementDB" -ForegroundColor Green
} else {
    Write-Host "⚠️  Database oluşturma hatası" -ForegroundColor Yellow
}

# Database'in gerçekten var olduğunu doğrula
$checkDbSql = "SELECT name FROM sys.databases WHERE name = 'ProductManagementDB';"
$dbExists = $checkDbSql | kubectl exec -i $mssqlPod -- /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P 'Az.123456+' -C -h -1 2>$null

if ($dbExists -match "ProductManagementDB") {
    Write-Host "✅ Database doğrulandı" -ForegroundColor Green
} else {
    Write-Host "❌ Database bulunamadı!" -ForegroundColor Red
    exit 1
}

# 5. Application pod'larını restart et
Write-Host "`n[5/5] Application pod'ları restart ediliyor..." -ForegroundColor Yellow
kubectl rollout restart deployment/product-service
Write-Host "✅ Restart komutu gönderildi" -ForegroundColor Green

# Biraz bekle
Write-Host "`n⏳ Application pod'ların yeniden başlaması bekleniyor (30 saniye)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

Write-Host "`n════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  ✅ MSSQL Hazır!  " -ForegroundColor Green
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Pod durumunu göster
Write-Host "📦 Pod Durumu:" -ForegroundColor Cyan
kubectl get pods

Write-Host "`n🗄️  MSSQL Bağlantı Bilgileri:" -ForegroundColor Cyan
Write-Host "   Host: mssql-service.default.svc.cluster.local" -ForegroundColor Gray
Write-Host "   Port: 1433" -ForegroundColor Gray
Write-Host "   Database: ProductManagementDB" -ForegroundColor Gray
Write-Host "   Username: sa" -ForegroundColor Gray

Write-Host "`n📋 Application Logları:" -ForegroundColor Cyan
kubectl logs -l app=product-service --tail=25

Write-Host "`n💡 Sonraki Adımlar:" -ForegroundColor Cyan
Write-Host "   1. Migrations çalıştır: .\run-migrations.ps1" -ForegroundColor Yellow
Write-Host "   2. Port forward başlat: .\port-forward.ps1" -ForegroundColor Yellow
Write-Host "   3. Swagger UI: http://localhost:8080/api/v1/docs" -ForegroundColor Green
Write-Host ""
