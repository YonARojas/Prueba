import os

class Config:

    # ======================================================
    # 1) BASE DE DATOS (ORACLE AUTONOMOUS — MODO THIN)
    # ======================================================
    #
    # Render recibirá algo como:
    # DATABASE_URL = oracle+oracledb://USER:PASSWORD@TNS_ALIAS?wallet_location=/app/Wallet&wallet_password=
    #
    # O simplemente:
    # DATABASE_URL = oracle+oracledb://USER:PASSWORD@TNS_ALIAS
    #
    # (El wallet lo aporta TNS_ADMIN, no es necesario poner parámetros adicionales)

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")

    # Fallback local
    if not SQLALCHEMY_DATABASE_URI:
        SQLALCHEMY_DATABASE_URI = "sqlite:///local.db"

    # ======================================================
    # 2) SECRETS
    # ======================================================

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-key")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ======================================================
    # 3) ORACLE ENGINE (CONEXIONES ESTABLES EN RENDER)
    # ======================================================

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 5,
        "max_overflow": 5,
        "pool_timeout": 30,
        "pool_recycle": 1800,  # evita desconexiones OCI por inactividad
        "pool_pre_ping": True  # evita errores ORA-03135
    }

    # ======================================================
    # 4) RUTA DEL WALLET (RECONSTRUIDO EN BUILD)
    # ======================================================

    # Render descomprime el wallet en /app/Wallet
    TNS_ADMIN = "/app/Wallet"
    os.environ["TNS_ADMIN"] = TNS_ADMIN  # Necesario para SQLAlchemy + oracledb thin

    # ======================================================
    # 5) UPLOADS
    # ======================================================

    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
