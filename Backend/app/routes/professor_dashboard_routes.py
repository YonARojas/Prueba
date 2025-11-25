"""
Rutas para el dashboard del profesor
Muestra estadísticas REALES y estudiantes en riesgo
"""
from flask import Blueprint, request, jsonify
from app import db
from app.models.student import Student
from app.models.justification import Justification
from app.services.statistics_service import StatisticsService
from datetime import datetime, timedelta

professor_dashboard_bp = Blueprint('professor_dashboard', __name__)

@professor_dashboard_bp.route('/stats', methods=['GET'])
def get_dashboard_stats():
    """Obtiene estadísticas generales REALES para el dashboard del profesor"""
    try:
        stats = StatisticsService.get_dashboard_stats()
        
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@professor_dashboard_bp.route('/students-at-risk', methods=['GET'])
def get_students_at_risk():
    """Obtiene lista de estudiantes en riesgo (≥25% inasistencias)"""
    try:
        students = StatisticsService.get_students_at_risk()
        
        return jsonify({
            'success': True,
            'data': students,
            'count': len(students)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@professor_dashboard_bp.route('/students-critical', methods=['GET'])
def get_students_critical():
    """Obtiene lista de estudiantes CRÍTICOS (≥30% inasistencias)"""
    try:
        students = StatisticsService.get_critical_students()
        
        return jsonify({
            'success': True,
            'data': students,
            'count': len(students)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@professor_dashboard_bp.route('/recent-justifications', methods=['GET'])
def get_recent_justifications():
    """Obtiene las justificaciones más recientes"""
    try:
        limit = int(request.args.get('limit', 10))
        
        justifications = db.session.query(Justification).order_by(
            Justification.submission_date.desc()
        ).limit(limit).all()
        
        result = []
        for j in justifications:
            student = db.session.query(Student).get(j.student_id)
            from app.models.course import Course
            course = db.session.query(Course).get(j.course_id)
            
            data = j.to_dict()
            data['student_name'] = student.full_name if student else 'Desconocido'
            data['student_code'] = student.student_code if student else 'N/A'
            data['course_name'] = course.course_name if course else 'Desconocido'
            result.append(data)
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@professor_dashboard_bp.route('/pending-justifications', methods=['GET'])
def get_pending_justifications():
    """Obtiene todas las justificaciones pendientes"""
    try:
        justifications = db.session.query(Justification).filter(
            Justification.status == 'PENDIENTE'
        ).order_by(
            Justification.submission_date.desc()
        ).all()
        
        result = []
        for j in justifications:
            student = db.session.query(Student).get(j.student_id)
            from app.models.course import Course
            course = db.session.query(Course).get(j.course_id)
            
            data = j.to_dict()
            data['student_name'] = student.full_name if student else 'Desconocido'
            data['student_code'] = student.student_code if student else 'N/A'
            data['student_email'] = student.email if student else None
            data['course_name'] = course.course_name if course else 'Desconocido'
            result.append(data)
        
        return jsonify({
            'success': True,
            'data': result,
            'count': len(result)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@professor_dashboard_bp.route('/send-alert/<int:student_id>', methods=['POST'])
def send_attendance_alert(student_id):
    """Envía alerta por email a un estudiante con alto porcentaje de inasistencias"""
    try:
        student = db.session.query(Student).get(student_id)
        
        if not student:
            return jsonify({
                'success': False,
                'message': 'Estudiante no encontrado'
            }), 404
        
        # Obtener estadísticas
        stats = StatisticsService.calculate_student_attendance(student_id)
        
        # Enviar email
        from app.services.email_service import EmailService
        email_sent = EmailService.send_attendance_alert(student, stats)
        
        if email_sent:
            return jsonify({
                'success': True,
                'message': f'Alerta enviada a {student.email}'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Error al enviar el email'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@professor_dashboard_bp.route('/send-custom-alert/<int:student_id>', methods=['POST'])
def send_custom_alert(student_id):
    """Envía un mensaje personalizado por email a un estudiante"""
    try:
        data = request.get_json()
        subject = data.get('subject', 'Mensaje del Profesor')
        message = data.get('message', '')
        
        if not message:
            return jsonify({
                'success': False,
                'message': 'El mensaje no puede estar vacío'
            }), 400
        
        student = db.session.query(Student).get(student_id)
        
        if not student:
            return jsonify({
                'success': False,
                'message': 'Estudiante no encontrado'
            }), 404
        
        # Obtener estadísticas para incluir en el email
        stats = StatisticsService.calculate_student_attendance(student_id)
        
        # Enviar email personalizado
        from app.services.email_service import EmailService
        email_sent = EmailService.send_custom_message(student, stats, subject, message)
        
        if email_sent:
            return jsonify({
                'success': True,
                'message': f'Mensaje enviado a {student.email}'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Error al enviar el email'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500
