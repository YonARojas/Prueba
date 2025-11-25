import os

class Config:

    # ============================================
    # 🔹 1. BASE DE DATOS (Render + Local)
    # ============================================

    # Render obtiene la conexión desde DATABASE_URL
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")

    # Si estás trabajando local SIN Oracle → usar SQLite
    if not SQLALCHEMY_DATABASE_URI:
        SQLALCHEMY_DATABASE_URI = "sqlite:///local.db"

    # ============================================
    # 🔹 2. CLAVES SEGURAS
    # ============================================

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-key")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ============================================
    # 🔹 3. OPTIMIZACIÓN PARA ORACLE EN RENDER
    # ============================================
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 10,
        "max_overflow": 15,
        "pool_timeout": 30,
        "pool_recycle": 1800,
        "pool_pre_ping": True
    }

    # ============================================
    # 🔹 4. CONFIGURACIÓN DE UPLOADS
    # ============================================

    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

    # Límite de subida: 16 MB
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
