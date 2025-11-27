#!/usr/bin/env bash
set -e

echo "🔎 Verificando variable WALLET_B64..."

# ================================================
# 1) Verificar si WALLET_B64 existe
# ================================================
if [ -z "$WALLET_B64" ]; then
  echo "⚠️ WALLET_B64 no fue proporcionado. Omitiendo reconstrucción del Wallet."
  exit 0
fi

echo "🔐 Reconstruyendo Oracle Wallet desde Base64..."

# ================================================
# 2) Crear carpeta /app/Wallet (Render runtime)
# ================================================
APP_WALLET_DIR="/app/Wallet"
mkdir -p "$APP_WALLET_DIR"

# ================================================
# 3) Decodificar Base64 → /app/Wallet/wallet.zip
# ================================================
echo "$WALLET_B64" | base64 -d > "$APP_WALLET_DIR/wallet.zip" || true

if [ ! -s "$APP_WALLET_DIR/wallet.zip" ]; then
  echo "❌ ERROR: No se generó $APP_WALLET_DIR/wallet.zip"
  exit 1
fi

# ================================================
# 4) Extraer contenido del Wallet
# ================================================
unzip -o "$APP_WALLET_DIR/wallet.zip" -d "$APP_WALLET_DIR" >/dev/null 2>&1

if [ ! -f "$APP_WALLET_DIR/tnsnames.ora" ] || [ ! -f "$APP_WALLET_DIR/sqlnet.ora" ]; then
  echo "❌ ERROR: Wallet incompleto. Faltan archivos necesarios."
  exit 1
fi

echo "📁 Archivos en $APP_WALLET_DIR:"
ls -l "$APP_WALLET_DIR"

echo "🎉 Wallet Oracle instalado correctamente en /app/Wallet"
