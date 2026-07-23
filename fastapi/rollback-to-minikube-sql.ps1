# Rollback to Minikube SQL Server - Host SQL'den Minikube SQL'e dön
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  🔄 Minikube SQL Server'a Geri Dön  " -ForegroundColor Green
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$minikubePath = "C:\Program Files\Kubernetes\Minikube\minikube.exe"

# 1. ConfigMap ve Secret'ı güncelle
Write-Host "[1/6] ConfigMap ve Secret Minikube için güncelleniyor..." -ForegroundColor Yellow
kubectl apply -f k8s/base/configmap.yaml
kubectl apply -f k8s/base/secret.yaml
Write-Host "✅ Konfigürasyon güncellendi" -ForegroundColor Green
Write-Host "   database_host: mssql-service.default.svc.cluster.local" -ForegroundColor Gray

# 2. MSSQL deployment'ını başlat
Write-Host "`n[2/6] Minikube MSSQL deployment başlatılıyor..." -ForegroundColor Yellow
kubectl scale deployment mssql-deployment --replicas=1
Write-Host "✅ MSSQL deployment başlatıldı" -ForegroundColor Green

# 3. MSSQL pod'unun hazır olmasını bekle
Write-Host "`n[3/6] MSSQL pod hazır olması bekleniyor..." -ForegroundColor Yellow
kubectl wait --for=condition=ready pod -l app=mssql --timeout=120s

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ MSSQL pod hazır" -ForegroundColor Green
} else {
    Write-Host "⚠️  MSSQL pod timeout, devam ediliyor..." -ForegroundColor Yellow
}

Start-Sleep -Seconds 5

# 4. Database'i kontrol et ve oluştur
Write-Host "`n[4/6] ProductManagementDB database kontrol ediliyor..." -ForegroundColor Yellow
$mssqlPod = kubectl get pods -l app=mssql -o jsonpath='{.items[0].metadata.name}' 2>$null

if (-not [string]::IsNullOrEmpty($mssqlPod)) {
    $createDbSql = @"
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'ProductManagementDB')
BEGIN
    CREATE DATABASE ProductManagementDB;
    PRINT 'Database created';
END
ELSE
BEGIN
    PRINT 'Database already exists';
END
GO
"@
    
    $createDbSql | kubectl exec -i $mssqlPod -- /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P 'Az.123456+' -C
    Write-Host "✅ Database hazır: ProductManagementDB" -ForegroundColor Green
} else {
    Write-Host "⚠️  MSSQL pod bulunamadı" -ForegroundColor Yellow
}

# 5. Application deployment'ını restart et
Write-Host "`n[5/6] Application deployment restart ediliyor..." -ForegroundColor Yellow
kubectl rollout restart deployment/product-service
Write-Host "✅ Deployment restart edildi" -ForegroundColor Green

# 6. Deployment'ın hazır olmasını bekle
Write-Host "`n[6/6] Application hazır olması bekleniyor..." -ForegroundColor Yellow
kubectl rollout status deployment/product-service --timeout=180s

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Application hazır" -ForegroundColor Green
} else {
    Write-Host "⚠️  Deployment timeout, logları kontrol edin" -ForegroundColor Yellow
}

Write-Host "`n════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  ✅ Minikube SQL Server'a Dönüldü!  " -ForegroundColor Green
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Pod durumu
Write-Host "📦 Pod Durumu:" -ForegroundColor Cyan
kubectl get pods

Write-Host "`n🗄️  Database Bağlantısı:" -ForegroundColor Cyan
Write-Host "   Host: mssql-service.default.svc.cluster.local" -ForegroundColor Gray
Write-Host "   Port: 1433" -ForegroundColor Gray
Write-Host "   Database: ProductManagementDB" -ForegroundColor Gray
Write-Host "   Username: sa" -ForegroundColor Gray
Write-Host "   Password: Az.123456+" -ForegroundColor Gray

Write-Host "`n📋 Application Logları:" -ForegroundColor Cyan
kubectl logs -l app=product-service --tail=20

Write-Host "`n💡 Migrations Çalıştırın:" -ForegroundColor Cyan
Write-Host "   .\run-migrations.ps1" -ForegroundColor Yellow

Write-Host "`n🌐 Port Forward:" -ForegroundColor Cyan
Write-Host "   .\port-forward.ps1" -ForegroundColor Yellow
Write-Host "   http://localhost:8080/api/v1/docs" -ForegroundColor Green
Write-Host ""
