#!/usr/bin/env bash
set -e

pip install -r requirements.txt

echo "🔎 Verificando Wallet Base64..."

if [ -n "$WALLET_B64" ]; then
  echo "🔐 Reconstruyendo Oracle Wallet..."
  mkdir -p Wallet
  echo "$WALLET_B64" | base64 -d > Wallet/wallet.zip
  unzip -o Wallet/wallet.zip -d Wallet
else
  echo "⚠️ WALLET_B64 no fue proporcionado"
fi
