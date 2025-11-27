import os

class Config:

    # ============================================
    # 1) BASE DE DATOS PARA RENDER (ORACLE)
    # ============================================

    # Render usa DATABASE_URL → debes poner esto en Render:
    # oracle+oracledb://usuario:password@alias_tns
    #
    # EJEMPLO:
    # oracle+oracledb://DEVELOPER_01:Developer123@justificacion_medium
    #
    # Sin wallet_password → obligatorio para Autonomous

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")

    # Local fallback
    if not SQLALCHEMY_DATABASE_URI:
        SQLALCHEMY_DATABASE_URI = "sqlite:///local.db"

    # ============================================
    # 2) SECRETS
    # ============================================

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-key")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ============================================
    # 3) OPTIMIZACIÓN ORACLE (CONEXIÓN ESTABLE)
    # ============================================

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 10,
        "max_overflow": 10,
        "pool_timeout": 30,
        "pool_recycle": 1800,
        "pool_pre_ping": True
    }

    # ============================================
    # 4) RUTA DEL WALLET (Render)
    # ============================================

    # Render reconstruye el wallet en /app/Wallet
    TNS_ADMIN = "/app/Wallet"

    # ============================================
    # 5) UPLOADS
    # ============================================

    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
