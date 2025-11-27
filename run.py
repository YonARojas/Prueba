import os
import sys
import oracledb
from app import create_app

# ===========================================================
# 🚀 1. CONFIGURACIÓN DE ORACLE CLIENT + WALLET (THICK MODE)
# ===========================================================

WALLET_DIR = os.path.join(os.getcwd(), "Wallet")
os.environ["TNS_ADMIN"] = WALLET_DIR  # Necesario para SQLAlchemy + cx_Oracle

def init_oracle():
    """Inicializa el Oracle Client en modo Thick y valida el Wallet."""
    print("🔧 Inicializando Oracle Client...")

    if not os.path.isdir(WALLET_DIR):
        print(f"❌ ERROR: No existe el directorio Wallet: {WALLET_DIR}")
        sys.exit(1)

    required_files = ["cwallet.sso", "ewallet.p12", "tnsnames.ora"]
    missing = [f for f in required_files if not os.path.isfile(os.path.join(WALLET_DIR, f))]

    if missing:
        print(f"❌ ERROR: Faltan archivos en el Wallet: {missing}")
        sys.exit(1)

    try:
        oracledb.init_oracle_client(lib_dir=None)  # Render usa lib propia
        print("✅ Oracle Client iniciado correctamente (Thick Mode).")
    except Exception as e:
        print(f"❌ ERROR iniciando Oracle Client: {e}")
        sys.exit(1)


# Inicializar Oracle Client al arrancar
init_oracle()


# ===========================================================
# 🚀 2. INICIAR FLASK APP
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
