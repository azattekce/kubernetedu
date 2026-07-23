# Reset MSSQL Completely - MSSQL'i PVC dahil tamamen sıfırla
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  🔄 MSSQL Tamamen Sıfırlama (PVC Dahil)  " -ForegroundColor Green
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠️  UYARI: Bu işlem TÜM MSSQL verilerini silecek!" -ForegroundColor Yellow
Write-Host ""

$confirm = Read-Host "Devam etmek istiyor musunuz? (E/H)"
if ($confirm -ne "E" -and $confirm -ne "e") {
    Write-Host "İşlem iptal edildi." -ForegroundColor Yellow
    exit 0
}

# 1. MSSQL deployment'ını sil
Write-Host "`n[1/6] MSSQL deployment siliniyor..." -ForegroundColor Yellow
kubectl delete deployment mssql-deployment --ignore-not-found=true
Write-Host "✅ Deployment silindi" -ForegroundColor Green

# 2. MSSQL PVC'yi sil (eski data)
Write-Host "`n[2/6] MSSQL PVC siliniyor (eski data)..." -ForegroundColor Yellow
kubectl delete pvc mssql-pvc --ignore-not-found=true
Write-Host "✅ PVC silindi" -ForegroundColor Green

# 3. Biraz bekle
Write-Host "`n[3/6] Temizlik için bekleniyor..." -ForegroundColor Yellow
Start-Sleep -Seconds 10
Write-Host "✅ Temizlik tamamlandı" -ForegroundColor Green

# 4. MSSQL'i yeniden oluştur
Write-Host "`n[4/6] MSSQL yeniden oluşturuluyor (yeni password ile)..." -ForegroundColor Yellow
kubectl apply -f k8s/dependencies/mssql-deployment.yaml
Write-Host "✅ MSSQL oluşturuldu" -ForegroundColor Green

# 5. Pod'un hazır olmasını bekle
Write-Host "`n[5/6] MSSQL pod hazır olması bekleniyor..." -ForegroundColor Yellow
Write-Host "   Bu 1-2 dakika sürebilir..." -ForegroundColor Gray

$waited = 0
$maxWait = 180

while ($waited -lt $maxWait) {
    $podStatus = kubectl get pods -l app=mssql -o jsonpath='{.items[0].status.phase}' 2>$null
    
    if ($podStatus -eq "Running") {
        Write-Host "`n   Pod Running, SQL hazır olması bekleniyor..." -ForegroundColor Gray
        
        # SQL bağlantısını test et
        $mssqlPod = kubectl get pods -l app=mssql -o jsonpath='{.items[0].metadata.name}' 2>$null
        $testSql = "SELECT @@VERSION;"
        $result = $testSql | kubectl exec -i $mssqlPod -- /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P 'Az.123456+' -C -h -1 2>$null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ MSSQL hazır!" -ForegroundColor Green
            break
        }
    }
    
    Write-Host "   Pod status: $podStatus - Bekleniyor... ($waited/$maxWait saniye)" -ForegroundColor Gray
    Start-Sleep -Seconds 10
    $waited += 10
}

if ($waited -ge $maxWait) {
    Write-Host "❌ Timeout! MSSQL başlatılamadı." -ForegroundColor Red
    Write-Host "`n📋 MSSQL Logları:" -ForegroundColor Yellow
    kubectl logs -l app=mssql --tail=30
    exit 1
}

# 6. Database oluştur
Write-Host "`n[6/6] ProductManagementDB database oluşturuluyor..." -ForegroundColor Yellow
$mssqlPod = kubectl get pods -l app=mssql -o jsonpath='{.items[0].metadata.name}'

$createDbSql = @"
CREATE DATABASE ProductManagementDB;
GO
"@

$createDbSql | kubectl exec -i $mssqlPod -- /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P 'Az.123456+' -C

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Database oluşturuldu: ProductManagementDB" -ForegroundColor Green
} else {
    Write-Host "⚠️  Database oluşturma hatası" -ForegroundColor Yellow
}

Write-Host "`n════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  ✅ MSSQL Sıfırlama Tamamlandı!  " -ForegroundColor Green
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

Write-Host "🗄️  Yeni MSSQL Bilgileri:" -ForegroundColor Cyan
Write-Host "   Host: mssql-service.default.svc.cluster.local" -ForegroundColor Gray
Write-Host "   Port: 1433" -ForegroundColor Gray
Write-Host "   Database: ProductManagementDB" -ForegroundColor Gray
Write-Host "   Username: sa" -ForegroundColor Gray
Write-Host "   Password: Az.123456+" -ForegroundColor Gray

Write-Host "`n💡 Sonraki Adımlar:" -ForegroundColor Cyan
Write-Host "   1. Application restart: kubectl rollout restart deployment/product-service" -ForegroundColor Yellow
Write-Host "   2. Migrations çalıştır: .\run-migrations.ps1" -ForegroundColor Yellow
Write-Host "   3. Port forward: .\port-forward.ps1" -ForegroundColor Yellow
Write-Host ""

# Application restart sorusu
$restartApp = Read-Host "Application pod'larını şimdi restart etmek ister misiniz? (E/H)"
if ($restartApp -eq "E" -or $restartApp -eq "e") {
    Write-Host "`nApplication pod'ları restart ediliyor..." -ForegroundColor Yellow
    kubectl rollout restart deployment/product-service
    Write-Host "✅ Restart komutu gönderildi" -ForegroundColor Green
    Write-Host "`n⏳ 30 saniye bekleniyor..." -ForegroundColor Yellow
    Start-Sleep -Seconds 30
    
    Write-Host "`n📦 Pod Durumu:" -ForegroundColor Cyan
    kubectl get pods
}

Write-Host ""
