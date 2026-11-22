# Levanta un tunel de Cloudflare para un puerto local.
# Uso: .\scripts\tunel.ps1 [-Puerto 8000]

param(
    [int]$Puerto = 8000
)

if (-not (Get-Command cloudflared -ErrorAction SilentlyContinue)) {
    Write-Host "cloudflared no esta instalado."
    Write-Host "Instalalo con: winget install Cloudflare.cloudflared"
    exit 1
}

Write-Host "============================================================"
Write-Host " Levantando tunel para http://127.0.0.1:$Puerto"
Write-Host "============================================================"
Write-Host "Cuando aparezca la direccion https://...trycloudflare.com:"
Write-Host "  1) pegala en URL_PUBLICA de tu .env y reinicia tu agente"
Write-Host "  2) pasasela a tu companero para que la ponga en su URLS_AGENTES"
Write-Host "============================================================"

cloudflared tunnel --url "http://127.0.0.1:$Puerto"
