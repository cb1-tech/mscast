# Brings the MSCAST demo fully online and keeps it there.
#   powershell -ExecutionPolicy Bypass -File D:\MSCAST\erpnext-poc\scripts\demo-up.ps1
#
# Why this exists: WSL 2.7.3 shuts its VM down whenever no session is attached, regardless of
# vmIdleTimeout. When the VM goes, the containers go with it and the public URL returns 502.
# A pinned session keeps the VM up; the tunnel config is rewritten because the WSL IP can change.

$ErrorActionPreference = "Continue"
$cf  = "C:\Program Files (x86)\cloudflared\cloudflared.exe"
$id  = "0e690596-81d9-4e00-9e00-7e87bd3d7477"
$dir = "$env:USERPROFILE\.cloudflared"

Write-Host "1/4 starting the POC stack..."
wsl -d Ubuntu -e bash /mnt/d/MSCAST/erpnext-poc/scripts/start-poc.sh | Select-Object -Last 2

Write-Host "2/4 pinning the WSL VM up..."
$alive = Get-CimInstance Win32_Process -Filter "Name='wsl.exe'" |
         Where-Object { $_.CommandLine -like "*sleep infinity*" }
if (-not $alive) {
    Start-Process -FilePath "wsl.exe" -ArgumentList '-d','Ubuntu','-e','sleep','infinity' -WindowStyle Hidden
    Write-Host "    keep-alive started"
} else {
    Write-Host "    keep-alive already running"
}

Write-Host "3/4 pointing the tunnel at the current WSL address..."
$ip = (wsl -d Ubuntu -e bash -c "hostname -I | awk '{print `$1}'").Trim()
Write-Host "    WSL IP: $ip"
@"
tunnel: $id
credentials-file: $dir\$id.json
originRequest:
  connectTimeout: 30s
ingress:
  - hostname: mscast.carobar.net
    service: http://${ip}:8080
  - service: http_status:404
"@ | Set-Content "$dir\config.yml" -Encoding ASCII

Get-Process cloudflared -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2
Start-Process -FilePath $cf -ArgumentList 'tunnel','run','mscast-demo' -WindowStyle Hidden

Write-Host "4/4 verifying..."
Start-Sleep -Seconds 20
try {
    $r = Invoke-WebRequest "https://mscast.carobar.net/login" -UseBasicParsing -TimeoutSec 45
    Write-Host "    https://mscast.carobar.net -> $($r.StatusCode)  DEMO IS LIVE"
} catch {
    Write-Host "    still not answering: $($_.Exception.Message)"
    Write-Host "    check: wsl -d Ubuntu -e bash -c 'docker ps'"
}
