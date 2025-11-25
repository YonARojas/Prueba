from flask import Blueprint, request, jsonify
from app import db
from app.models.student import Student
from app.models.professor import Professor
from app.models.audit_log import AuditLog
from werkzeug.security import check_password_hash
import jwt
import datetime
from functools import wraps

auth_bp = Blueprint('auth', __name__)

# Clave secreta para JWT (debería estar en .env)
SECRET_KEY = 'dev-secret-key-change-in-production'

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'success': False, 'message': 'Token no proporcionado'}), 401
        
        try:
            token = token.split(' ')[1]  # Bearer <token>
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            current_user = data
        except:
            return jsonify({'success': False, 'message': 'Token inválido'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login para estudiantes y profesores - SOLO usuarios registrados en Oracle"""
    try:
        data = request.get_json()
        email_raw = data.get('email', '').strip()
        password = data.get('password', '')
        user_type = data.get('user_type', 'student')  # 'student' o 'professor'
        
        # Normalizar email: decodificar punycode si existe
        email = email_raw.lower()
        if '@' in email and 'xn--' in email:
            # Decodificar punycode manualmente
            try:
                local, domain = email.rsplit('@', 1)
                domain = domain.encode('ascii').decode('idna')
                email = f"{local}@{domain}"
            except:
                pass
        
        print(f"🔐 Intento de login: email_raw={email_raw}, email_normalizado={email}, tipo={user_type}")
        
        # Validar que se proporcionen credenciales
        if not email or not password:
            print("❌ Email o contraseña vacíos")
            return jsonify({
                'success': False,
                'message': 'Email y contraseña son requeridos'
            }), 400
        
        user = None
        role = None
        
        # Buscar usuario en Oracle según el tipo
        if user_type == 'professor':
            print(f"🔍 Buscando profesor en Oracle: {email}")
            user = db.session.query(Professor).filter(
                db.func.lower(Professor.email) == email
            ).first()
            role = 'professor'
        else:
            print(f"🔍 Buscando estudiante en Oracle: {email}")
            user = db.session.query(Student).filter(
                db.func.lower(Student.email) == email
            ).first()
            role = 'student'
        
        # Usuario no existe en Oracle
        if not user:
            print(f"❌ Usuario no encontrado en Oracle: {email}")
            # Registrar intento fallido en audit_logs
            try:
                AuditLog.log_action(
                    user_id=None,
                    user_type=user_type.upper(),
                    action='LOGIN_FAILED',
                    table_name='users',
                    new_values=f'Intento de login fallido - usuario no existe: {email}',
                    ip_address=request.remote_addr
                )
                db.session.commit()
            except:
                db.session.rollback()
            return jsonify({
                'success': False,
                'message': 'Usuario no registrado en el sistema. Contacte al administrador.'
            }), 401

        # Verificar contraseña (comparación directa con la BD de Oracle)
        if user.password != password:
            print(f"❌ Contraseña incorrecta para: {email}")
            # Registrar intento fallido en audit_logs
            try:
                AuditLog.log_action(
                    user_id=user.id,
                    user_type=role.upper(),
                    action='LOGIN_FAILED',
                    table_name=role + 's',
                    record_id=user.id,
                    new_values=f'Intento de login fallido - contraseña incorrecta',
                    ip_address=request.remote_addr
                )
                db.session.commit()
            except:
                pass
            return jsonify({
                'success': False,
                'message': 'Contraseña incorrecta'
            }), 401
        
        # Verificar que el usuario esté activo en Oracle
        if user.status != 'A':
            print(f"❌ Usuario inactivo: {email}")
            return jsonify({
                'success': False,
                'message': 'Su cuenta está inactiva. Contacte al administrador.'
            }), 401
        
        print(f"✅ Login exitoso: {email} como {role}")
        
        # Registrar login exitoso en audit_logs (opcional - no bloquea el login)
        try:
            AuditLog.log_action(
                user_id=user.id,
                user_type=role.upper(),
                action='LOGIN_SUCCESS',
                table_name=role + 's',
                record_id=user.id,
                new_values=f'Login exitoso como {role}',
                ip_address=request.remote_addr
            )
            db.session.commit()
        except Exception as audit_error:
            print(f"⚠️ Error al registrar audit log: {audit_error}")
            # Hacer rollback para limpiar la sesión y continuar con el login
            db.session.rollback()
        
        # Generar token JWT
        token = jwt.encode({
            'user_id': user.id,
            'email': user.email,
            'role': role,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, SECRET_KEY, algorithm='HS256')
        
        return jsonify({
            'success': True,
            'message': 'Login exitoso',
            'data': {
                'token': token,
                'user': user.to_dict(),
                'role': role
            }
        })
        
    except Exception as e:
        print(f"❌ Error en login: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': 'Error en el servidor. Intente nuevamente.'
        }), 500

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    """Obtener información del usuario actual"""
    try:
        role = current_user.get('role')
        user_id = current_user.get('user_id')
        
        if role == 'professor':
            user = db.session.query(Professor).get(user_id)
        else:
            user = db.session.query(Student).get(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'Usuario no encontrado'
            }), 404
        
        return jsonify({
            'success': True,
            'data': {
                'user': user.to_dict(),
                'role': role
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    """Logout (en el cliente se elimina el token)"""
    return jsonify({
        'success': True,
        'message': 'Logout exitoso'
    })

@auth_bp.route('/change-password', methods=['POST'])
@token_required
def change_password(current_user):
    """Cambiar contraseña del usuario (estudiante o profesor)"""
    try:
        data = request.get_json()
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        
        # Validaciones
        if not current_password or not new_password:
            return jsonify({
                'success': False,
                'message': 'Contraseña actual y nueva son requeridas'
            }), 400
        
        if len(new_password) < 6:
            return jsonify({
                'success': False,
                'message': 'La nueva contraseña debe tener al menos 6 caracteres'
            }), 400
        
        if current_password == new_password:
            return jsonify({
                'success': False,
                'message': 'La nueva contraseña debe ser diferente a la actual'
            }), 400
        
        # Obtener usuario
        role = current_user.get('role')
        user_id = current_user.get('user_id')
        
        if role == 'professor':
            user = db.session.query(Professor).get(user_id)
        else:
            user = db.session.query(Student).get(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'Usuario no encontrado'
            }), 404
        
        # Verificar contraseña actual
        if user.password != current_password:
            return jsonify({
                'success': False,
                'message': 'La contraseña actual es incorrecta'
            }), 401
        
        # Actualizar contraseña en Oracle
        user.password = new_password
        db.session.commit()
        
        # Registrar en audit log
        try:
            AuditLog.log_action(
                user_id=user.id,
                user_type=role.upper(),
                action='PASSWORD_CHANGED',
                table_name=role + 's',
                record_id=user.id,
                new_values='Contraseña actualizada exitosamente',
                ip_address=request.remote_addr
            )
            db.session.commit()
        except:
            db.session.rollback()
        
        print(f"✅ Contraseña cambiada para {user.email}")
        
        return jsonify({
            'success': True,
            'message': 'Contraseña actualizada exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error al cambiar contraseña: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error al cambiar la contraseña'
        }), 500
