import os
from app import create_app

# ===========================================================
# 🚀 1. CONFIGURACIÓN PARA ORACLE EN MODO THIN (Render compatible)
# ===========================================================

# Render descomprime el wallet SIEMPRE en /app/Wallet
WALLET_DIR = "/app/Wallet"
os.environ["TNS_ADMIN"] = WALLET_DIR


def validate_wallet():
    """Verifica que los archivos del Wallet existen, pero NO inicia modo thick."""
    print("🔧 Verificando Wallet...")

    if not os.path.isdir(WALLET_DIR):
        print(f"❌ ERROR: No existe el directorio Wallet: {WALLET_DIR}")
        return False

    required_files = ["cwallet.sso", "ewallet.p12", "tnsnames.ora"]
    missing = [f for f in required_files if not os.path.isfile(os.path.join(WALLET_DIR, f))]

    if missing:
        print(f"❌ ERROR: Faltan archivos en el Wallet: {missing}")
        return False

    print("✅ Wallet verificado correctamente (Modo THIN).")
    return True


# Validar Wallet
validate_wallet()


# ===========================================================
# 🚀 2. INICIAR FLASK APP (sin intentar thick mode)
# ===========================================================

app = create_app()

if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "true").lower() == "true"

    print("🚀 Iniciando servidor Flask...")
    print(f"🔐 TNS_ADMIN = {os.environ.get('TNS_ADMIN')}")
    print(f"🐍 Debug = {debug_mode}")

    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000)),
        debug=debug_mode
    )
