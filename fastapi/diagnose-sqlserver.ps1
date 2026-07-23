# SQL Server Diagnostic Script - SQL Server durumunu kontrol et
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  🔍 SQL Server Diagnostic  " -ForegroundColor Green
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# 1. SQL Server servislerini kontrol et
Write-Host "[1/6] SQL Server servisleri kontrol ediliyor..." -ForegroundColor Yellow
Write-Host ""

$sqlServices = Get-Service -Name "*SQL*" -ErrorAction SilentlyContinue | Where-Object { $_.DisplayName -like "*SQL Server*" }

if ($sqlServices) {
    foreach ($service in $sqlServices) {
        $status = $service.Status
        $color = if ($status -eq "Running") { "Green" } else { "Red" }
        Write-Host "   $($service.DisplayName): $status" -ForegroundColor $color
    }
} else {
    Write-Host "   ❌ SQL Server servisi bulunamadı!" -ForegroundColor Red
    Write-Host "   SQL Server yüklü değil veya farklı bir isimle çalışıyor." -ForegroundColor Yellow
}

# 2. Port 1433'ün dinlendiğini kontrol et
Write-Host "`n[2/6] Port 1433 dinleme durumu kontrol ediliyor..." -ForegroundColor Yellow
$port1433 = netstat -ano | Select-String ":1433" | Select-String "LISTENING"

if ($port1433) {
    Write-Host "   ✅ Port 1433 dinleniyor:" -ForegroundColor Green
    Write-Host "   $port1433" -ForegroundColor Gray
} else {
    Write-Host "   ❌ Port 1433 dinlenmiyor!" -ForegroundColor Red
    Write-Host "   SQL Server TCP/IP bağlantıları kabul etmiyor." -ForegroundColor Yellow
}

# 3. Windows Firewall kurallarını kontrol et
Write-Host "`n[3/6] Windows Firewall kuralları kontrol ediliyor..." -ForegroundColor Yellow
$firewallRules = Get-NetFirewallRule -DisplayName "*SQL*" -ErrorAction SilentlyContinue

if ($firewallRules) {
    foreach ($rule in $firewallRules) {
        $enabled = $rule.Enabled
        $color = if ($enabled -eq "True") { "Green" } else { "Yellow" }
        Write-Host "   $($rule.DisplayName): $($rule.Direction) - Enabled: $enabled" -ForegroundColor $color
    }
} else {
    Write-Host "   ⚠️  SQL Server için firewall kuralı bulunamadı" -ForegroundColor Yellow
}

# 4. Localhost bağlantısını test et (ping)
Write-Host "`n[4/6] Localhost bağlantısı test ediliyor..." -ForegroundColor Yellow
$tcpClient = New-Object System.Net.Sockets.TcpClient
try {
    $tcpClient.Connect("localhost", 1433)
    Write-Host "   ✅ Port 1433'e TCP bağlantısı başarılı" -ForegroundColor Green
    $tcpClient.Close()
} catch {
    Write-Host "   ❌ Port 1433'e bağlanılamıyor: $($_.Exception.Message)" -ForegroundColor Red
}

# 5. SQL Server Configuration Manager yolunu göster
Write-Host "`n[5/6] SQL Server Configuration Manager yolu:" -ForegroundColor Yellow
$configMgrPath = "C:\Windows\SysWOW64\SQLServerManager*.msc"
$configFiles = Get-Item $configMgrPath -ErrorAction SilentlyContinue

if ($configFiles) {
    Write-Host "   $($configFiles.FullName)" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  SQL Server Configuration Manager bulunamadı" -ForegroundColor Yellow
}

# 6. Çözüm önerileri
Write-Host "`n[6/6] Durum Özeti ve Çözüm Önerileri:" -ForegroundColor Yellow
Write-Host ""

$hasRunningSQL = $sqlServices | Where-Object { $_.Status -eq "Running" }
$hasPort1433 = $port1433 -ne $null

if (-not $hasRunningSQL) {
    Write-Host "❌ SORUN: SQL Server servisi çalışmıyor" -ForegroundColor Red
    Write-Host ""
    Write-Host "✅ ÇÖZÜM 1: SQL Server servisini başlat" -ForegroundColor Green
    Write-Host "   Start-Service MSSQLSERVER" -ForegroundColor Cyan
    Write-Host "   # veya" -ForegroundColor Gray
    Write-Host "   services.msc açın ve 'SQL Server (MSSQLSERVER)' başlatın" -ForegroundColor Cyan
    Write-Host ""
    
    $startService = Read-Host "SQL Server servisini şimdi başlatmak ister misiniz? (E/H)"
    if ($startService -eq "E" -or $startService -eq "e") {
        try {
            Start-Service MSSQLSERVER -ErrorAction Stop
            Write-Host "   ✅ SQL Server başlatıldı!" -ForegroundColor Green
            Start-Sleep -Seconds 3
        } catch {
            Write-Host "   ❌ Başlatılamadı: $($_.Exception.Message)" -ForegroundColor Red
            Write-Host "   Manuel olarak services.msc'den başlatın" -ForegroundColor Yellow
        }
    }
}

if (-not $hasPort1433) {
    Write-Host "❌ SORUN: TCP/IP protokolü aktif değil veya port 1433 dinlenmiyor" -ForegroundColor Red
    Write-Host ""
    Write-Host "✅ ÇÖZÜM 2: TCP/IP protokolünü aktifleştir" -ForegroundColor Green
    Write-Host "   1. SQL Server Configuration Manager'ı açın:" -ForegroundColor Cyan
    Write-Host "      C:\Windows\SysWOW64\SQLServerManager*.msc" -ForegroundColor Gray
    Write-Host ""
    Write-Host "   2. Sol panelden:" -ForegroundColor Cyan
    Write-Host "      SQL Server Network Configuration > Protocols for MSSQLSERVER" -ForegroundColor Gray
    Write-Host ""
    Write-Host "   3. TCP/IP'ye sağ tıklayın > Enable" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "   4. SQL Server servisini restart edin:" -ForegroundColor Cyan
    Write-Host "      Restart-Service MSSQLSERVER" -ForegroundColor Gray
    Write-Host ""
}

Write-Host "✅ ÇÖZÜM 3: Windows Firewall'da port 1433'ü aç" -ForegroundColor Green
Write-Host "   New-NetFirewallRule -DisplayName 'SQL Server' -Direction Inbound -Protocol TCP -LocalPort 1433 -Action Allow" -ForegroundColor Cyan
Write-Host ""

Write-Host "✅ ÇÖZÜM 4: SQL Server Authentication'ı aktifleştir" -ForegroundColor Green
Write-Host "   1. SSMS'de server'a bağlanın" -ForegroundColor Cyan
Write-Host "   2. Server'a sağ tıklayın > Properties > Security" -ForegroundColor Cyan
Write-Host "   3. 'SQL Server and Windows Authentication mode' seçin" -ForegroundColor Cyan
Write-Host "   4. SQL Server'ı restart edin" -ForegroundColor Cyan
Write-Host ""

Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  💡 Alternatif: Minikube içindeki SQL kullanın  " -ForegroundColor Yellow
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "Eğer host SQL Server'ı yapılandırmak istemiyorsanız," -ForegroundColor Yellow
Write-Host "Minikube içindeki SQL Server'ı kullanabilirsiniz:" -ForegroundColor Yellow
Write-Host ""
Write-Host "   kubectl scale deployment mssql-deployment --replicas=1" -ForegroundColor Cyan
Write-Host "   # ConfigMap'i eski haline çevir (mssql-service.default.svc.cluster.local)" -ForegroundColor Gray
Write-Host ""

Write-Host "🔍 Test komutu:" -ForegroundColor Cyan
Write-Host "   sqlcmd -S localhost,1433 -U sa -P 'Az.123456+' -Q 'SELECT @@VERSION;'" -ForegroundColor Gray
Write-Host ""
