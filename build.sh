#!/usr/bin/env bash
set -e

echo "🔎 Verificando variable WALLET_B64..."

# ================================================
# 1) Verifica si WALLET_B64 existe
# ================================================
if [ -z "$WALLET_B64" ]; then
  echo "⚠️  WALLET_B64 no fue proporcionado. Omitiendo reconstrucción del Wallet."
  exit 0
fi

echo "🔐 Reconstruyendo Oracle Wallet desde Base64..."

# ================================================
# 2) Crear carpeta Wallet
# ================================================
mkdir -p Wallet

# ================================================
# 3) Decodificar Base64 → wallet.zip
# ================================================
# '|| true' evita que falle por saltos de línea
echo "$WALLET_B64" | base64 -d > Wallet/wallet.zip || true

# Comprueba creación
if [ ! -f "Wallet/wallet.zip" ]; then
  echo "❌ ERROR: No se generó Wallet/wallet.zip"
  exit 1
fi

# ================================================
# 4) Descomprimir wallet
# ================================================
unzip -o Wallet/wallet.zip -d Wallet >/dev/null 2>&1

echo "✅ Wallet Oracle reconstruido correctamente."
