from flask import Blueprint, request, jsonify
from app import db
from app.models.audit_log import AuditLog
from datetime import datetime, timedelta

audit_bp = Blueprint('audit', __name__)

@audit_bp.route('/', methods=['GET'])
def get_audit_logs():
    """Obtener registros de auditoría con filtros"""
    try:
        # Parámetros de filtro
        user_email = request.args.get('user_email')
        user_type = request.args.get('user_type')
        action_type = request.args.get('action_type')
        table_name = request.args.get('table_name')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        
        # Construir query
        query = db.session.query(AuditLog)
        
        if user_email:
            query = query.filter(AuditLog.user_email.ilike(f'%{user_email}%'))
        
        if user_type:
            query = query.filter(AuditLog.user_type == user_type)
        
        if action_type:
            query = query.filter(AuditLog.action_type == action_type)
        
        if table_name:
            query = query.filter(AuditLog.table_name == table_name)
        
        if date_from:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(AuditLog.action_date >= date_from_obj)
        
        if date_to:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(AuditLog.action_date < date_to_obj)
        
        # Ordenar por fecha descendente
        query = query.order_by(AuditLog.action_date.desc())
        
        # Paginar
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'success': True,
            'data': {
                'logs': [log.to_dict() for log in pagination.items],
                'pagination': {
                    'page': pagination.page,
                    'pages': pagination.pages,
                    'per_page': pagination.per_page,
                    'total': pagination.total,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@audit_bp.route('/stats', methods=['GET'])
def get_audit_stats():
    """Obtener estadísticas de auditoría"""
    try:
        # Total de registros
        total_logs = db.session.query(AuditLog).count()
        
        # Logins exitosos vs fallidos
        login_success = db.session.query(AuditLog).filter(
            AuditLog.action_type == 'LOGIN_SUCCESS'
        ).count()
        
        login_failed = db.session.query(AuditLog).filter(
            AuditLog.action_type == 'LOGIN_FAILED'
        ).count()
        
        # Justificaciones aprobadas vs rechazadas
        justifications_approved = db.session.query(AuditLog).filter(
            AuditLog.action_type == 'APPROVE_JUSTIFICATION'
        ).count()
        
        justifications_rejected = db.session.query(AuditLog).filter(
            AuditLog.action_type == 'REJECT_JUSTIFICATION'
        ).count()
        
        # Registros de asistencia
        attendance_records = db.session.query(AuditLog).filter(
            AuditLog.action_type == 'RECORD_ATTENDANCE'
        ).count()
        
        # Actividad por tipo de usuario
        student_actions = db.session.query(AuditLog).filter(
            AuditLog.user_type == 'student'
        ).count()
        
        professor_actions = db.session.query(AuditLog).filter(
            AuditLog.user_type == 'professor'
        ).count()
        
        # Actividad de hoy
        today = datetime.now().date()
        today_actions = db.session.query(AuditLog).filter(
            db.func.date(AuditLog.action_date) == today
        ).count()
        
        return jsonify({
            'success': True,
            'data': {
                'total_logs': total_logs,
                'login_success': login_success,
                'login_failed': login_failed,
                'justifications_approved': justifications_approved,
                'justifications_rejected': justifications_rejected,
                'attendance_records': attendance_records,
                'student_actions': student_actions,
                'professor_actions': professor_actions,
                'today_actions': today_actions
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@audit_bp.route('/recent', methods=['GET'])
def get_recent_logs():
    """Obtener los últimos registros de auditoría"""
    try:
        limit = int(request.args.get('limit', 20))
        
        logs = db.session.query(AuditLog).order_by(
            AuditLog.action_date.desc()
        ).limit(limit).all()
        
        return jsonify({
            'success': True,
            'data': [log.to_dict() for log in logs]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@audit_bp.route('/user/<string:email>', methods=['GET'])
def get_user_logs(email):
    """Obtener registros de auditoría de un usuario específico"""
    try:
        limit = int(request.args.get('limit', 50))
        
        logs = db.session.query(AuditLog).filter(
            AuditLog.user_email == email
        ).order_by(
            AuditLog.action_date.desc()
        ).limit(limit).all()
        
        return jsonify({
            'success': True,
            'data': [log.to_dict() for log in logs]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500
