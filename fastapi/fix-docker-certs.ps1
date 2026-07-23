# Minikube Docker TLS Sertifika Düzeltme Script'i
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  🔒 Minikube Docker TLS Sertifika Düzeltmesi  " -ForegroundColor Green
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$minikubePath = "C:\Program Files\Kubernetes\Minikube\minikube.exe"

# 1. Windows sertifikalarını export et
Write-Host "[1/4] Windows kurumsal sertifikaları export ediliyor..." -ForegroundColor Yellow
$certPath = "$env:TEMP\corporate-certs.crt"
$certs = Get-ChildItem -Path Cert:\LocalMachine\Root | Where-Object { $_.Subject -like "*" }

$pemContent = ""
foreach ($cert in $certs) {
    $pemContent += "-----BEGIN CERTIFICATE-----`n"
    $pemContent += [System.Convert]::ToBase64String($cert.RawData, [System.Base64FormattingOptions]::InsertLineBreaks)
    $pemContent += "`n-----END CERTIFICATE-----`n"
}

$pemContent | Out-File -FilePath $certPath -Encoding ASCII
Write-Host "✅ Sertifikalar export edildi: $certPath" -ForegroundColor Green

# 2. Minikube içine sertifikaları kopyala
Write-Host "`n[2/4] Sertifikalar Minikube içine kopyalanıyor..." -ForegroundColor Yellow
& $minikubePath ssh "sudo mkdir -p /etc/docker/certs.d/docker.io"
& $minikubePath ssh "sudo mkdir -p /etc/docker/certs.d/registry-1.docker.io"
& $minikubePath ssh "sudo mkdir -p /usr/local/share/ca-certificates"

# Sertifikaları Minikube'a gönder
Get-Content $certPath | & $minikubePath ssh "sudo tee /usr/local/share/ca-certificates/corporate-certs.crt > /dev/null"
Get-Content $certPath | & $minikubePath ssh "sudo tee /etc/docker/certs.d/docker.io/ca.crt > /dev/null"
Get-Content $certPath | & $minikubePath ssh "sudo tee /etc/docker/certs.d/registry-1.docker.io/ca.crt > /dev/null"

Write-Host "✅ Sertifikalar kopyalandı" -ForegroundColor Green

# 3. Sertifikaları güncelle
Write-Host "`n[3/4] Sistem sertifikaları güncelleniyor..." -ForegroundColor Yellow
& $minikubePath ssh "sudo update-ca-certificates"
Write-Host "✅ Sertifikalar güncellendi" -ForegroundColor Green

# 4. Docker daemon'ı yeniden başlat
Write-Host "`n[4/4] Docker daemon yeniden başlatılıyor..." -ForegroundColor Yellow
& $minikubePath ssh "sudo systemctl restart docker"
Start-Sleep -Seconds 10
Write-Host "✅ Docker daemon yeniden başlatıldı" -ForegroundColor Green

Write-Host "`n════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  ✅ Sertifika düzeltmesi tamamlandı!  " -ForegroundColor Green
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "Şimdi deploy script'ini tekrar çalıştırabilirsiniz:" -ForegroundColor Yellow
Write-Host ".\deploy-to-minikube.ps1" -ForegroundColor Cyan
Write-Host ""

# Temizlik
Remove-Item $certPath -ErrorAction SilentlyContinue
