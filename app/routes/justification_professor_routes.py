from flask import Blueprint, request, jsonify
from app import db
from app.models.justification import Justification
from app.models.student import Student
from app.models.professor import Professor
from app.models.course import Course
from app.models.audit_log import AuditLog
from datetime import datetime

justification_professor_bp = Blueprint('justification_professor', __name__)

@justification_professor_bp.route('/all', methods=['GET'])
def get_all_justifications():
    """Obtener todas las justificaciones con datos del estudiante y curso"""
    try:
        print("🔍 Obteniendo TODAS las justificaciones...")
        # Query con JOIN para obtener datos relacionados
        justifications_data = db.session.query(
            Justification,
            Student.first_name,
            Student.last_name,
            Student.student_code,
            Student.email,
            Student.career,
            Course.course_name,
            Course.course_code
        ).join(
            Student, Justification.student_id == Student.id
        ).join(
            Course, Justification.course_id == Course.id
        ).order_by(
            Justification.submission_date.desc()
        ).all()
        
        print(f"✅ Justificaciones encontradas: {len(justifications_data)}")
        
        # Construir respuesta con datos completos
        result = []
        for justification, student_first, student_last, student_code, student_email, student_career, course_name, course_code in justifications_data:
            justification_dict = justification.to_dict()
            justification_dict['student_name'] = f"{student_first} {student_last}"
            justification_dict['student_code'] = student_code
            justification_dict['student_email'] = student_email
            justification_dict['student_career'] = student_career
            justification_dict['course_name'] = course_name
            justification_dict['course_code'] = course_code
            result.append(justification_dict)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        print(f"❌ Error al obtener justificaciones: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@justification_professor_bp.route('/pending', methods=['GET'])
def get_pending_justifications():
    """Obtener justificaciones pendientes con datos del estudiante y curso"""
    try:
        print("🔍 Obteniendo justificaciones PENDIENTES...")
        # Query con JOIN para obtener datos relacionados
        justifications_data = db.session.query(
            Justification,
            Student.first_name,
            Student.last_name,
            Student.student_code,
            Student.email,
            Student.career,
            Course.course_name,
            Course.course_code
        ).join(
            Student, Justification.student_id == Student.id
        ).join(
            Course, Justification.course_id == Course.id
        ).filter(
            Justification.status == 'PENDIENTE'
        ).order_by(
            Justification.submission_date.desc()
        ).all()
        
        print(f"✅ Justificaciones pendientes encontradas: {len(justifications_data)}")
        
        # Construir respuesta con datos completos
        result = []
        for justification, student_first, student_last, student_code, student_email, student_career, course_name, course_code in justifications_data:
            justification_dict = justification.to_dict()
            justification_dict['student_name'] = f"{student_first} {student_last}"
            justification_dict['student_code'] = student_code
            justification_dict['student_email'] = student_email
            justification_dict['student_career'] = student_career
            justification_dict['course_name'] = course_name
            justification_dict['course_code'] = course_code
            result.append(justification_dict)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        print(f"❌ Error al obtener justificaciones pendientes: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@justification_professor_bp.route('/<int:justification_id>/approve', methods=['POST'])
def approve_justification(justification_id):
    """Aprobar una justificación"""
    try:
        data = request.get_json()
        professor_id = data.get('professor_id')
        admin_response = data.get('admin_response', '')
        
        justification = db.session.query(Justification).get(justification_id)
        
        if not justification:
            return jsonify({
                'success': False,
                'message': 'Justificación no encontrada'
            }), 404
        
        # Actualizar justificación
        justification.status = 'APROBADA'
        justification.reviewed_by = professor_id
        justification.review_date = datetime.utcnow()
        justification.admin_response = admin_response
        
        # Obtener estudiante
        student = db.session.query(Student).get(justification.student_id)
        
        # Registrar en audit_logs
        professor = db.session.query(Professor).get(professor_id)
        if professor and student:
            AuditLog.log_action(
                user_id=professor.id,
                user_type='PROFESSOR',
                action='APPROVE_JUSTIFICATION',
                table_name='justifications',
                record_id=justification_id,
                new_values=f'Aprobó justificación de {student.first_name} {student.last_name} - {justification.reason_type}',
                ip_address=request.remote_addr
            )
        
        db.session.commit()
        
        # Enviar email al estudiante
        try:
            from app.services.email_service import EmailService
            from app.models.course import Course
            course = db.session.query(Course).get(justification.course_id)
            EmailService.send_justification_processed(
                student, justification, course, admin_response, True
            )
        except Exception as email_error:
            print(f"⚠️ Error al enviar email: {email_error}")
        
        return jsonify({
            'success': True,
            'message': 'Justificación aprobada exitosamente',
            'data': justification.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@justification_professor_bp.route('/<int:justification_id>/reject', methods=['POST'])
def reject_justification(justification_id):
    """Rechazar una justificación"""
    try:
        data = request.get_json()
        professor_id = data.get('professor_id')
        admin_response = data.get('admin_response', '')
        
        if not admin_response:
            return jsonify({
                'success': False,
                'message': 'Debe proporcionar un motivo de rechazo'
            }), 400
        
        justification = db.session.query(Justification).get(justification_id)
        
        if not justification:
            return jsonify({
                'success': False,
                'message': 'Justificación no encontrada'
            }), 404
        
        # Actualizar justificación
        justification.status = 'RECHAZADA'
        justification.reviewed_by = professor_id
        justification.review_date = datetime.utcnow()
        justification.admin_response = admin_response
        
        # Registrar en audit_logs
        professor = db.session.query(Professor).get(professor_id)
        student = db.session.query(Student).get(justification.student_id)
        if professor and student:
            AuditLog.log_action(
                user_id=professor.id,
                user_type='PROFESSOR',
                action='REJECT_JUSTIFICATION',
                table_name='justifications',
                record_id=justification_id,
                new_values=f'Rechazó justificación de {student.first_name} {student.last_name} - {justification.reason_type}',
                ip_address=request.remote_addr
            )
        
        db.session.commit()
        
        # Enviar email al estudiante
        try:
            from app.services.email_service import EmailService
            from app.models.course import Course
            course = db.session.query(Course).get(justification.course_id)
            EmailService.send_justification_processed(
                student, justification, course, admin_response, False
            )
        except Exception as email_error:
            print(f"⚠️ Error al enviar email: {email_error}")
        
        return jsonify({
            'success': True,
            'message': 'Justificación rechazada',
            'data': justification.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@justification_professor_bp.route('/stats', methods=['GET'])
def get_justification_stats():
    """Obtener estadísticas de justificaciones"""
    try:
        total = db.session.query(Justification).count()
        pending = db.session.query(Justification).filter(
            Justification.status == 'PENDIENTE'
        ).count()
        approved = db.session.query(Justification).filter(
            Justification.status == 'APROBADA'
        ).count()
        rejected = db.session.query(Justification).filter(
            Justification.status == 'RECHAZADA'
        ).count()
        
        return jsonify({
            'success': True,
            'data': {
                'total': total,
                'pending': pending,
                'approved': approved,
                'rejected': rejected
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500
