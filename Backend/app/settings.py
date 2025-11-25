import os

class Config:
    # Render usa DATABASE_URL (NO el wallet)
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")

    # Claves
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-key")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Pool optimizado para Oracle + Render
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 10,
        "max_overflow": 15,
        "pool_timeout": 30,
        "pool_recycle": 1800,
        "pool_pre_ping": True
    }

    # Uploads
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
