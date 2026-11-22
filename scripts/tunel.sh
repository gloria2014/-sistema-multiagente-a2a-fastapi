#!/usr/bin/env bash
# Levanta un túnel de Cloudflare para un puerto local.
# Uso: ./scripts/tunel.sh [puerto]   (por defecto 8000)

PUERTO="${1:-8000}"

if ! command -v cloudflared >/dev/null 2>&1; then
  echo "cloudflared no está instalado."
  echo "Instálalo con: brew install cloudflared"
  exit 1
fi

echo "============================================================"
echo " Levantando túnel para http://127.0.0.1:${PUERTO}"
echo "============================================================"
echo "Cuando aparezca la dirección https://...trycloudflare.com:"
echo "  1) pégala en URL_PUBLICA de tu .env y reinicia tu agente"
echo "  2) pásasela a tu compañero para que la ponga en su URLS_AGENTES"
echo "============================================================"

cloudflared tunnel --url "http://127.0.0.1:${PUERTO}"
