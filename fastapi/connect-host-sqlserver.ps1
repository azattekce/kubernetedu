# Connect to Host SQL Server - Host makinedeki SQL Server'a bağlan
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  🔌 Host SQL Server Bağlantısı  " -ForegroundColor Green
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

Write-Host "📋 Bağlantı Bilgileri:" -ForegroundColor Yellow
Write-Host "   Host: localhost (host.minikube.internal)" -ForegroundColor Gray
Write-Host "   Port: 1433" -ForegroundColor Gray
Write-Host "   Database: ProductManagementDB" -ForegroundColor Gray
Write-Host "   Username: sa" -ForegroundColor Gray
Write-Host ""

# 1. Minikube MSSQL deployment'ını kapat
Write-Host "[1/6] Minikube içindeki MSSQL pod'u kapatılıyor..." -ForegroundColor Yellow
kubectl scale deployment mssql-deployment --replicas=0 2>$null
Write-Host "✅ MSSQL pod kapatıldı (host SQL Server kullanılacak)" -ForegroundColor Green

# 2. ConfigMap ve Secret'ı güncelle
Write-Host "`n[2/6] ConfigMap ve Secret güncelleniyor..." -ForegroundColor Yellow
kubectl apply -f k8s/base/configmap.yaml
kubectl apply -f k8s/base/secret.yaml
Write-Host "✅ Konfigürasyon güncellendi" -ForegroundColor Green

# 3. Host SQL Server'da database oluştur
Write-Host "`n[3/6] Host SQL Server'da database kontrol ediliyor..." -ForegroundColor Yellow
Write-Host "   SQL Server Management Studio veya sqlcmd ile ProductManagementDB" -ForegroundColor Gray
Write-Host "   database'ini oluşturmanız gerekiyor." -ForegroundColor Gray
Write-Host ""
Write-Host "   SQL Komutu:" -ForegroundColor Cyan
Write-Host @"
   IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'ProductManagementDB')
   BEGIN
       CREATE DATABASE ProductManagementDB;
   END
"@ -ForegroundColor Gray
Write-Host ""

$createDb = Read-Host "Database'i oluşturmak ister misiniz? (E/H)"
if ($createDb -eq "E" -or $createDb -eq "e") {
    Write-Host "   sqlcmd kullanılıyor..." -ForegroundColor Yellow
    $sql = "IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'ProductManagementDB') BEGIN CREATE DATABASE ProductManagementDB; PRINT 'Database created'; END ELSE BEGIN PRINT 'Database already exists'; END"
    
    try {
        sqlcmd -S localhost,1433 -U sa -P "Az.123456+" -Q $sql -C
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Database hazır" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Database oluşturulamadı. Manuel oluşturun." -ForegroundColor Yellow
        }
    } catch {
        Write-Host "⚠️  sqlcmd bulunamadı. SQL Server Management Studio ile oluşturun." -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️  Manuel database oluşturmanız gerekiyor!" -ForegroundColor Yellow
}

# 4. Application deployment'ını restart et
Write-Host "`n[4/6] Application deployment restart ediliyor..." -ForegroundColor Yellow
kubectl rollout restart deployment/product-service
Write-Host "✅ Deployment restart edildi" -ForegroundColor Green

# 5. Deployment'ın hazır olmasını bekle
Write-Host "`n[5/6] Deployment hazır olması bekleniyor..." -ForegroundColor Yellow
kubectl rollout status deployment/product-service --timeout=120s

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Deployment hazır" -ForegroundColor Green
} else {
    Write-Host "⚠️  Deployment timeout, logları kontrol edin" -ForegroundColor Yellow
}

# 6. Alembic migrations çalıştır
Write-Host "`n[6/6] Alembic migrations çalıştırılıyor..." -ForegroundColor Yellow
Start-Sleep -Seconds 5
$podName = kubectl get pods -l app=product-service -o jsonpath='{.items[0].metadata.name}' 2>$null

if (-not [string]::IsNullOrEmpty($podName)) {
    kubectl exec $podName -- alembic upgrade head
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Migrations başarılı" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Migration hatası, logları kontrol edin" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️  Pod bulunamadı, migrations manuel çalıştırın" -ForegroundColor Yellow
}

Write-Host "`n════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  ✅ Host SQL Server Bağlantısı Kuruldu!  " -ForegroundColor Green
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Pod durumu
Write-Host "📦 Pod Durumu:" -ForegroundColor Cyan
kubectl get pods

Write-Host "`n📋 Son loglar:" -ForegroundColor Cyan
kubectl logs -l app=product-service --tail=15

Write-Host "`n🌐 Port Forward:" -ForegroundColor Cyan
Write-Host "   .\port-forward.ps1" -ForegroundColor Yellow
Write-Host "   http://localhost:8080/api/v1/docs" -ForegroundColor Green
Write-Host ""

Write-Host "💡 SQL Server Kontrol:" -ForegroundColor Cyan
Write-Host "   sqlcmd -S localhost,1433 -U sa -P 'Az.123456+' -Q 'SELECT name FROM sys.databases;'" -ForegroundColor Gray
Write-Host ""
