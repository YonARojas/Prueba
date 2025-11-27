import os
import oracledb
from app import create_app

# ============================================
# 🚀 1. ACTIVAR MODO THICK (OBLIGATORIO PARA WALLET)
# ============================================

WALLET_DIR = os.path.join(os.getcwd(), "Wallet")
TNS_ADMIN = WALLET_DIR

# Render reconstruye Wallet/ en build.sh
# Aquí activamos Thick Mode para permitir wallet con passphrase
oracledb.init_oracle_client()

# Asegurar que Flask/SQLAlchemy use el wallet
os.environ["TNS_ADMIN"] = TNS_ADMIN


# ============================================
# 🚀 2. INICIAR APP
# ============================================

app = create_app()

if __name__ == "__main__":
    # En local sí usa debug
    app.run(host="0.0.0.0", port=5000, debug=True)
