#!/bin/bash
# İllüstratörler — derle, dağıt, sabit adresi doğrula.
# Kullanım:  bash yayinla.sh
set -euo pipefail
export PATH="$PATH:/usr/local/bin:/opt/homebrew/bin"
cd "$(dirname "$0")"

SABIT="illustratorler.vercel.app"
TOKEN="${VERCEL_TOKEN:-}"
[ -z "$TOKEN" ] && [ -f .vercel-token ] && TOKEN=$(cat .vercel-token)
[ -z "$TOKEN" ] && [ -f "$HOME/Documents/JobsForZeyn/.vercel-token" ] && TOKEN=$(cat "$HOME/Documents/JobsForZeyn/.vercel-token")
YETKI=(); [ -n "$TOKEN" ] && YETKI=(--token "$TOKEN")

echo "→ katalog derleniyor..."
/usr/bin/python3 scripts/derle.py

echo "→ dağıtılıyor (production)..."
YENI=$(vercel deploy --prod --yes "${YETKI[@]}" 2>/dev/null | grep -Eo 'https://[a-z0-9.-]+\.vercel\.app' | tail -1)
[ -n "$YENI" ] || { echo "HATA: dağıtım adresi alınamadı"; exit 1; }

vercel alias set "${YENI#https://}" "$SABIT" "${YETKI[@]}" >/dev/null 2>&1 || true

KOD=$(curl -s -o /dev/null -w '%{http_code}' "https://$SABIT/")
VERI=$(curl -s -o /dev/null -w '%{http_code}' "https://$SABIT/data/katalog.json")
echo
echo "Site  : https://$SABIT   (HTTP $KOD, veri $VERI — ikisi de 200 beklenir)"
echo "Kaynak: $YENI"
