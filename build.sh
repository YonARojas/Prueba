#!/usr/bin/env bash
set -e

echo "🔎 Verificando variable WALLET_B64..."

# ================================================
# 1) Verificar si WALLET_B64 existe
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
# 3) Decodificar Base64 → Wallet/wallet.zip
# ================================================
# '|| true' evita fallos por saltos de línea
echo "$WALLET_B64" | base64 -d > Wallet/wallet.zip || true

# Validar creación del zip
if [ ! -s "Wallet/wallet.zip" ]; then
  echo "❌ ERROR: No se generó Wallet/wallet.zip"
  exit 1
fi

# ================================================
# 4) Extraer contenido del wallet
# ================================================
unzip -o Wallet/wallet.zip -d Wallet >/dev/null 2>&1

# Validación extra: verificar archivos esenciales
if [ ! -f "Wallet/tnsnames.ora" ] || [ ! -f "Wallet/sqlnet.ora" ]; then
  echo "❌ ERROR: Wallet incompleto. Faltan archivos necesarios."
  exit 1
fi

echo "✅ Wallet Oracle reconstruido correctamente."
