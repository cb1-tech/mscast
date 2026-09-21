# Add mscastdev.carobar.net to the existing tunnel WITHOUT dropping mscast.carobar.net.
# Start a second connector with the new two-host config, confirm it serves,
# then stop the old connector. Cloudflare routes to whichever connector is up.
$ErrorActionPreference = "Continue"
$cf  = "C:\Program Files (x86)\cloudflared\cloudflared.exe"
$id  = "0e690596-81d9-4e00-9e00-7e87bd3d7477"
$dir = "$env:USERPROFILE\.cloudflared"

Write-Host "1/4 DNS record for mscastdev.carobar.net"
& $cf tunnel route dns mscast-demo mscastdev.carobar.net 2>&1 | Select-Object -Last 2

Write-Host "2/4 two-host config"
$ip = (wsl -d Ubuntu -e bash -c "hostname -I | awk '{print `$1}'").Trim()
Copy-Item "$dir\config.yml" "$dir\config.yml.bak-onehost" -Force
@"
tunnel: $id
credentials-file: $dir\$id.json
originRequest:
  connectTimeout: 30s
ingress:
  - hostname: mscast.carobar.net
    service: http://${ip}:8080
  - hostname: mscastdev.carobar.net
    service: http://${ip}:8081
  - service: http_status:404
"@ | Set-Content "$dir\config.yml" -Encoding ASCII

Write-Host "3/4 start new connector, keep old one serving"
$old = @(Get-Process cloudflared -ErrorAction SilentlyContinue | ForEach-Object Id)
Start-Process -FilePath $cf -ArgumentList 'tunnel','run','mscast-demo' -WindowStyle Hidden
Start-Sleep -Seconds 25

Write-Host "4/4 stop old connector(s): $old"
foreach ($p in $old) { Stop-Process -Id $p -Force -ErrorAction SilentlyContinue }
Start-Sleep -Seconds 8
foreach ($u in "https://mscast.carobar.net/login","https://mscastdev.carobar.net/login") {
  try { $r = Invoke-WebRequest $u -UseBasicParsing -TimeoutSec 45; Write-Host "    $u -> $($r.StatusCode)" }
  catch { Write-Host "    $u -> FAIL $($_.Exception.Message)" }
}
