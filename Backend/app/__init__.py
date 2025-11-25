from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from app.settings import Config
import os

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)

    # Configuración base
    app.config.from_object(Config)
    app.config['JSON_AS_ASCII'] = False
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

    # CORS para localhost + frontend Render
    CORS(app,
         origins=[
             "http://localhost:3000", "http://localhost:5173",
             "http://localhost:5174", "http://localhost:5175",
             "http://127.0.0.1:3000", "http://127.0.0.1:5173",
             "http://127.0.0.1:5174", "http://127.0.0.1:5175",
             "https://as241s4-pii-t19-fe.onrender.com"  # tu frontend
         ],
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])

    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)

    # Registrar Blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.student_routes import student_bp
    from app.routes.student_dashboard_routes import student_dashboard_bp
    from app.routes.justification_routes import justification_bp
    from app.routes.justification_student_routes import justification_student_bp
    from app.routes.justification_professor_routes import justification_professor_bp
    from app.routes.dashboard_routes import dashboard_bp
    from app.routes.professor_routes import professor_bp
    from app.routes.attendance_routes import attendance_bp
    from app.routes.audit_routes import audit_bp
    from app.routes.professor_dashboard_routes import professor_dashboard_bp
    from app.routes.report_routes import report_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(student_bp, url_prefix="/api/students")
    app.register_blueprint(student_dashboard_bp, url_prefix="/api/students")
    app.register_blueprint(justification_bp, url_prefix="/api/justifications")
    app.register_blueprint(justification_student_bp, url_prefix="/api/justifications")
    app.register_blueprint(justification_professor_bp, url_prefix="/api/justifications")
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")
    app.register_blueprint(professor_bp, url_prefix="/api/professors")
    app.register_blueprint(attendance_bp, url_prefix="/api/attendance")
    app.register_blueprint(audit_bp, url_prefix="/api/audit")
    app.register_blueprint(professor_dashboard_bp, url_prefix="/api/professor/dashboard")
    app.register_blueprint(report_bp, url_prefix="/api/reports")

    # Carpeta de uploads compatible con Render
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

    @app.route('/uploads/<path:filename>')
    def serve_upload(filename):
        return send_from_directory(UPLOAD_FOLDER, filename)

    return app
