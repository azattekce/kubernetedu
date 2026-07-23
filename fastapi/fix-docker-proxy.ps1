# Docker Daemon Proxy Configuration for Minikube
# Kurumsal proxy arkasındaysanız bu script'i kullanın

Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  🌐 Minikube Docker Proxy Konfigürasyonu  " -ForegroundColor Green
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$minikubePath = "C:\Program Files\Kubernetes\Minikube\minikube.exe"

# Proxy bilgilerini kullanıcıdan al
Write-Host "Kurumsal proxy bilgilerinizi girin (yoksa boş bırakın):" -ForegroundColor Yellow
Write-Host ""
$httpProxy = Read-Host "HTTP Proxy (örn: http://proxy.sirket.com:8080)"
$httpsProxy = Read-Host "HTTPS Proxy (örn: http://proxy.sirket.com:8080)"
$noProxy = Read-Host "No Proxy (örn: localhost,127.0.0.1,.local)"

if ([string]::IsNullOrWhiteSpace($httpProxy) -and [string]::IsNullOrWhiteSpace($httpsProxy)) {
    Write-Host "`n⚠️  Proxy bilgisi girilmedi. TLS bypass yapılacak..." -ForegroundColor Yellow
    
    # TLS bypass config
    $dockerConfig = @"
{
  "insecure-registries": ["docker.io", "registry-1.docker.io", "mcr.microsoft.com"],
  "registry-mirrors": []
}
"@
} else {
    Write-Host "`n✅ Proxy yapılandırması oluşturuluyor..." -ForegroundColor Green
    
    # Proxy config
    $dockerConfig = @"
{
  "proxies": {
    "http-proxy": "$httpProxy",
    "https-proxy": "$httpsProxy",
    "no-proxy": "$noProxy"
  },
  "insecure-registries": ["docker.io", "registry-1.docker.io"],
  "registry-mirrors": []
}
"@
}

Write-Host "`n[1/3] Docker daemon config oluşturuluyor..." -ForegroundColor Yellow
$dockerConfig | & $minikubePath ssh "sudo tee /etc/docker/daemon.json > /dev/null"
Write-Host "✅ Config oluşturuldu" -ForegroundColor Green

Write-Host "`n[2/3] Docker daemon yeniden başlatılıyor..." -ForegroundColor Yellow
& $minikubePath ssh "sudo systemctl restart docker"
Start-Sleep -Seconds 10
Write-Host "✅ Docker yeniden başlatıldı" -ForegroundColor Green

Write-Host "`n[3/3] Docker durumu kontrol ediliyor..." -ForegroundColor Yellow
& $minikubePath ssh "sudo systemctl status docker --no-pager | head -n 5"

Write-Host "`n════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  ✅ Proxy konfigürasyonu tamamlandı!  " -ForegroundColor Green
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "Test etmek için:" -ForegroundColor Yellow
Write-Host "  & 'C:\Program Files\Kubernetes\Minikube\minikube.exe' docker-env | Invoke-Expression" -ForegroundColor Cyan
Write-Host "  docker pull python:3.12-slim" -ForegroundColor Cyan
Write-Host ""
