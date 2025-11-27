#!/usr/bin/env bash
set -e

echo "🔎 Verificando Wallet Base64..."

# Si la variable existe reconstruye el wallet
if [ -n "$WALLET_B64" ]; then
  echo "🔐 Reconstruyendo Oracle Wallet..."
  
  mkdir -p Wallet

  echo "$WALLET_B64" | base64 -d > Wallet/wallet.zip

  if [ -f "Wallet/wallet.zip" ]; then
    unzip -o Wallet/wallet.zip -d Wallet
    echo "✅ Wallet reconstruido correctamente."
  else
    echo "❌ No se generó wallet.zip"
  fi

else
  echo "⚠️ WALLET_B64 no fue proporcionado"
fi
